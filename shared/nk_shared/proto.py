# Generated by the protocol buffer compiler.  DO NOT EDIT!
# sources: proto/direction.proto, proto/character.proto, proto/player.proto, proto/projectile.proto, proto/text_message.proto, proto/message.proto
# plugin: python-betterproto
from dataclasses import dataclass

import betterproto


class Direction(betterproto.Enum):
    DIRECTION_UNSPECIFIED = 0
    DIRECTION_N = 1
    DIRECTION_NE = 2
    DIRECTION_E = 3
    DIRECTION_SE = 4
    DIRECTION_S = 5
    DIRECTION_SW = 6
    DIRECTION_W = 7
    DIRECTION_NW = 8


class CharacterType(betterproto.Enum):
    CHARACTER_TYPE_UNSPECIFIED = 0
    CHARACTER_TYPE_PIGSASSIN = 1
    CHARACTER_TYPE_ASSAULT_DROID = 2
    CHARACTER_TYPE_DROID_ASSASSIN = 3
    CHARACTER_TYPE_SAMURAI = 4
    CHARACTER_TYPE_SHADOW_GUARDIAN = 5


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
    requested: bool = betterproto.bool_field(1)


@dataclass
class PlayerJoinResponse(betterproto.Message):
    uuid: str = betterproto.string_field(1)
    x: float = betterproto.float_field(2)
    y: float = betterproto.float_field(3)


@dataclass
class PlayerLeft(betterproto.Message):
    uuid: str = betterproto.string_field(1)


@dataclass
class Projectile(betterproto.Message):
    uuid: str = betterproto.string_field(1)
    x: float = betterproto.float_field(2)
    y: float = betterproto.float_field(3)
    dx: float = betterproto.float_field(4)
    dy: float = betterproto.float_field(5)
    attack_profile_name: str = betterproto.string_field(6)


@dataclass
class ProjectileCreated(betterproto.Message):
    projectile: "Projectile" = betterproto.message_field(1)


@dataclass
class ProjectileDestroyed(betterproto.Message):
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
    player_left: "PlayerLeft" = betterproto.message_field(101, group="payload")
    player_joined: "PlayerJoined" = betterproto.message_field(100, group="payload")
    player_join_request: "PlayerJoinRequest" = betterproto.message_field(
        102, group="payload"
    )
    player_join_response: "PlayerJoinResponse" = betterproto.message_field(
        103, group="payload"
    )
    projectile_created: "ProjectileCreated" = betterproto.message_field(
        300, group="payload"
    )
    projectile_destroyed: "ProjectileDestroyed" = betterproto.message_field(
        301, group="payload"
    )
    text_message: "TextMessage" = betterproto.message_field(1, group="payload")
