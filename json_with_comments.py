"""Routines to process JSON extended with comments."""

import json
from enum import Enum


class JSONWithCommentsError(ValueError):
    """An error occurred while processing JSON-with-comments."""


class FsmState(Enum):
    """Finite State Machine states for scanning JSON-with-comments."""
    DEFAULT            = 1  # default state ; not scanning a string or comment.
    COMMENT_INTRO      = 2  # accepted '/'  ; the start of a line or block comment.
    LINE_COMMENT       = 3  # accepted '//' ; scanning a line comment.
    BLOCK_COMMENT      = 4  # accepted '/*' ; scanning a block comment.
    BLOCK_COMMENT_STAR = 5  # accepted '/*' ; scanning a block comment, and just scanned a '*'.
    STRING             = 6  # accepted '"'  ; scanning a string.
    STRING_BACKSLASH   = 7  # accepted '"'  ; scanning a string, and just scanned a backslash.


class FsmAction(Enum):
    """Finite State Machine actions for scanning JSON-with-comments."""
    EMIT_NOTHING             = 1  # emit nothing
    EMIT_CURRENT             = 2  # emit the current character
    EMIT_FSLASH_THEN_CURRENT = 3  # emit forward slash followed by current character
    EMIT_ONE_SPACE           = 4  # emit one space character
    EMIT_TWO_SPACES          = 5  # emit two space characters


class CharacterClass(Enum):
    """Character classes to be distinguished while scanning JSON-with-comments."""
    FSLASH = 1  # forward slash
    BSLASH = 2  # back slash
    QUOTE  = 3  # string quote
    CR     = 4  # carriage return
    NL     = 5  # newline
    STAR   = 6  # star (asterisk)
    OTHER  = 7  # any other character


# Define the transition table of (state, character_class) -> (action, next_state).
#
# Note that not all possible combinations of (state, character_class) are explicitly specified.
# If a (state, character_class) combination is encountered while scanning that is not present
# in the transition table, the key (state, CharacterClass.OTHER) key will be used instead.
#
# This makes the transition table both smaller (only 22 out of 49 entries need to be specified)
# and easier to understand.

_fsm_definition = {

    ( FsmState.DEFAULT            , CharacterClass.FSLASH ) : ( FsmAction.EMIT_NOTHING             , FsmState.COMMENT_INTRO      ),
    ( FsmState.DEFAULT            , CharacterClass.QUOTE  ) : ( FsmAction.EMIT_CURRENT             , FsmState.STRING             ),
    ( FsmState.DEFAULT            , CharacterClass.OTHER  ) : ( FsmAction.EMIT_CURRENT             , FsmState.DEFAULT            ),

    ( FsmState.COMMENT_INTRO      , CharacterClass.FSLASH ) : ( FsmAction.EMIT_TWO_SPACES          , FsmState.LINE_COMMENT       ),
    ( FsmState.COMMENT_INTRO      , CharacterClass.STAR   ) : ( FsmAction.EMIT_TWO_SPACES          , FsmState.BLOCK_COMMENT      ),
    ( FsmState.COMMENT_INTRO      , CharacterClass.OTHER  ) : ( FsmAction.EMIT_FSLASH_THEN_CURRENT , FsmState.DEFAULT            ),

    ( FsmState.LINE_COMMENT       , CharacterClass.CR     ) : ( FsmAction.EMIT_CURRENT             , FsmState.LINE_COMMENT       ),
    ( FsmState.LINE_COMMENT       , CharacterClass.NL     ) : ( FsmAction.EMIT_CURRENT             , FsmState.DEFAULT            ),
    ( FsmState.LINE_COMMENT       , CharacterClass.OTHER  ) : ( FsmAction.EMIT_ONE_SPACE           , FsmState.LINE_COMMENT       ),

    ( FsmState.BLOCK_COMMENT      , CharacterClass.CR     ) : ( FsmAction.EMIT_CURRENT             , FsmState.BLOCK_COMMENT      ),
    ( FsmState.BLOCK_COMMENT      , CharacterClass.NL     ) : ( FsmAction.EMIT_CURRENT             , FsmState.BLOCK_COMMENT      ),
    ( FsmState.BLOCK_COMMENT      , CharacterClass.STAR   ) : ( FsmAction.EMIT_ONE_SPACE           , FsmState.BLOCK_COMMENT_STAR ),
    ( FsmState.BLOCK_COMMENT      , CharacterClass.OTHER  ) : ( FsmAction.EMIT_ONE_SPACE           , FsmState.BLOCK_COMMENT      ),

    ( FsmState.BLOCK_COMMENT_STAR , CharacterClass.FSLASH ) : ( FsmAction.EMIT_ONE_SPACE           , FsmState.DEFAULT            ),
    ( FsmState.BLOCK_COMMENT_STAR , CharacterClass.CR     ) : ( FsmAction.EMIT_CURRENT             , FsmState.BLOCK_COMMENT      ),
    ( FsmState.BLOCK_COMMENT_STAR , CharacterClass.NL     ) : ( FsmAction.EMIT_CURRENT             , FsmState.BLOCK_COMMENT      ),
    ( FsmState.BLOCK_COMMENT_STAR , CharacterClass.STAR   ) : ( FsmAction.EMIT_ONE_SPACE           , FsmState.BLOCK_COMMENT_STAR ),
    ( FsmState.BLOCK_COMMENT_STAR , CharacterClass.OTHER  ) : ( FsmAction.EMIT_ONE_SPACE           , FsmState.BLOCK_COMMENT      ),

    ( FsmState.STRING             , CharacterClass.BSLASH ) : ( FsmAction.EMIT_CURRENT             , FsmState.STRING_BACKSLASH   ),
    ( FsmState.STRING             , CharacterClass.QUOTE  ) : ( FsmAction.EMIT_CURRENT             , FsmState.DEFAULT            ),
    ( FsmState.STRING             , CharacterClass.OTHER  ) : ( FsmAction.EMIT_CURRENT             , FsmState.STRING             ),

    ( FsmState.STRING_BACKSLASH   , CharacterClass.OTHER  ) : ( FsmAction.EMIT_CURRENT             , FsmState.STRING             )
}

# Characters are classified according to this table.
# All characters that are not explicitly specified belong to CharacterClass.OTHER.

_character_classifications = {
    '/'  : CharacterClass.FSLASH,
    '\\' : CharacterClass.BSLASH,
    '\"' : CharacterClass.QUOTE,
    '\r' : CharacterClass.CR,
    '\n' : CharacterClass.NL,
    '*'  : CharacterClass.STAR
}


def replace_json_comments_by_whitespace(input_string: str) -> str:
    """Replace the comments in JSON-with-comments by whitespace, yielding valid JSON.

    All characters in a comment are replaced by spaces, except carriage return and
    newline characters that are passed through as-is.

    This preserves line and character numbering of the output relative to the input.
    If a JSON parser runs on our output and needs to report an issue, it can do so
    with line and character numbers that are meaningful.
    """

    output = []

    state = FsmState.DEFAULT

    for current_character in input_string:

        character_class = _character_classifications.get(current_character, CharacterClass.OTHER)

        # If a (state, character_class) tuple is not explicitly handled in the FSM definition,
        # the behavior of CharacterClass.OTHER will be applied, which is defined for all states.

        if (state, character_class) not in _fsm_definition:
            character_class = CharacterClass.OTHER

        # Look up action and next state.

        (action, next_state) = _fsm_definition[(state, character_class)]

        # Perform the specified action.

        if action in (FsmAction.EMIT_CURRENT, FsmAction.EMIT_FSLASH_THEN_CURRENT):
            if action == FsmAction.EMIT_FSLASH_THEN_CURRENT:
                output.append("/")
            output.append(current_character)
        elif action in (FsmAction.EMIT_ONE_SPACE, FsmAction.EMIT_TWO_SPACES):
            if action == FsmAction.EMIT_TWO_SPACES:
                output.append(" ")
            output.append(" ")

        # Proceed to the next state.

        state = next_state

    # We're at the end of the character scan loop.

    # The usual end state for a successful scan should be DEFAULT. We also accept LINE_COMMENT,
    # meaning that line comments that are not terminated by a newline are acceptable.
    #
    # If we're in one of the five other states at the end of the scan, something is wrong!
    #
    # The end states STRING and STRING_BACKSLASH indicate that the input ended while inside a string.
    # This issue remains in the output, and will be caught when a JSON parser processes our output.
    #
    # The three remaining erroneous states need action from our side:

    if state == FsmState.COMMENT_INTRO:
        # If we're in the COMMENT_INTRO state, the input ended in a forward slash. This forward
        # slash was not yet emitted when we entered the COMMENT_INTRO state, so we emit it now.
        # Since no valid JSON file can end with a forward slash, this will be caught when a#
        # JSON parser processes our output.
        output.append("/")
    elif state in (FsmState.BLOCK_COMMENT, FsmState.BLOCK_COMMENT_STAR):
        # The end states BLOCK_COMMENT and BLOCK_COMMENT_STAR indicate that the input ended while
        # scanning an unterminated block comment. This issue would not be noticed by a JSON parser
        # that processes our output, as our output will just end with the spaces that replaced
        # the partial block comment. So for both these end states, we will raise an exception.
        raise JSONWithCommentsError("Unterminated block comment.")

    # Concatenate the output characters and return the result.

    output_string = "".join(output)

    return output_string


def parse_json_with_comments(json_with_comments: str):
    """Parse JSON-with-comments by removing the comments and parsing the result as JSON."""
    json_without_comments = replace_json_comments_by_whitespace(json_with_comments)
    try:
        return json.loads(json_without_comments)
    except json.JSONDecodeError as json_exception:
        # Wrap the JSONDecodeError in a JSONWithCommentsError exception.
        raise JSONWithCommentsError("Comment removal did not yield valid JSON.") from json_exception


def read_json_with_comments(filename: str):
    """Read JSON-with-comments from file and parse it."""
    with open(filename, "r") as f:
        json_with_comments = f.read()
    return parse_json_with_comments(json_with_comments)
