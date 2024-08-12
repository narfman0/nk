from dataclasses import dataclass

from nk_shared.models.zone import Environment, Spawner


@dataclass
class SpawnerStruct:
    spawner: Spawner
    next_spawn_time_s: float
    parent_feature: Environment

    @property
    def spawn_x(self) -> int:
        return self.parent_feature.center_x + self.spawner.offset_x

    @property
    def spawn_y(self) -> int:
        return self.parent_feature.center_y + self.spawner.offset_y

    def __lt__(self, other) -> bool:
        return self.next_spawn_time_s < other.next_spawn_time_s
