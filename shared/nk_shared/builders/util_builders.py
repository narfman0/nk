from nk_shared import proto


def build_text_message(contents: str) -> proto.Message:
    return proto.Message(text_message=proto.TextMessage(text=contents))
