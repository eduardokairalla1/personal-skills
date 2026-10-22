# Driving the front end

## The user's Chrome (Claude in Chrome)

- The Chrome tools only exist if the Claude Code session was **started** with the integration. If `/chrome` shows nothing and the `mcp__claude-in-chrome__*` tools do not exist, ask the user to quit and come back with `claude --chrome --resume` (keeps the conversation) and run `/chrome` again. Requirements: login through `/login` (not an API key), extension installed and Chrome restarted once after installing it.
- The tools arrive deferred: load the whole set in a single call (`ToolSearch select:...tabs_context_mcp,navigate,computer,read_page,find,form_input,get_page_text,javascript_tool,read_console_messages,read_network_requests,browser_batch,file_upload`).
- Prefer `browser_batch` for predictable sequences (click, type, wait, capture) — it is much faster.
- Use the user's browser only as agreed. To switch users in it (e.g. supervisor → operator), say so before clicking "Log out".

## Headless browser (Playwright)

Use it for parallel users (a second operator, the supervisor) and to avoid touching the user's window.

```python
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=['--ignore-certificate-errors'])
    ctx = b.new_context(ignore_https_errors=True, locale='pt-BR', viewport={'width': 1568, 'height': 765})
    pg = ctx.new_page()
    try:
        ...  # login, steps
    finally:
        ...  # log out through the menu, confirm
        b.close()
```

- **Locale**: without `locale`, headless opens in English and placeholders change. Set the product's locale or select by type (`input[type=password]`).
- **Selectors**: `get_by_text("Login")` also matches "Login as supervisor" and fails in strict mode; use `get_by_role('button', name='Login', exact=True)`.
- **Background session**: to keep a user online while you drive another one, run the script with `nohup`, periodically writing the screen state (card texts as JSON Lines + a screenshot) to a file you read.
- **Always log out**, in `finally`. A session that dies without logging out stays "online" on the server and receives work (e.g. conversations scheduled to it for tens of seconds). If it happened, log that user in again and log out through the menu.
- A tooltip intercepting the menu click: move the mouse away and use `click(force=True)`.

## Finding and clicking

- `find` with a natural-language description returns a `ref`; clicking by `ref` is more stable than by coordinates.
- Coordinates of a scaled screenshot are in the coordinate frame reported by the tool, not in the image pixels.
- `getBoundingClientRect()` via JS is in CSS pixels of the viewport, which may have a different scale than the screenshot frame. Convert, or click via JS.
- Element off screen (sliding panel, negative `x`) or covered: `element.click()` via `javascript_tool`.
- Virtualised lists: read the content through JS (`document.querySelectorAll('article')` or equivalent) instead of trusting what is visible in the screenshot.
- Screens with one tab per channel/account: hover and read the tooltip to confirm which tab you are on before acting.

## Tricky fields

- **Phone mask** with a fixed prefix (`+5`): selecting all and typing the whole number duplicates the prefix. Delete (repeated Backspace), check what is left and type only the rest.
- **Date and time picker**: future dates come disabled; pick the day in the grid and scroll the time list to the wanted time. Check the final value in the input before applying.
- **Confirmation modal**: after clicking, wait for the modal to close before the next click; clicks that come too fast land on the overlay and do nothing.

## Verifying without side effects

- **Copy to clipboard** with an unfocused window writes nothing. Intercept it in the page and read the argument:
  ```js
  window.__copied=[]; navigator.clipboard.writeText = async t => { window.__copied.push(t) };
  ```
- **Exports/downloads** (CSV etc.): downloading a file needs permission. Read the generated content without saving it:
  ```js
  URL.createObjectURL = b => { b.text().then(t => window.__csv = t); return 'about:blank' };
  HTMLAnchorElement.prototype.click = function(){ window.__dl = this.download };
  ```
  Click Export and read `window.__csv`. PDFs and real downloads are left for the user.
- **Calling the API with the user's session** (to produce a state the screen cannot, e.g. a message type only a bot sends): capture the auth headers from one of the front end's own requests by intercepting `fetch`, and use them in the same page context. Never print or copy the token outside the page.

## Network and console

- `read_network_requests` only records after its first call; call it once to start recording and repeat the action.
- Generic error on screen ("Failed to load"): capture the network response (headless: `page.on('response', ...)`) and read the backend error before concluding it is the change.
