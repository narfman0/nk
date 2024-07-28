from dataclasses import dataclass
from dataclass_wizard import YAMLWizard


@dataclass
class Level(YAMLWizard):
    tmx_path: str
