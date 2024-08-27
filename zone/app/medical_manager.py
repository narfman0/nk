from typing import Protocol

from nk_shared import builders
from nk_shared.models.character import Character
from nk_shared.models.zone import Medic
from nk_shared.proto import Message

from app.models import Player

HEAL_DST_SQ = 5
HEAL_AMT = 10.0
RESPAWN_TIME = 5.0


class ProviderProtocol(Protocol):
    def get_character_by_uuid(self, uuid: str) -> Character | None: ...

    async def publish(self, message: Message, **kwargs) -> None: ...

    @property
    def players(self) -> list[Player]: ...


class MedicalManager:
    def __init__(self, protocol: ProviderProtocol, medics: list[Medic]):
        self.protocol = protocol
        self.medics = medics
        self._player_respawns: dict[str, float] = {}

    async def update(self, dt: float):
        for player in self.protocol.players:
            self.update_medic(dt, player)
        await self.update_respawns(dt)

    async def update_respawns(self, dt: float):
        """Update respawn timers for players"""
        for player_uuid in list(self._player_respawns):
            respawn_time = self._player_respawns[player_uuid]
            respawn_time -= dt
            if respawn_time <= 0:
                del self._player_respawns[player_uuid]
                player = self.protocol.get_character_by_uuid(player_uuid)
                await self.respawn_player(player)
            else:
                self._player_respawns[player_uuid] = respawn_time

    async def respawn_player(self, player: Player):
        player.hp = player.hp_max
        closest_dst_sq = float("inf")
        spawn_point = None
        for medic in self.medics:
            dst_sq = player.position.get_dist_sqrd((medic.x, medic.y))
            if dst_sq < closest_dst_sq:
                closest_dst_sq = dst_sq
                spawn_point = (medic.x, medic.y)
        player.body.position = spawn_point
        await self.protocol.publish(builders.build_player_respawned(player))

    def schedule_respawn(self, player: Player):
        self._player_respawns[player.uuid] = RESPAWN_TIME

    def update_medic(self, dt: float, player: Player):
        """Check if player is in range of a medic and heal if so"""
        for medic in self.medics:
            dst_sq = player.position.get_dist_sqrd((medic.x, medic.y))
            if dst_sq < HEAL_DST_SQ:
                player.handle_healing_received(HEAL_AMT * dt)
                return
