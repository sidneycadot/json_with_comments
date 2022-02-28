#! /usr/bin/env python3

import re

# A valid JSON string token consists of a quotation mark, followed by zero or more string characters, followed by a quotation mark.
#
# A string character is either ...
#    - a single character (Unicode 0x0020 .. 0x10ffff, except '"' (0x22) and '\' (0x5c));
#    - a backslash followed by any of the characters {'"', '\', or '/', 'b', 'f', 'n', 'r', 't'};
#    - a backslash followed by a character 'u' and precisely four hex digits ([0-9A-Fa-f]).
#
re_string_pattern = '"(?:[^\\x00-\\x1f"\\\\]|\\\\(?:[bfnrt"\\\\/]|u[0-9A-Fa-f]{4}))*"'

re_string = re.compile(re_string_pattern)

testcases_good = [
    '""',
    '"hi"',
    '"Mötorhead"',
    '"\\\\"',
    '"\\/"',
    '"\\""',
    '"\\b"',
    '"\\f"',
    '"\\n"',
    '"\\r"',
    '"\\t"',
    '"/"',
    '"forward slash: / or  \\/."',
    '"backslash: \\\\."',
    '"\\udead"',
    '"\\udeadb"',
    '"\\udeadbe"',
    '"\\udeadbee"',
    '"\\udeadbeef"'
]

testcases_bad = [
    '',
    'hello',
    '"',
    '"hello',
    'hello"',
    '"""',
    '"\x00"', '"\x01"', '"\x02"', '"\x03"', '"\x04"', '"\x05"', '"\x06"', '"\x07"',
    '"\x08"', '"\x09"', '"\x0a"', '"\x0b"', '"\x0c"', '"\x0d"', '"\x0e"', '"\x0f"',
    '"\x10"', '"\x11"', '"\x12"', '"\x13"', '"\x14"', '"\x15"', '"\x16"', '"\x17"',
    '"\x18"', '"\x19"', '"\x1a"', '"\x1b"', '"\x1c"', '"\x1d"', '"\x1e"', '"\x1f"',
    '"\\"',
    '"\\a"', '"\\c"', '"\\d"', '"\\e"', '"\\g"', '"\\h"', '"\\i"',
    '"\\j"', '"\\k"', '"\\l"', '"\\m"', '"\\o"', '"\\p"', '"\\q"',
    '"\\s"', '"\\u"', '"\\v"', '"\\w"', '"\\x"', '"\\y"', '"\\z"',
    '"backslash: not just \\.',
    '"\\u"',
    '"\\ud"',
    '"\\ude"',
    '"\\udea"'
]

for testcase in testcases_good:
    if not re_string.fullmatch(testcase):
        print("testcases_good failure; the following {}-character string was incorrectly rejected as a string token: {!r}".format(len(testcase), testcase))

for testcase in testcases_bad:
    if re_string.fullmatch(testcase):
        print("testcases_bad failure; the following {}-character string was incorrectly accepted as a string token: {!r}".format(len(testcase), testcase))
