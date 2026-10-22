#!/usr/bin/env python3
"""Recording HTTP proxy for end-to-end reviews (stdlib only, Python 3.6+).

Sits between the service under test and an external API:
  - records every request as JSON Lines (method, path, body, response);
  - for routes configured as stubs, answers without forwarding;
  - forwards everything else to the real upstream (with the auth headers);
  - optionally, after a stub, fires a callback (e.g. a status webhook) built
    from the request, with fields overridden by a control file.

JSON configuration (--config):
{
  "upstream": "https://api.example.com",
  "log": "/tmp/proxy.log",
  "stubs": [
    {"method": "POST", "path_regex": "/messages$",
     "status": 200,
     "response": {"messages": [{"id": "{id}"}]},
     "callback": {"url": "http://service:4008/webhook", "delay": 1,
                  "body": {"statuses": [{"id": "{id}", "status": "sent"}]}}}
  ],
  "control_file": "/tmp/proxy.ctrl"
}

{id} is replaced by an id generated per request. If the control file exists when
a stub is hit, it is read once and deleted. Accepted content:
  {"fail": {"status": 400, "response": {...}}}   -> the stub answers this error
  {"skip_callback": true}                          -> the callback is not fired
  {"callback_set": {"field": value, ...}}          -> overrides fields of the first
                                                     object inside a list in the
                                                     callback body (null removes it)

Usage: nohup python3 recording_proxy.py --config cfg.json --port 8999 & echo $! > /tmp/proxy.pid
"""
import argparse
import json
import os
import re
import ssl
import threading
import time
import urllib.error
import urllib.request
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn

CONFIG = {}


def log(entry):
    entry['t'] = time.strftime('%H:%M:%S')
    with open(CONFIG.get('log', '/tmp/proxy.log'), 'a') as log_file:
        log_file.write(json.dumps(entry, ensure_ascii=False) + '\n')


def fill_id(obj, request_id):
    return json.loads(json.dumps(obj).replace('{id}', request_id))


def read_control():
    path = CONFIG.get('control_file')
    if not path or not os.path.exists(path):
        return {}
    try:
        with open(path) as control:
            return json.load(control)
    finally:
        os.remove(path)


def first_list_item(body):
    """First dict inside the first list found (target for field overrides)."""
    if isinstance(body, dict):
        for value in body.values():
            if isinstance(value, list) and value and isinstance(value[0], dict):
                return value[0]
            found = first_list_item(value)
            if found is not None:
                return found
    if isinstance(body, list):
        for value in body:
            found = first_list_item(value)
            if found is not None:
                return found
    return None


def fire_callback(callback, request_id, control):
    if control.get('skip_callback'):
        log({'kind': 'CALLBACK-SKIP', 'id': request_id})
        return
    body = fill_id(callback['body'], request_id)
    target = first_list_item(body)
    for key, value in control.get('callback_set', {}).items():
        if target is None:
            break
        if value is None:
            target.pop(key, None)
        else:
            target[key] = value
    time.sleep(callback.get('delay', 1))
    request = urllib.request.Request(callback['url'], data=json.dumps(body).encode(),
                                     headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            code = response.status
    except urllib.error.HTTPError as error:
        code = error.code
    except Exception as error:  # noqa: BLE001 - record any callback failure
        code = str(error)
    log({'kind': 'CALLBACK', 'body': body, 'code': code})


class Handler(BaseHTTPRequestHandler):
    def _read_body(self):
        length = int(self.headers.get('Content-Length') or 0)
        return self.rfile.read(length) if length else b''

    def _reply(self, code, body, content_type='application/json'):
        self.send_response(code)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _forward(self, raw):
        request = urllib.request.Request(CONFIG['upstream'] + self.path, data=raw or None,
                                         method=self.command)
        for header in ('Authorization', 'Content-Type', 'apikey'):
            if self.headers.get(header):
                request.add_header(header, self.headers.get(header))
        try:
            with urllib.request.urlopen(request, timeout=30,
                                        context=ssl.create_default_context()) as response:
                return response.status, response.read(), response.headers.get(
                    'Content-Type', 'application/json')
        except urllib.error.HTTPError as error:
            return error.code, error.read(), 'application/json'
        except (urllib.error.URLError, OSError) as error:
            # upstream unreachable: answer 502 instead of dropping the connection
            return 502, json.dumps({'proxy_error': str(error)}).encode(), \
                'application/json'

    def _handle(self):
        raw = self._read_body()
        try:
            body = json.loads(raw.decode() or 'null')
        except Exception:  # noqa: BLE001 - non-JSON body (form, binary)
            body = raw[:800].decode(errors='replace')
        for stub in CONFIG.get('stubs', []):
            if stub.get('method', self.command) == self.command and \
                    re.search(stub['path_regex'], self.path):
                request_id = 'mock.' + uuid.uuid4().hex
                control = read_control()
                if 'fail' in control:
                    failure = control['fail']
                    log({'kind': 'STUB-FAIL', 'path': self.path, 'body': body})
                    return self._reply(failure.get('status', 400),
                                       json.dumps(failure.get('response', {})).encode())
                log({'kind': 'STUB', 'path': self.path, 'body': body, 'id': request_id})
                if stub.get('callback'):
                    threading.Thread(target=fire_callback,
                                     args=(stub['callback'], request_id, control),
                                     daemon=True).start()
                response = fill_id(stub.get('response', {}), request_id)
                return self._reply(stub.get('status', 200), json.dumps(response).encode())
        code, response_body, content_type = self._forward(raw)
        log({'kind': 'PROXY', 'method': self.command, 'path': self.path.split('?')[0],
             'body': body, 'code': code,
             'resp': response_body[:300].decode(errors='replace')})
        return self._reply(code, response_body, content_type)

    do_GET = do_POST = do_PUT = do_PATCH = do_DELETE = _handle

    def log_message(self, *args):
        pass


class Server(ThreadingMixIn, HTTPServer):
    daemon_threads = True


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    parser.add_argument('--port', type=int, default=8999)
    args = parser.parse_args()
    with open(args.config) as config_file:
        CONFIG.update(json.load(config_file))
    Server(('0.0.0.0', args.port), Handler).serve_forever()
