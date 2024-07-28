import pymunk
from uuid import UUID

from nk_shared.map import Map
from nk_shared.models import (
    AttackProfile,
    AttackType,
    Character,
    Direction,
    Level,
    Projectile,
)
from nk_shared.proto import CharacterType


class World:
    def __init__(self, level_name="1"):
        self.projectiles: list[Projectile] = []
        self.attack_profiles: dict[str, AttackProfile] = {}
        self.space = pymunk.Space()
        self.level = Level.from_yaml_file(f"../data/levels/{level_name}.yml")
        self.map = Map(self.level.tmx_path)
        self.map.add_map_geometry_to_space(self.space)

        # initialize player
        tile_x, tile_y = self.map.get_start_tile()
        self.player = Character(
            character_type=CharacterType.PIGSASSIN.name.lower(),
        )
        self.player.body.position = (0.5 + tile_x, 0.5 + tile_y)
        self.space.add(self.player.body, self.player.shape, self.player.hitbox_shape)

        self.enemies: list[Character] = []
        self.npcs: list[Character] = []

    def update(
        self,
        dt: float,
        player_movement_direction: Direction,
    ):
        self.player.movement_direction = player_movement_direction
        self.player.update(dt)
        if self.player.should_process_attack:
            self.process_attack_damage(self.player, self.enemies)
        for npc in self.npcs:
            npc.update(dt)
        for enemy in self.enemies:
            enemy.ai(dt, self.player)
            enemy.update(dt)
            if not enemy.alive and not enemy.body_removal_processed:
                enemy.body_removal_processed = True
                self.space.remove(enemy.body, enemy.shape, enemy.hitbox_shape)
            if enemy.should_process_attack:
                if enemy.attack_type == AttackType.MELEE:
                    self.process_attack_damage(enemy, [self.player])
                elif enemy.attack_type == AttackType.RANGED:
                    attack_profile = self.attack_profiles.get(enemy.attack_profile_name)
                    if not attack_profile:
                        attack_profile = AttackProfile.from_yaml_file(
                            f"../data/attack_profiles/{enemy.attack_profile_name}.yml"
                        )
                        self.attack_profiles[enemy.attack_profile_name] = attack_profile
                    speed = enemy.facing_direction.to_vector().scale_to_length(
                        attack_profile.speed
                    )
                    projectile = Projectile(
                        x=enemy.position.x + attack_profile.emitter_offset_x,
                        y=enemy.position.y + attack_profile.emitter_offset_y,
                        dx=speed.x,
                        dy=speed.y,
                        origin=enemy,
                        attack_profile=attack_profile,
                    )
                    self.projectiles.append(projectile)
                    enemy.should_process_attack = False
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

    def add_npc(self, uuid: UUID, x: float, y: float, character_type: str) -> Character:
        npc = Character(uuid=uuid, character_type=character_type)
        npc.body.position = (x, y)
        self.npcs.append(npc)
        self.space.add(npc.body, npc.shape, npc.hitbox_shape)
        return npc

    def get_npc_by_uuid(self, uuid: UUID) -> Character | None:
        for npc in self.npcs:
            if npc.uuid == uuid:
                return npc
