from functools import lru_cache

import pymunk
from loguru import logger
from nk_shared.map import Map
from nk_shared.models import AttackProfile, Character, Projectile, Zone
from nk_shared.proto import CharacterType, Direction
from nk_shared.proto import Projectile as ProjectileProto
from typing_extensions import Unpack

from nk.settings import NK_DATA_ROOT

HEAL_DST_SQ = 5  # this should be on the backend but whatevs
HEAL_AMT = 10.0


class World:  # pylint: disable=too-many-instance-attributes
    def __init__(self, uuid: str, x: float, y: float, zone_name="1"):
        self.projectiles: list[Projectile] = []
        self.attack_profiles: dict[str, AttackProfile] = {}
        self.space = pymunk.Space()
        self.zone = Zone.from_yaml_file(f"{NK_DATA_ROOT}/zones/{zone_name}.yml")
        self.map = Map(self.zone.tmx_path)
        self.map.add_map_geometry_to_space(self.space)
        for feature in self.zone.environment_features:
            tilemap = Map(feature.tmx_name)
            tilemap.add_map_geometry_to_space(
                self.space,
                feature.center_x - tilemap.width // 2,
                feature.center_y - tilemap.height // 2,
            )

        # initialize player
        self.player = self.add_character(
            uuid=uuid,
            character_type=CharacterType.CHARACTER_TYPE_PIGSASSIN,
            start_x=x,
            start_y=y,
        )

        self.enemies: list[Character] = []
        self.players: list[Character] = []

    def update(
        self,
        dt: float,
        player_moving_direction: Direction,
    ):
        self.player.moving_direction = player_moving_direction
        self.player.update(dt)
        self.update_characters(dt, self.enemies)
        self.update_characters(dt, self.players)
        self.update_projectiles(dt)
        self.update_medic(dt)
        self.space.step(dt)

    def update_medic(self, dt: float):
        for medic in self.zone.medics:
            # pylint: disable-next=no-member
            dst_sq = self.player.position.get_dist_sqrd((medic.x, medic.y))
            if dst_sq < HEAL_DST_SQ:
                self.player.handle_healing_received(HEAL_AMT * dt)
                return

    def update_characters(self, dt: float, characters: list[Character]):
        for character in characters:
            character.update(dt)
            if not character.alive and not character.body_removal_processed:
                character.body_removal_processed = True
                self.space.remove(
                    character.body, character.shape, character.hitbox_shape
                )

    def update_projectiles(self, dt: float):
        for projectile in self.projectiles:
            projectile.update(dt)

    def add_enemy(self, **character_kwargs: Unpack[Character]) -> Character:
        character = self.add_character(**character_kwargs)
        self.enemies.append(character)
        return character

    def add_player(self, **character_kwargs: Unpack[Character]) -> Character:
        character = self.add_character(**character_kwargs)
        self.players.append(character)
        return character

    def add_character(self, **character_kwargs: Unpack[Character]) -> Character:
        character = Character(**character_kwargs)
        self.space.add(character.body, character.shape, character.hitbox_shape)
        return character

    def get_enemy_by_uuid(self, uuid: str) -> Character | None:
        for character in self.enemies:
            if character.uuid == uuid:
                return character
        return None

    def get_player_by_uuid(self, uuid: str) -> Character | None:
        for character in self.players:
            if character.uuid == uuid:
                return character
        return None

    def get_character_by_uuid(self, uuid: str) -> Character | None:
        for character in self.players + self.enemies + [self.player]:
            if character.uuid == uuid:
                return character
        logger.debug("Could not find character with uuid {}", uuid)
        return None

    def create_projectile(self, proto: ProjectileProto):
        attack_profile = load_attack_profile_by_name(proto.attack_profile_name)
        self.projectiles.append(
            Projectile(
                uuid=proto.uuid,
                attack_profile=attack_profile,
                x=proto.x,
                y=proto.y,
                dx=proto.dx,
                dy=proto.dy,
            )
        )
        logger.debug("Created projectile: {}", self.projectiles[-1])

    def get_projectile_by_uuid(self, uuid: str) -> Projectile | None:
        for projectile in self.projectiles:
            if projectile.uuid == uuid:
                return projectile
        return None


@lru_cache
def load_attack_profile_by_name(attack_profile_name: str) -> AttackProfile:
    path = f"{NK_DATA_ROOT}/attack_profiles/{attack_profile_name}.yml"
    return AttackProfile.from_yaml_file(path)
