import logging
import pymunk
from typing_extensions import Unpack
from uuid import UUID

from nk_shared.map import Map
from nk_shared.models import (
    AttackProfile,
    Character,
    Zone,
    Projectile,
)
from nk_shared.proto import CharacterType, Direction

logger = logging.getLogger(__name__)


class World:
    def __init__(self, zone_name="1"):
        self.projectiles: list[Projectile] = []
        self.attack_profiles: dict[str, AttackProfile] = {}
        self.space = pymunk.Space()
        self.zone = Zone.from_yaml_file(f"../data/zones/{zone_name}.yml")
        self.map = Map(self.zone.tmx_path)
        self.map.add_map_geometry_to_space(self.space)

        # initialize player
        tile_x, tile_y = self.map.get_start_tile()
        self.player = self.add_character(
            character_type=CharacterType.PIGSASSIN,
            start_x=0.5 + tile_x,
            start_y=0.5 + tile_y,
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
        self.space.step(dt)

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
            should_remove = False
            for query_info in self.space.shape_query(projectile.shape):
                if hasattr(query_info.shape.body, "character"):
                    character = query_info.shape.body.character
                    # let's avoid friendly fire. eventually it'd be cool to have factions.
                    player_involved = (
                        projectile.origin == self.player or character == self.player
                    )
                    if player_involved and projectile.origin != character:
                        character.handle_damage_received(1)
                        should_remove = True
                else:
                    should_remove = True
            if should_remove:
                self.projectiles.remove(projectile)

    def add_enemy(self, **character_kwargs: Unpack[Character]) -> Character:
        character = self.add_character(**character_kwargs)
        self.enemies.append(character)
        return character

    def add_character(self, **character_kwargs: Unpack[Character]) -> Character:
        character = Character(**character_kwargs)
        self.space.add(character.body, character.shape, character.hitbox_shape)
        return character

    def get_enemy_by_uuid(self, uuid: UUID) -> Character | None:
        for character in self.enemies:
            if character.uuid == uuid:
                return character

    def get_player_by_uuid(self, uuid: UUID) -> Character | None:
        for character in self.players:
            if character.uuid == uuid:
                return character

    def get_character_by_uuid(self, uuid: UUID) -> Character | None:
        for character in self.players + self.enemies + [self.player]:
            if character.uuid == uuid:
                return character
        logger.info(f"Could not find character with uuid {uuid}")
