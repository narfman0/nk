from dataclasses import dataclass
from dataclass_wizard import YAMLWizard

from nk_shared.proto import CharacterType


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
class Zone(YAMLWizard):
    tmx_path: str
    enemy_groups: list[EnemyGroup]
