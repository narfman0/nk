from nk_shared import proto


def build_text_message(contents: str) -> proto.Message:
    return proto.Message(text_message=proto.TextMessage(text=contents))


def build_spawn_requested(
    x: float, y: float, count: int, character_type: proto.CharacterType
) -> proto.Message:
    return proto.Message(
        spawn_requested=proto.SpawnRequested(
            x=x, y=y, count=count, character_type=character_type
        )
    )
