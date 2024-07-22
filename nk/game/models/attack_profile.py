from dataclasses import dataclass
from dataclass_wizard import YAMLWizard


@dataclass
class AttackProfile(YAMLWizard):
    name: str
    image_path: str
    speed: float
    radius: float
    emitter_offset_x: float = 0
    emitter_offset_y: float = 0
