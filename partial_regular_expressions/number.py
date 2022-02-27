#! /usr/bin/env python3

import re

# A valid JSON number token consists of an optional minus sign, followed by an unsigned integer, followed by an optional fractional part,
# followed by an optional exponential part.
#
re_number_pattern = '-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?'

re_number = re.compile(re_number_pattern)

testcases_good = [
    '-0', '-1', '-9', '-10', '-99', '-100', '-999',
    '0', '1', '9', '10', '99', '100', '999',
    '1.2',
    '0.1',
    '1e3',
    '1E3',
    '1e005',
    '1e+005',
    '1e-005',
    '1.7e005',
    '1.7e+005',
    '1.7e-005'
]

testcases_bad = [
    '',
    '-',
    '+',
    ' 123',  # No leading or trailing whitespace allowed.
    '123 ',  # No leading or trailing whitespace allowed.
    '01',    # A number may not start with a 0 digit, unless it's zero.
    '+0',    # Unary + not allowed.
    '+1',    # Unary + not allowed.
    '1,2',   # Only a period is allowed as a integer/fractional part separator.
    '0.',    # Bare period not allowed.
    '1.',    # Bare period not allowed.
    '1.E3',  # Bare period not allowed.
    'inf',   # JSON does not support IEEE-754 infinity.
    '+inf',  # JSON does not support IEEE-754 infinity.
    '-inf',  # JSON does not support IEEE-754 infinity.
    'nan',   # JSON does not support IEEE-754 NaNs.
    '+nan',  # JSON does not support IEEE-754 NaNs.
    '-nan'   # JSON does not support IEEE-754 NaNs.
]

for testcase in testcases_good:
    if not re_number.fullmatch(testcase):
        print("testcases_good failure; the following {}-character string was incorrectly rejected as a number token: {!r}".format(len(testcase), testcase))

for testcase in testcases_bad:
    if re_number.fullmatch(testcase):
        print("testcases_good failure; the following {}-character string was incorrectly accepted as a number token: {!r}".format(len(testcase), testcase))
