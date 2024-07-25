from nk.game.models.character import Character
from nk.proto import Heartbeat, Message, TextMessage, PlayerUpdate


def build_hb() -> Message:
    return Message(heartbeat=Heartbeat())


def build_player_update_from_character(character: Character) -> Message:
    return Message(
        player_update=PlayerUpdate(
            uuid=str(character.uuid),
            x=character.position.x,
            y=character.position.y,
        )
    )


def build_text(text: str) -> Message:
    return Message(text_message=TextMessage(text=text))
