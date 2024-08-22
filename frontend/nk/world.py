from functools import lru_cache
from math import cos, sin
from uuid import uuid4

from nk_shared import builders
import pymunk
from loguru import logger
from nk_shared.map import Map
from nk_shared.models import AttackProfile, Character, Projectile, Zone
from nk_shared.proto import (
    CharacterType,
    Direction,
    ProjectileCreated,
    Projectile as ProjectileProto,
)
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
        if self.player.should_process_attack:
            self.process_local_attack(self.player)
            self.player.should_process_attack = False
        self.update_characters(dt, self.enemies)
        self.update_characters(dt, self.players)
        self.update_projectiles(dt)
        self.update_medic(dt)
        self.space.step(dt)

    def process_local_attack(self, character: Character) -> ProjectileCreated:
        attack_profile = load_attack_profile_by_name(character.attack_profile_name)
        speed = pymunk.Vec2d(
            cos(character.attack_direction), sin(character.attack_direction)
        ).scale_to_length(attack_profile.speed)
        projectile = ProjectileProto(
            uuid=str(uuid4()),
            x=character.position.x + attack_profile.emitter_offset_x,
            y=character.position.y + attack_profile.emitter_offset_y,
            dx=speed.x,
            dy=speed.y,
            attack_profile_name=character.attack_profile_name,
        )
        proto = builders.build_projectile_created(character, projectile)
        self.create_projectile(proto.projectile_created)

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
            if self.handle_projectile_collisions(projectile):
                self.projectiles.remove(projectile)

    def handle_projectile_collisions(self, projectile: Projectile) -> bool:
        """Handle collisions for a single projectile."""
        for query_info in self.space.shape_query(projectile.shape):
            if hasattr(query_info.shape.body, "character"):
                character: Character = query_info.shape.body.character
                return projectile.origin != character
            else:
                return True
        return False

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

    def create_projectile(self, proto: ProjectileCreated):
        attack_profile = load_attack_profile_by_name(
            proto.projectile.attack_profile_name
        )
        self.projectiles.append(
            Projectile(
                origin=self.get_character_by_uuid(proto.origin_uuid),
                uuid=proto.projectile.uuid,
                attack_profile=attack_profile,
                x=proto.projectile.x,
                y=proto.projectile.y,
                dx=proto.projectile.dx,
                dy=proto.projectile.dy,
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
