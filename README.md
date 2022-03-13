# json_with_comments

This module provides functions to parse JSON-with-comments.

Standard JSON is a human-readable data interchange format that is popular due to its simplicity
and wide support across programming languages. Unfortunately, it does not support comments,
making it less suitable for some applications like configuration files.

This module implements several functions that add support for comments to JSON, resulting in a
JSON dialect that we refer to as "JSON-with-comments"; elsewhere, this format has been referred
to as "jsonc".

Two types of comments are supported, mirroring the two types of comments available in the
JavaScript language from which JSON originates:

* Line comments start with "//" and continue to the next newline character;
* Block comments start with "/*" and end with the next "*/".

The core functionality of this module is provided by the erase_json_comments() function. It
takes an input string argument, replaces comments with whitespace, and returns an output string
that is 'pure' JSON. Inside comments, carriage returns and newlines are passed through as-is;
all other characters are replaced by spaces. This preserves the structure of the original input,
allowing a subsequently run JSON parser to report any issues in the output with line numbers and
column offsets that correspond to the original JSON-with-comments input.

Two convenience functions are provided that run erase_json_comments() on input, then pass the
resulting 'purified' JSON-string to the JSON parser that is provided by the 'json' module in the
Python standard library. For most programs, one of these two functions will provide the easiest
way to use JSON-with-comments:

* parse_json_with_comments_string() parses JSON-with comments from a string;
* parse_json_with_comments_file() parses JSON-with comments from a file.
