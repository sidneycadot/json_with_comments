#! /usr/bin/env -S python3 -B

"""A small example showing how to use the 'remove_comments_from_json_with_comments' function."""

from json_with_comments import remove_comments_from_json_with_comments
import json

stress_test = """# This is a small test to see if comment removal works as it should.
{
   "key"     : "value", # end-of-line comment...
   "hello"   : [ true, false, null, 1.0, "ciao" ],
   "strings" : ["", "Mötorhead", "/", "\\\\", "\\/", "\\\"", "🎈", "\\u2665" ],
   "numbers" : [0, -0, 0e0 ]
}

# bye!
"""

print(stress_test)

stress_test_json = remove_comments_from_json_with_comments(stress_test)

stress_test_dict = json.loads(stress_test_json)

print(stress_test_dict)
