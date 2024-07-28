# Generated by the protocol buffer compiler.  DO NOT EDIT!
# sources: proto/character_update.proto, proto/player_joined.proto, proto/player_join_request.proto, proto/player_join_response.proto, proto/player_left.proto, proto/text_message.proto, proto/message.proto
# plugin: python-betterproto
from dataclasses import dataclass

import betterproto


@dataclass
class CharacterUpdate(betterproto.Message):
    uuid: str = betterproto.string_field(1)
    x: float = betterproto.float_field(2)
    y: float = betterproto.float_field(3)


@dataclass
class PlayerJoined(betterproto.Message):
    uuid: str = betterproto.string_field(1)


@dataclass
class PlayerJoinRequest(betterproto.Message):
    uuid: str = betterproto.string_field(1)


@dataclass
class PlayerJoinResponse(betterproto.Message):
    success: bool = betterproto.bool_field(1)
    x: float = betterproto.float_field(2)
    y: float = betterproto.float_field(3)


@dataclass
class PlayerLeft(betterproto.Message):
    uuid: str = betterproto.string_field(1)


@dataclass
class TextMessage(betterproto.Message):
    text: str = betterproto.string_field(1)


@dataclass
class Message(betterproto.Message):
    character_update: "CharacterUpdate" = betterproto.message_field(5, group="payload")
    player_joined: "PlayerJoined" = betterproto.message_field(2, group="payload")
    player_left: "PlayerLeft" = betterproto.message_field(3, group="payload")
    player_join_request: "PlayerJoinRequest" = betterproto.message_field(
        4, group="payload"
    )
    player_join_response: "PlayerJoinResponse" = betterproto.message_field(
        6, group="payload"
    )
    text_message: "TextMessage" = betterproto.message_field(1, group="payload")
