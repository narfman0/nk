from dataclasses import dataclass
from functools import lru_cache
from dataclass_wizard import YAMLWizard
from nk_shared.map import DATA_ROOT


@dataclass
class Weapon(YAMLWizard):
    name: str
    image_path: str
    speed: float
    radius: float
    emitter_offset_x: float = 0
    emitter_offset_y: float = 0


@lru_cache
def load_weapon_by_name(weapon_name: str) -> Weapon:
    path = f"{DATA_ROOT}/weapons/{weapon_name}.yml"
    return Weapon.from_yaml_file(path)
