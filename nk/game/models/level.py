from dataclasses import dataclass
from dataclass_wizard import YAMLWizard


@dataclass
class LevelEnemy:
    character_type: str
    x: int
    y: int


@dataclass
class Level(YAMLWizard):
    tmx_path: str
    enemies: list[LevelEnemy]
