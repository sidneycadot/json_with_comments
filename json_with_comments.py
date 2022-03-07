"""Support routines for the JSON-with-comments file format."""

import json
from enum import Enum


class CharacterClass(Enum):
    """Character classes for parsing JSON-with-comments."""
    FSLASH = 1  # forward slash
    BSLASH = 2  # back slash
    QUOTE  = 3  # string quote
    CR     = 4  # carriage return
    NL     = 5  # newline
    STAR   = 6  # star (asterisk)
    OTHER  = 7  # any other character


class FsmAction(Enum):
    """FSM actions for parsing JSON-with-comments."""
    EMIT_CURRENT             = 1
    EMIT_FSLASH_THEN_CURRENT = 2
    EMIT_NOTHING             = 3
    EMIT_ONE_SPACE           = 4
    EMIT_TWO_SPACES          = 5


class FsmState(Enum):
    """FSM states for parsing JSON-with-comments."""
    DEFAULT            = 1
    MAYBE_COMMENT      = 2
    LINE_COMMENT       = 3
    BLOCK_COMMENT      = 4
    BLOCK_COMMENT_STAR = 5
    STRING             = 6
    STRING_BACKSLASH   = 7


class JSONWithCommentsError(Exception):
    """An error occurred while processing JSON-with-comments."""


_fsm_definition = {

    (FsmState.DEFAULT , CharacterClass.FSLASH) : (FsmAction.EMIT_NOTHING , FsmState.MAYBE_COMMENT),
    (FsmState.DEFAULT , CharacterClass.QUOTE ) : (FsmAction.EMIT_CURRENT , FsmState.STRING       ),
    (FsmState.DEFAULT , CharacterClass.OTHER ) : (FsmAction.EMIT_CURRENT , FsmState.DEFAULT      ),

    (FsmState.MAYBE_COMMENT , CharacterClass.FSLASH) : (FsmAction.EMIT_TWO_SPACES          , FsmState.LINE_COMMENT ),
    (FsmState.MAYBE_COMMENT , CharacterClass.STAR  ) : (FsmAction.EMIT_TWO_SPACES          , FsmState.BLOCK_COMMENT),
    (FsmState.MAYBE_COMMENT , CharacterClass.OTHER ) : (FsmAction.EMIT_FSLASH_THEN_CURRENT , FsmState.DEFAULT      ),

    (FsmState.LINE_COMMENT , CharacterClass.CR   ) : (FsmAction.EMIT_CURRENT   , FsmState.LINE_COMMENT),
    (FsmState.LINE_COMMENT , CharacterClass.NL   ) : (FsmAction.EMIT_CURRENT   , FsmState.DEFAULT     ),
    (FsmState.LINE_COMMENT , CharacterClass.OTHER) : (FsmAction.EMIT_ONE_SPACE , FsmState.LINE_COMMENT),

    (FsmState.BLOCK_COMMENT , CharacterClass.CR   ) : (FsmAction.EMIT_CURRENT   , FsmState.BLOCK_COMMENT     ),
    (FsmState.BLOCK_COMMENT , CharacterClass.NL   ) : (FsmAction.EMIT_CURRENT   , FsmState.BLOCK_COMMENT     ),
    (FsmState.BLOCK_COMMENT , CharacterClass.STAR ) : (FsmAction.EMIT_ONE_SPACE , FsmState.BLOCK_COMMENT_STAR),
    (FsmState.BLOCK_COMMENT , CharacterClass.OTHER) : (FsmAction.EMIT_ONE_SPACE , FsmState.BLOCK_COMMENT     ),

    (FsmState.BLOCK_COMMENT_STAR , CharacterClass.FSLASH) : (FsmAction.EMIT_ONE_SPACE , FsmState.DEFAULT           ),
    (FsmState.BLOCK_COMMENT_STAR , CharacterClass.CR    ) : (FsmAction.EMIT_CURRENT   , FsmState.BLOCK_COMMENT     ),
    (FsmState.BLOCK_COMMENT_STAR , CharacterClass.NL    ) : (FsmAction.EMIT_CURRENT   , FsmState.BLOCK_COMMENT     ),
    (FsmState.BLOCK_COMMENT_STAR , CharacterClass.STAR  ) : (FsmAction.EMIT_ONE_SPACE , FsmState.BLOCK_COMMENT_STAR),
    (FsmState.BLOCK_COMMENT_STAR , CharacterClass.OTHER ) : (FsmAction.EMIT_ONE_SPACE , FsmState.BLOCK_COMMENT     ),

    (FsmState.STRING , CharacterClass.BSLASH) : (FsmAction.EMIT_CURRENT , FsmState.STRING_BACKSLASH),
    (FsmState.STRING , CharacterClass.QUOTE ) : (FsmAction.EMIT_CURRENT , FsmState.DEFAULT         ),
    (FsmState.STRING , CharacterClass.OTHER ) : (FsmAction.EMIT_CURRENT , FsmState.STRING          ),

    (FsmState.STRING_BACKSLASH , CharacterClass.OTHER) : (FsmAction.EMIT_CURRENT , FsmState.STRING)
}


_character_classifications = {
    '/'  : CharacterClass.FSLASH,
    '\\' : CharacterClass.BSLASH,
    '\"' : CharacterClass.QUOTE,
    '\r' : CharacterClass.CR,
    '\n' : CharacterClass.NL,
    '*'  : CharacterClass.STAR
}


def remove_comments_from_json_with_comments(input_string: str) -> str:
    """Go through a finite state machine to remove line and block comments from JSON-with-comments.

    Note: the comments are not actually removed; their contents are overwritten by spaces,
    except that carriage returns and line feeds inside comments are passed through as-is.

    The reason for doing this is that it preserves line and character numbering of the output
    relative to the input. If a JSON parser runs on our output and needs to report an issue,
    it can do so with line and character numbers that are meaningful.
    """

    output = []
    state = FsmState.DEFAULT
    for current_character in input_string:

        character_class = _character_classifications.get(current_character, CharacterClass.OTHER)

        # If a (state, character_class) tuple is not explicitly handled in the FSM definition,
        # the behavior of CharacterClass.OTHER will be applied, which is defined for all states.
        if (state, character_class) not in _fsm_definition:
            character_class = CharacterClass.OTHER

        (action, state) = _fsm_definition[(state, character_class)]

        # Perform the specified action.

        if action in (FsmAction.EMIT_CURRENT, FsmAction.EMIT_FSLASH_THEN_CURRENT):
            if action == FsmAction.EMIT_FSLASH_THEN_CURRENT:
                output.append("/")
            output.append(current_character)
        elif action in (FsmAction.EMIT_ONE_SPACE, FsmAction.EMIT_TWO_SPACES):
            if action == FsmAction.EMIT_TWO_SPACES:
                output.append(" ")
            output.append(" ")

    # We're at the end of the character processing loop.

    # The usual end state for a succesful FSM run should be DEFAULT.
    # We also accept LINE_COMMENT, i.e., line comments that are not terminated by a newline are accepted.
    #
    # If we're in one of the five other possible states at the end, it indicates some parsing issue.

    # The end states STRING and STRING_BACKSLASH indicate that the input ended while inside a string.
    # This issue remains in the output, and will be caught when a JSON parser runs on our output.

    # If we're in the MAYBE_COMMENT state, the input ended in a forward slash. This forward slash was not
    # emitted when we entered the MAYBE_COMMENT state, so we emit it now.
    # This will result in a JSON grammar error that will be caught when a JSON parser runs on our output.

    if state == FsmState.MAYBE_COMMENT:
        output.append("/")

    # The two remaining possible end states (BLOCK_COMMENT, BLOCK_COMMENT_STAR) indicate that the input
    # ended while parsing an unterminated block comment.
    # This issue will not be picked up by the JSON parser that runs on our output, so we handle it here:

    if state in (FsmState.BLOCK_COMMENT, FsmState.BLOCK_COMMENT_STAR):
        raise JSONWithCommentsError("Unterminated block comment at end of string.")

    # Concatenate the output characters and return the result.

    output_string = "".join(output)

    return output_string


def parse_json_with_comments(json_with_comments: str):
    """Parse JSON-with-comments by removing the comments and parsing the result as JSON."""
    json_without_comments = remove_comments_from_json_with_comments(json_with_comments)
    return json.loads(json_without_comments)


def read_json_with_comments(filename: str):
    """Read JSON-with-comments from file and parse it."""
    with open(filename, "r") as fi:
        json_with_comments = fi.read()
    try:
        return parse_json_with_comments(json_with_comments)
    except JSONWithCommentsError:
        raise JSONWithCommentsError("Unterminated block comment at end of file.")
