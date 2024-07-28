from nk_shared.models.character import Character
from nk.proto import Message, TextMessage, CharacterUpdate


def build_character_update_from_character(character: Character) -> Message:
    return Message(
        character_update=CharacterUpdate(
            uuid=str(character.uuid),
            x=character.position.x,
            y=character.position.y,
        )
    )


def build_text(text: str) -> Message:
    return Message(text_message=TextMessage(text=text))
