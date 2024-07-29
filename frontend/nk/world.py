import pymunk
from typing_extensions import Unpack
from uuid import UUID

from nk_shared.map import Map
from nk_shared.models import (
    AttackProfile,
    AttackType,
    Character,
    Zone,
    Projectile,
)
from nk_shared.proto import CharacterType, Direction
from nk_shared.util import direction_util


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
        self.player = Character(
            character_type=CharacterType.PIGSASSIN,
            start_x=0.5 + tile_x,
            start_y=0.5 + tile_y,
        )
        self.space.add(self.player.body, self.player.shape, self.player.hitbox_shape)

        self.enemies: list[Character] = []

    def update(
        self,
        dt: float,
        player_moving_direction: Direction,
    ):
        self.player.moving_direction = player_moving_direction
        self.player.update(dt)
        if self.player.should_process_attack:
            self.process_attack_damage(self.player, self.enemies)
        for enemy in self.enemies:
            enemy.update(dt)
            if not enemy.alive and not enemy.body_removal_processed:
                enemy.body_removal_processed = True
                self.space.remove(enemy.body, enemy.shape, enemy.hitbox_shape)
        self.update_projectiles(dt)
        self.space.step(dt)

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

    def process_attack_damage(self, attacker: Character, enemies: list[Character]):
        attacker.should_process_attack = False
        for enemy in enemies:
            if attacker.hitbox_shape.shapes_collide(enemy.shape).points:
                enemy.handle_damage_received(1)

    def add_enemy(self, **character_kwargs: Unpack[Character]) -> Character:
        enemy = Character(**character_kwargs)
        self.enemies.append(enemy)
        self.space.add(enemy.body, enemy.shape, enemy.hitbox_shape)
        return enemy

    def get_enemy_by_uuid(self, uuid: UUID) -> Character | None:
        for enemy in self.enemies:
            if enemy.uuid == uuid:
                return enemy
