"""Remove comments from JSON-with-comments."""

import json
from enum import Enum

class CharacterClass(Enum):
    FSLASH = 1
    BSLASH = 2
    QUOTE  = 3
    CR     = 4
    NL     = 5
    STAR   = 6
    OTHER  = 7

class FsmAction(Enum):
    EMIT_NOTHING = 1
    EMIT_CURRENT = 2
    EMIT_FSLASH_THEN_CURRENT = 3

class FsmState(Enum):
    START              = 1
    MAYBE_COMMENT      = 2
    LINE_COMMENT       = 3
    BLOCK_COMMENT      = 4
    BLOCK_COMMENT_STAR = 5
    STRING             = 6
    STRING_BACKSLASH   = 7

fsm_definition = {

    (FsmState.START , CharacterClass.FSLASH) : (FsmAction.EMIT_NOTHING , FsmState.MAYBE_COMMENT),
    (FsmState.START , CharacterClass.BSLASH) : (FsmAction.EMIT_CURRENT , FsmState.START        ),
    (FsmState.START , CharacterClass.QUOTE ) : (FsmAction.EMIT_CURRENT , FsmState.STRING       ),
    (FsmState.START , CharacterClass.CR    ) : (FsmAction.EMIT_CURRENT , FsmState.START        ),
    (FsmState.START , CharacterClass.NL    ) : (FsmAction.EMIT_CURRENT , FsmState.START        ),
    (FsmState.START , CharacterClass.STAR  ) : (FsmAction.EMIT_CURRENT , FsmState.START        ),
    (FsmState.START , CharacterClass.OTHER ) : (FsmAction.EMIT_CURRENT , FsmState.START        ),

    (FsmState.MAYBE_COMMENT, CharacterClass.FSLASH) : (FsmAction.EMIT_NOTHING             , FsmState.LINE_COMMENT ),
    (FsmState.MAYBE_COMMENT, CharacterClass.BSLASH) : (FsmAction.EMIT_FSLASH_THEN_CURRENT , FsmState.START        ),
    (FsmState.MAYBE_COMMENT, CharacterClass.QUOTE ) : (FsmAction.EMIT_FSLASH_THEN_CURRENT , FsmState.START        ),
    (FsmState.MAYBE_COMMENT, CharacterClass.CR    ) : (FsmAction.EMIT_FSLASH_THEN_CURRENT , FsmState.START        ),
    (FsmState.MAYBE_COMMENT, CharacterClass.NL    ) : (FsmAction.EMIT_FSLASH_THEN_CURRENT , FsmState.START        ),
    (FsmState.MAYBE_COMMENT, CharacterClass.STAR  ) : (FsmAction.EMIT_NOTHING             , FsmState.BLOCK_COMMENT),
    (FsmState.MAYBE_COMMENT, CharacterClass.OTHER ) : (FsmAction.EMIT_FSLASH_THEN_CURRENT , FsmState.START        ),

    (FsmState.LINE_COMMENT, CharacterClass.FSLASH) : (FsmAction.EMIT_NOTHING , FsmState.LINE_COMMENT ),
    (FsmState.LINE_COMMENT, CharacterClass.BSLASH) : (FsmAction.EMIT_NOTHING , FsmState.LINE_COMMENT ),
    (FsmState.LINE_COMMENT, CharacterClass.QUOTE ) : (FsmAction.EMIT_NOTHING , FsmState.LINE_COMMENT ),
    (FsmState.LINE_COMMENT, CharacterClass.CR    ) : (FsmAction.EMIT_CURRENT , FsmState.LINE_COMMENT ),
    (FsmState.LINE_COMMENT, CharacterClass.NL    ) : (FsmAction.EMIT_CURRENT , FsmState.START        ),
    (FsmState.LINE_COMMENT, CharacterClass.STAR  ) : (FsmAction.EMIT_NOTHING , FsmState.LINE_COMMENT ),
    (FsmState.LINE_COMMENT, CharacterClass.OTHER ) : (FsmAction.EMIT_NOTHING , FsmState.LINE_COMMENT ),

    (FsmState.BLOCK_COMMENT, CharacterClass.FSLASH) : (FsmAction.EMIT_NOTHING , FsmState.BLOCK_COMMENT      ),
    (FsmState.BLOCK_COMMENT, CharacterClass.BSLASH) : (FsmAction.EMIT_NOTHING , FsmState.BLOCK_COMMENT      ),
    (FsmState.BLOCK_COMMENT, CharacterClass.QUOTE ) : (FsmAction.EMIT_NOTHING , FsmState.BLOCK_COMMENT      ),
    (FsmState.BLOCK_COMMENT, CharacterClass.CR    ) : (FsmAction.EMIT_CURRENT , FsmState.BLOCK_COMMENT      ),
    (FsmState.BLOCK_COMMENT, CharacterClass.NL    ) : (FsmAction.EMIT_CURRENT , FsmState.BLOCK_COMMENT      ),
    (FsmState.BLOCK_COMMENT, CharacterClass.STAR  ) : (FsmAction.EMIT_NOTHING , FsmState.BLOCK_COMMENT_STAR ),
    (FsmState.BLOCK_COMMENT, CharacterClass.OTHER ) : (FsmAction.EMIT_NOTHING , FsmState.BLOCK_COMMENT      ),

    (FsmState.BLOCK_COMMENT_STAR, CharacterClass.FSLASH) : (FsmAction.EMIT_NOTHING , FsmState.START              ),
    (FsmState.BLOCK_COMMENT_STAR, CharacterClass.BSLASH) : (FsmAction.EMIT_NOTHING , FsmState.BLOCK_COMMENT      ),
    (FsmState.BLOCK_COMMENT_STAR, CharacterClass.QUOTE ) : (FsmAction.EMIT_NOTHING , FsmState.BLOCK_COMMENT      ),
    (FsmState.BLOCK_COMMENT_STAR, CharacterClass.CR    ) : (FsmAction.EMIT_CURRENT , FsmState.BLOCK_COMMENT      ),
    (FsmState.BLOCK_COMMENT_STAR, CharacterClass.NL    ) : (FsmAction.EMIT_CURRENT , FsmState.BLOCK_COMMENT      ),
    (FsmState.BLOCK_COMMENT_STAR, CharacterClass.STAR  ) : (FsmAction.EMIT_NOTHING , FsmState.BLOCK_COMMENT_STAR ),
    (FsmState.BLOCK_COMMENT_STAR, CharacterClass.OTHER ) : (FsmAction.EMIT_NOTHING , FsmState.BLOCK_COMMENT      ),

    (FsmState.STRING, CharacterClass.FSLASH) : (FsmAction.EMIT_CURRENT , FsmState.STRING           ),
    (FsmState.STRING, CharacterClass.BSLASH) : (FsmAction.EMIT_CURRENT , FsmState.STRING_BACKSLASH ),
    (FsmState.STRING, CharacterClass.QUOTE ) : (FsmAction.EMIT_CURRENT , FsmState.START            ),
    (FsmState.STRING, CharacterClass.CR    ) : (FsmAction.EMIT_CURRENT , FsmState.STRING           ),
    (FsmState.STRING, CharacterClass.NL    ) : (FsmAction.EMIT_CURRENT , FsmState.STRING           ),
    (FsmState.STRING, CharacterClass.STAR  ) : (FsmAction.EMIT_CURRENT , FsmState.STRING           ),
    (FsmState.STRING, CharacterClass.OTHER ) : (FsmAction.EMIT_CURRENT , FsmState.STRING           ),

    (FsmState.STRING_BACKSLASH, CharacterClass.FSLASH) : (FsmAction.EMIT_CURRENT , FsmState.STRING ),
    (FsmState.STRING_BACKSLASH, CharacterClass.BSLASH) : (FsmAction.EMIT_CURRENT , FsmState.STRING ),
    (FsmState.STRING_BACKSLASH, CharacterClass.QUOTE ) : (FsmAction.EMIT_CURRENT , FsmState.STRING ),
    (FsmState.STRING_BACKSLASH, CharacterClass.CR    ) : (FsmAction.EMIT_CURRENT , FsmState.STRING ),
    (FsmState.STRING_BACKSLASH, CharacterClass.NL    ) : (FsmAction.EMIT_CURRENT , FsmState.STRING ),
    (FsmState.STRING_BACKSLASH, CharacterClass.STAR  ) : (FsmAction.EMIT_CURRENT , FsmState.STRING ),
    (FsmState.STRING_BACKSLASH, CharacterClass.OTHER ) : (FsmAction.EMIT_CURRENT , FsmState.STRING )
}

character_classifications = {
    '/'  : CharacterClass.FSLASH,
    '\\' : CharacterClass.BSLASH,
    '\"' : CharacterClass.QUOTE,
    '\r' : CharacterClass.CR,
    '\n' : CharacterClass.NL,
    '*'  : CharacterClass.STAR
}

def remove_comments_from_json_with_comments(s: str) -> str:
    """Go through a state machine to remove line and block comments from JSON-with-comments."""
    output = []
    state = FsmState.START
    for current_character in s:
        character_class = character_classifications.get(current_character, CharacterClass.OTHER)
        (action, state) = fsm_definition[(state, character_class)]

        if action == FsmAction.EMIT_FSLASH_THEN_CURRENT:
            output.append("/")
        if action != FsmAction.EMIT_NOTHING:
            output.append(current_character)

    return "".join(output)


def parse_json_with_comments(json_with_comments: str):
    """Parse JSON-with-comments by removing the comments."""
    json_without_comments = remove_comments_from_json_with_comments(json_with_comments)
    return json.loads(json_without_comments)


def read_json_with_comments(filename: str):
    """Read JSON-with-comments from file."""
    with open(filename, "r") as fi:
        json_with_comments = fi.read()
    return parse_json_with_comments(json_with_comments)
