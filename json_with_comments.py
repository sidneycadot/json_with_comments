"""This module removes #-style comments from JSON-with-comments, yielding a compliant JSON string."""

import re

_json_with_comments_token = re.compile("|".join([
    '[{},:[\]]'         ,                                             # the six single-character tokens;
    'true|false|null'   ,                                             # the three keyword tokens;
    '"(?:[^\\x00-\\x1f"\\\]|\\\(?:[bfnrt"\\\/]|u[0-9A-Fa-f]{4}))*"',  # a string token;
    '-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?',           # a number token;
    '[ \n\r\t]*',                                                     # a whitespace token;
    '#.*'                                                             # a comment token ('#' up to and including end-of-line).
])

def remove_comments_from_json_with_comments(json_with_comments: str) -> str:
    """This function takes a string input consisting of JSON with optional comments
    and strips out the comments.
    """

    tokens = re.findall(_json_with_comments_token, json_with_comments)

    # The re.findall() function just skips over stuff it doesn't recognize.
    # Let's make sure that didn't happen.

    concatenated_tokens = "".join(tokens)

    if concatenated_tokens != json_with_comments:
        # Concatenating the tokens does not yield the original input string.
        raise ValueError("The file is neither valid JSON or JSON-with-comments.")

    # Concatenate all tokens except the 

    return "".join(token for token in tokens if not token.startswith("#"))
