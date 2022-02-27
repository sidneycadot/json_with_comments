#! /usr/bin/env python3

import re

# A valid JSON whitespace token consists of zero or more whitespace characters.
#
# A whitespace character is either ...
#    - a single space
#    - a single linefeed ('\n').
#    - a single carriage return ('\r').
#    - a single horizontal tab ('\t').

re_whitespace_pattern = '[ \n\r\t]*'

re_whitespace = re.compile(re_whitespace_pattern)

testcases_good = [
    '',
    ' ',
    '\n',
    '\r',
    '\t',
    ' \n\r\t \n\r\t'
]

testcases_bad = [
    '\v',
    '\x00'
]

for testcase in testcases_good:
    if not re_whitespace.fullmatch(testcase):
        print("testcases_good failure; the following {}-character string was incorrectly rejected as a whitespace token: {!r}".format(len(testcase), testcase))

for testcase in testcases_bad:
    if re_whitespace.fullmatch(testcase):
        print("testcases_bad failure; the following {}-character string was incorrectly accepted as a whitespace token: {!r}".format(len(testcase), testcase))
