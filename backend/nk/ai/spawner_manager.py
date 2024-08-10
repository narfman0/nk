from abc import ABC, abstractmethod
import heapq

from nk.models import Enemy
from nk_shared.proto import CharacterType

from nk.ai.models import SpawnerStruct
from nk_shared.models.zone import Environment


class SpawnerProvider(ABC):
    @abstractmethod
    def spawn_enemy(
        self, character_type: CharacterType, center_x: int, center_y: int
    ) -> Enemy:
        raise NotImplementedError()


class SpawnerManager:
    def __init__(
        self, provider: SpawnerProvider, environment_features: list[Environment]
    ):
        self.provider = provider
        self.spawners: list[SpawnerStruct] = []
        self.current_time = 0
        for environment_feature in environment_features:
            for spawner in environment_feature.spawners:
                next_spawn = spawner.spawn_frequency_s
                self.spawners.append(
                    SpawnerStruct(
                        spawner=spawner,
                        next_spawn_time_s=next_spawn,
                        parent_feature=environment_feature,
                    )
                )
        heapq.heapify(self.spawners)

    def update(self, dt: float):
        """Update the spawners to spawn enemies based on their next spawn time."""
        self.current_time += dt
        while self.spawners and self.spawners[0].next_spawn_time_s <= self.current_time:
            spawn_str = heapq.heappop(self.spawners)
            self.provider.spawn_enemy(
                spawn_str.spawner.character_type, spawn_str.spawn_x, spawn_str.spawn_y
            )
            next_spawn = self.current_time + spawn_str.spawner.spawn_frequency_s
            spawn_str.next_spawn_time_s = next_spawn
            heapq.heappush(self.spawners, spawn_str)
