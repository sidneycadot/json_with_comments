"""This module implements support for JSON-with-comments.

JSON tokens fall into one of the following five categories:

(J.1) Single-character tokens. There are six of these: '{', '}', ',', ':', '[', and ']'.
(J.2) Reserved word tokens. There are three of these: 'true', 'false', and 'null'.
(J.3) String tokens. These start and end with a quotation mark (0x22), with string characters in between.

      JSON allows the following three types of string characters:

      (3a) single characters in the Unicode range (0x0020 .. 0x10ffff), with the exception of the quotation mark (0x22) and backslash (0x5c).
      (3b) a backslash character (0x5c) followed by one of the following eight characters: 'b', 'f', 'n', 'r', 't', '"', backslash (0x5c), and '/'.
      (3c) a Unicode escape sequence, consisting of a backslash and 'u' followed by precisely four case-insensitive hexadecimal digits, e.g. \u0041.

      Note that the forward slash (0x3f) can be written either directly or with a preceding backslash in a JSON string.

(J.4) Number tokens, consisting of up to four parts:

      (4a) optionally: a preceding '-' sign. (A preceding '+' sign is not allowed.)
      (4b) an unsigned integer part consisting of decimal digits. Leading zeros are not allowed, except if the value zero itself must be represented.
      (4c) optionally: a period (.) followed by a nonempty sequence of decimal digits. This is the fractional part of the mantissa.
      (4d) optionally: a character 'e' or 'E', followed by an optional minus or plus sign, followed by a nonempty sequence of decimal digits. This is the exponent.

(J.5) Whitespace, consisting of a sequence of {space, newline, carriage return, horizontal tab} characters.

      Note that the JSON grammar allows empty whitespace tokens, simplifying its grammar. We will not allow empty whitespace tokens.

In addition to these five tokens defined by JSON, our JSON-with-comments format supports two more tokens that represent comments:

(JWC.1) A line comment, starting with the characters '//' and reaching up to (but not including) the next newline character.
(JWC.2) A block comment, starting with the two characters '/*' and ending with the first occurrence of the two characters '*/'.
"""

import re
import json

def remove_comments_from_json_with_comments(json_with_comments: str) -> str:
    """Takes a string input consisting of JSON-with-comments and strips out the comments.

    The strategy here is to chop up the string in valid JSON-with-comment tokens,
    remove the comment tokens, then re-assemble the remaining tokens.
    """

    json_with_comments_token = "|".join((
        '[{},:[\\]]',                                                        # the six single-character tokens;
        'true|false|null',                                                   # the three keyword tokens;
        '"(?:[^\\x00-\\x1f"\\\\]|\\\\(?:[bfnrt"\\\\/]|u[0-9A-Fa-f]{4}))*"',  # a string token;
        '-?(?:0|[1-9][0-9]*)(?:\\.[0-9]+)?(?:[eE][+-]?[0-9]+)?',             # a number token;
        '[ \n\r\t]+',                                                        # a whitespace token (note that we don't recognize the zero-length whitespace token);
        '//.*',                                                              # a // comment, running to end-of-line;
        '/\\*(?:.|\\n)*?\\*/'                                                # a /* ... */ block comment. This uses non-greedy matching up to the first '*/'.
    ))

    tokens = re.findall(json_with_comments_token, json_with_comments)

    # The re.findall() function just skips over stuff it doesn't recognize.
    # Let's make sure that didn't happen.

    concatenated_tokens = "".join(tokens)

    if concatenated_tokens != json_with_comments:
        # Concatenating the tokens does not yield the original input string.
        raise ValueError("The string is not valid JSON-with-comments.")

    # Concatenate all tokens except the comment tokens.

    return "".join(token for token in tokens if not token.startswith("/"))


def parse_json_with_comments(json_with_comments: str):
    """Parse JSON-with-comments by removing the comments."""
    json_without_comments = remove_comments_from_json_with_comments(json_with_comments)
    return json.loads(json_without_comments)


def read_json_with_comments(filename: str):
    """Read JSON-with-comments from file."""
    with open(filename, "r") as fi:
        json_with_comments = fi.read()
    return parse_json_with_comments(json_with_comments)
