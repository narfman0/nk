from dataclasses import dataclass
from functools import lru_cache

from dataclass_wizard import YAMLWizard

from nk_shared.models.attack_type import AttackType
from nk_shared.settings import DATA_ROOT


@dataclass
class Weapon(YAMLWizard):
    attack_duration: float = None
    attack_distance: float = None
    attack_time_until_damage: float = None
    attack_type: AttackType = AttackType.MELEE


@dataclass
class RangedWeapon(Weapon):
    projectile_image_path: str = None
    projectile_speed: float = None
    projectile_radius: float = None
    clip_size: int = None
    reload_time: float = None


@lru_cache
def load_weapon_by_name(weapon_name: str) -> Weapon | RangedWeapon:
    path = f"{DATA_ROOT}/weapons/{weapon_name}.yml"
    with open(path, encoding="utf-8") as weapon_file:
        weapon_yaml = weapon_file.read()
        weapon = Weapon.from_yaml(weapon_yaml)
        if weapon.attack_type == AttackType.RANGED:
            weapon = RangedWeapon.from_yaml(weapon_yaml)
    return weapon
