# Generated by the protocol buffer compiler.  DO NOT EDIT!
# sources: proto/direction.proto, proto/character.proto, proto/player.proto, proto/text_message.proto, proto/message.proto
# plugin: python-betterproto
from dataclasses import dataclass

import betterproto


class Direction(betterproto.Enum):
    INVALID_DIRECTION = 0
    N = 1
    NE = 2
    E = 3
    SE = 4
    S = 5
    SW = 6
    W = 7
    NW = 8


class CharacterType(betterproto.Enum):
    INVALID_CHARACTER_TYPE = 0
    PIGSASSIN = 1
    ASSAULT_DROID = 2
    DROID_ASSASSIN = 3
    SAMURAI = 4
    SHADOW_GUARDIAN = 5


@dataclass
class CharacterAttacked(betterproto.Message):
    uuid: str = betterproto.string_field(1)


@dataclass
class CharacterDamaged(betterproto.Message):
    uuid: str = betterproto.string_field(1)
    damage: float = betterproto.float_field(2)


@dataclass
class CharacterUpdated(betterproto.Message):
    uuid: str = betterproto.string_field(1)
    x: float = betterproto.float_field(2)
    y: float = betterproto.float_field(3)
    character_type: "CharacterType" = betterproto.enum_field(4)
    facing_direction: "Direction" = betterproto.enum_field(5)
    moving_direction: "Direction" = betterproto.enum_field(6)


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
    character_updated: "CharacterUpdated" = betterproto.message_field(
        200, group="payload"
    )
    character_attacked: "CharacterAttacked" = betterproto.message_field(
        201, group="payload"
    )
    character_damaged: "CharacterDamaged" = betterproto.message_field(
        202, group="payload"
    )
    player_joined: "PlayerJoined" = betterproto.message_field(100, group="payload")
    player_left: "PlayerLeft" = betterproto.message_field(101, group="payload")
    player_join_request: "PlayerJoinRequest" = betterproto.message_field(
        102, group="payload"
    )
    player_join_response: "PlayerJoinResponse" = betterproto.message_field(
        103, group="payload"
    )
    text_message: "TextMessage" = betterproto.message_field(1, group="payload")
