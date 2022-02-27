#! /usr/bin/env python3

import re

# A valid JSON string token consists of a quotation mark, followed by zero or more string characters, followed by a quotation mark.
#
# A string character is either ...
#    - a single character (Unicode 0x0020 .. 0x10ffff, except '"' (0x22) and '\' (0x5c));
#    - a backslash followed by any of the characters {'"', '\', or '/', 'b', 'f', 'n', 'r', 't'};
#    - a backslash followed by a character 'u' and precisely four hex digits ([0-9A-Fa-f]).
#
re_string_pattern = '"(?:[^\\x00-\\x1f"\\\]|\\\(?:[bfnrt"\\\/]|u[0-9A-Fa-f]{4}))*"'

print(len(re_string_pattern), repr(re_string_pattern))

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
    '"slash may be written directly as / or with a preceding backslash as \\/."',
    '"backslash may be written with a preceding backslash as \\\\."',
    '"\\udead"',
    '"\\udeadb"',
    '"\\udeadbe"',
    '"\\udeadbee"',
    '"\\udeadbeef"'
]

testcases_bad = [
    '',
    'hoi',
    '"',
    '"hallo',
    'hallo"',
    '"""',
    '"\a"',
    '"\b"',
    '"\c"',
    '"\d"',
    '"\e"',
    '"\f"',
    '"\g"',
    '"\h"',
    '"\i"',
    '"\j"',
    '"\k"',
    '"\l"',
    '"\m"',
    '"\n"',
    '"\o"',
    '"\p"',
    '"\q"',
    '"\r"',
    '"\s"',
    '"\t"',
    '"\v"',
    '"\w"',
    '"\y"',
    '"\z"',
    '"\\"',
    '"\\a"', '"\\c"', '"\\d"', '"\\e"', '"\\g"', '"\\h"', '"\\i"',
    '"\\j"', '"\\k"', '"\\l"', '"\\m"', '"\\o"', '"\\p"', '"\\q"',
    '"\\s"', '"\\u"', '"\\v"', '"\\w"', '"\\x"', '"\\y"', '"\\z"',
    '"backslash may not be directly written as \\.',
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
