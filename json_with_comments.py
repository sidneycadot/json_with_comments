"""This module removes #-style comments from JSON-with-comments, yielding a compliant JSON string."""

import re

def remove_comments_from_json_with_comments(json_with_comments: str) -> str:
    """Takes a string input consisting of JSON-with-comments and strips out the comments."""

    json_with_comments_token = "|".join((
        '[{},:[\\]]',                                                        # the six single-character tokens;
        'true|false|null',                                                   # the three keyword tokens;
        '"(?:[^\\x00-\\x1f"\\\\]|\\\\(?:[bfnrt"\\\\/]|u[0-9A-Fa-f]{4}))*"',  # a string token;
        '-?(?:0|[1-9][0-9]*)(?:\\.[0-9]+)?(?:[eE][+-]?[0-9]+)?',             # a number token;
        '[ \n\r\t]+',                                                        # a non-empty whitespace token;
        '//.*',                                                              # a // comment, running to end-of-line;
        '/\\*(?:.|\\n)*?\\*/'                                                # a /* ... */ block comment.
    ))

    tokens = re.findall(json_with_comments_token, json_with_comments)

    # The re.findall() function just skips over stuff it doesn't recognize.
    # Let's make sure that didn't happen.

    concatenated_tokens = "".join(tokens)

    if concatenated_tokens != json_with_comments:
        # Concatenating the tokens does not yield the original input string.
        raise ValueError("The file is neither valid JSON or JSON-with-comments.")

    # Concatenate all tokens except the comment tokens.

    return "".join(token for token in tokens if not token.startswith("#"))


def parse_json_with_comments(json_with_comments: str):
    """Parse JSON-with-comments by removing the comments."""
    json_without_comments = remove_comments_from_json_with_comments(json_with_comments)
    return json.loads(json_without_comments)


def read_json_with_comments(filename: str):
    """Read JSON-with-comments from file."""
    with open(filename, "r") as fi:
        json_with_comments = fi.read()
    return parse_json_with_comments(json_with_comments)
