#! /usr/bin/env -S python3 -B

"""A small example showing how to use JSON-with-comments."""

from json_with_comments_fsm import parse_json_with_comments

stress_test = """// This is a small test to see if comment removal works as it should.
{
   "key"     : "value", // end-of-line comment...
   "hello"   : [ true, false, null, 1.0, "ciao" ],
   "strings" : ["", "Mötorhead", "/", "\\\\", "\\/", "\\\"", "🎈", "\\u2665" ],
   "numbers" : [0, -0, 0e0 ]
}

/* A block comment.

tralala

*/

"""

stress_test_dict = parse_json_with_comments(stress_test)

print(stress_test_dict)
