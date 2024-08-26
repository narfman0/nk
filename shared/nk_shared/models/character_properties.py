from dataclasses import dataclass

from dataclass_wizard import YAMLWizard


@dataclass
class CharacterProperties(YAMLWizard):  # pylint: disable=too-many-instance-attributes
    mass: float = 10
    dash_cooldown: float = None
    dash_duration: float = None
    dash_scalar: float = None
    run_force: float = 1000
    running_stop_threshold: float = 1.0
    max_velocity: float = 1
    radius: float = 0.5
    weapon_name: str = None
    hp_max: int = 1
    chase_distance: float = 15
