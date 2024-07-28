from dataclasses import dataclass
from dataclass_wizard import YAMLWizard


@dataclass
class EnemyGroup:
    character_type: str
    count: int
    center_x: int
    center_y: int


@dataclass
class Level(YAMLWizard):
    tmx_path: str
    enemy_groups: list[EnemyGroup]
