from dataclasses import dataclass
from dataclass_wizard import YAMLWizard

from nk_shared.proto import CharacterType, EnvironmentType


@dataclass
class Spawner:
    character_type_str: str
    offset_x: int
    offset_y: int
    spawn_frequency_s: float = 10

    @property
    def character_type(self) -> CharacterType:
        return CharacterType[f"CHARACTER_TYPE_{self.character_type_str.upper()}"]


@dataclass
class EnemyGroup:
    character_type_str: str
    count: int
    center_x: int
    center_y: int

    @property
    def character_type(self) -> CharacterType:
        return CharacterType[f"CHARACTER_TYPE_{self.character_type_str.upper()}"]


@dataclass
class Environment:
    environment_type_str: str
    center_x: int
    center_y: int
    spawners: list[Spawner]

    @property
    def environment_type(self) -> EnvironmentType:
        return EnvironmentType[f"ENVIRONMENT_TYPE_{self.environment_type_str.upper()}"]


@dataclass
class Zone(YAMLWizard):
    tmx_path: str
    enemy_groups: list[EnemyGroup]
    environment_features: list[Environment]
