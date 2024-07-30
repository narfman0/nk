from dataclasses import dataclass

from pymunk import Body, Circle

from nk_shared.models import AttackProfile, Character
from nk_shared.proto import Projectile as ProjectileProto


@dataclass
class Projectile(ProjectileProto):
    origin: Character = None
    attack_profile: AttackProfile = None
    body: Body = None
    shape: Circle = None

    def __post_init__(self):
        self.body = Body()
        self.body.position = (self.x, self.y)
        self.shape = Circle(body=self.body, radius=self.attack_profile.radius)

    def update(self, dt: float):
        self.x += dt * self.dx
        self.y += dt * self.dy
        self.body.position = (self.x, self.y)
