#!/usr/bin/env python3
"""Recount the statuses of the scenario table rows in a .md report.

Only counts table rows whose first column is a scenario number
(e.g. "| 1.2 | ... | 🔴 bug 1 |"), using the first status symbol found in the
last column. Prints the totals and the rows with no recognised status.

Usage: python count_status.py report.md
"""
import re
import sys

SYMBOLS = {
    '✅': 'Passed',
    '🔴': 'Failed',
    '🚫': 'Blocked',
    '➖': 'Not applicable',
    '⬜': 'Not tested',
}
SCENARIO_ROW = re.compile(r'^\|\s*\d+(\.\d+)+\s*\|')


def main(path: str) -> None:
    totals = {label: 0 for label in SYMBOLS.values()}
    without_status = []
    with open(path, encoding='utf-8') as report:
        for number, line in enumerate(report, 1):
            if not SCENARIO_ROW.match(line):
                continue
            last_column = line.strip().strip('|').split('|')[-1]
            found = next((s for s in SYMBOLS if s in last_column), None)
            if found is None:
                without_status.append((number, line.strip()[:100]))
                continue
            totals[SYMBOLS[found]] += 1
    for label, count in totals.items():
        if count:
            print(f'{label}: {count}')
    print(f'Total: {sum(totals.values())}')
    for number, text in without_status:
        print(f'NO STATUS line {number}: {text}')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
