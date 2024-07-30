import logging
from dataclasses import dataclass

import pygame
from pygame.event import Event

from nk_shared import builders
from nk_shared.models.character import Character
from nk_shared.proto import Direction
from nk_shared.util.math import cartesian_to_isometric
from nk_shared.util import direction_util

from nk.game_state import GameState
from nk.settings import WIDTH, HEIGHT
from nk.ui.character_sprite import CharacterSprite
from nk.ui.input import (
    ActionEnum,
    read_input_player_move_direction,
    read_input_player_actions,
)
from nk.ui.renderables import (
    create_renderable_list,
    MapRenderable,
    renderables_generate_key,
    SpriteRenderable,
    BlittableRenderable,
)
from nk.ui.screen import Screen, ScreenManager

logger = logging.getLogger(__name__)
DEFAULT_SCREEN_SCALE = 5


@dataclass
class CharacterStruct:
    character: Character
    sprite: CharacterSprite
    sprite_group: pygame.sprite.Group
    last_moving_direction: Direction


class GameScreen(Screen):  # pylint: disable=too-many-instance-attributes
    """UI screen for game state"""

    def __init__(self, screen_manager: ScreenManager, game_state: GameState):
        super().__init__()
        self.screen_manager = screen_manager
        self.game_state = game_state
        self.world = game_state.world
        self.network = game_state.network
        self.projectile_image_dict = {}
        self.cam_x, self.cam_y = 0, 0
        self.screen_scale = DEFAULT_SCREEN_SCALE
        self.recalculate_screen_scale_derivatives()
        self.game_state.character_added_callback = self.handle_character_added
        self.game_state.character_attacked_callback = self.handle_character_attacked
        self.player_struct = CharacterStruct(
            self.world.player,
            None,
            pygame.sprite.Group(),
            None,
        )
        self.update_player_sprite()
        self.character_structs = [self.player_struct]
        for enemy in self.world.enemies:
            sprite = CharacterSprite(enemy.character_type.name.lower())
            self.character_structs.append(
                CharacterStruct(enemy, sprite, pygame.sprite.Group(sprite), None)
            )

        self.ground_renderables = list(self.generate_map_renderables(ground=True))
        self.map_renderables = list(self.generate_map_renderables(ground=False))

    def update(self, dt: float, events: list[Event]):
        player_actions = read_input_player_actions(events)
        self.handle_player_actions(player_actions)
        player_move_direction = read_input_player_move_direction()
        self.world.update(dt, player_move_direction)
        self.cam_x, self.cam_y = cartesian_to_isometric(
            self.world.player.position.x * self.world.map.tile_width // 2,
            self.world.player.position.y * self.world.map.tile_width // 2,
        )
        if (
            self.world.player.alive
            and self.world.player.character_type_short
            != self.player_struct.sprite.sprite_name
        ):
            # ideally we could pass a callback here but :shrugs:
            self.update_player_sprite()
        if player_move_direction:
            self.world.player.facing_direction = player_move_direction
        assert self.world.player.facing_direction is not None
        self.update_character_structs(dt)
        self.game_state.update()

    def handle_player_actions(self, player_actions: list[ActionEnum]):
        if ActionEnum.DASH in player_actions:
            if not self.world.player.dashing:
                self.world.player.dash()
        if ActionEnum.ATTACK in player_actions:
            if self.world.player.alive and not self.world.player.attacking:
                self.world.player.attack()
                self.network.send(builders.build_character_attacked(self.world.player))
                self.player_struct.sprite.change_animation("attack")
        if ActionEnum.PLAYER_HEAL in player_actions:
            self.world.player.handle_healing_received(1.0)
            logger.info("Player now has %r hp", self.world.player.hp)
        if ActionEnum.PLAYER_INVICIBILITY in player_actions:
            self.world.player.invincible = not self.world.player.invincible
            logger.info("Player invincibility set to %r", self.world.player.invincible)
        if ActionEnum.ZOOM_OUT in player_actions:
            # TODO self.screen_scale = max(3, self.screen_scale - 1) # pylint: disable=fixme
            self.recalculate_screen_scale_derivatives()
        if ActionEnum.ZOOM_IN in player_actions:
            # TODO self.screen_scale = min(6, self.screen_scale + 1) # pylint: disable=fixme
            self.recalculate_screen_scale_derivatives()

    def draw(self, dest_surface: pygame.Surface):  # pylint: disable=arguments-renamed
        renderables = create_renderable_list()
        for map_renderable in self.map_renderables:
            blit_x, blit_y = map_renderable.blit_coords
            bottom_y = blit_y - self.cam_y + map_renderable.blit_image.get_height() - 8
            renderable = BlittableRenderable(
                renderables_generate_key(map_renderable.layer, bottom_y),
                map_renderable.blit_image,
                (blit_x - self.cam_x, blit_y - self.cam_y),
            )
            renderables.add(renderable)
        for renderable in self.generate_projectile_renderables():
            renderables.add(renderable)
        for character_struct in self.character_structs:
            img_height = character_struct.sprite.image.get_height()
            bottom_y = character_struct.sprite.rect.top + img_height // 2
            key = renderables_generate_key(self.world.map.get_1f_layer_id(), bottom_y)
            renderables.add(SpriteRenderable(key, character_struct.sprite_group))

        surface = pygame.Surface(size=(self.screen_width, self.screen_height))
        for ground_renderable in self.ground_renderables:
            blit_x, blit_y = ground_renderable.blit_coords
            blit_coords = (blit_x - self.cam_x, blit_y - self.cam_y)
            surface.blit(ground_renderable.blit_image, blit_coords)
        for renderable in renderables:
            renderable.draw(surface)
        pygame.transform.scale_by(
            surface, dest_surface=dest_surface, factor=self.screen_scale
        )

    def generate_projectile_renderables(self):
        for projectile in self.world.projectiles:
            image = self.projectile_image_dict.get(projectile.attack_profile.image_path)
            if image is None:
                path = f"../data/projectiles/{projectile.attack_profile.image_path}.png"
                image = pygame.image.load(path).convert_alpha()
                self.projectile_image_dict[projectile.attack_profile.image_path] = image
            blit_x, blit_y = self.calculate_draw_coordinates(
                projectile.x, projectile.y, image
            )
            bottom_y = blit_y - self.cam_y + image.get_height()
            yield BlittableRenderable(
                renderables_generate_key(self.world.map.get_1f_layer_id(), bottom_y),
                image,
                (blit_x - self.cam_x, blit_y - self.cam_y),
            )

    def update_character_structs(self, dt: float):
        for character_struct in self.character_structs:
            character = character_struct.character
            sprite = character_struct.sprite
            if character.alive:
                if not character.attacking:
                    if character.moving_direction:
                        if (
                            character.moving_direction
                            != character_struct.last_moving_direction
                        ):
                            sprite.move(
                                direction_util.to_isometric(character.moving_direction)
                            )
                        sprite.change_animation("run")
                    else:
                        sprite.change_animation("idle")
                character_struct.last_moving_direction = character.facing_direction
            else:
                if sprite.sprite_name != "death":
                    sprite.change_animation("death", loop=False)
            x, y = self.calculate_draw_coordinates(
                character.position.x, character.position.y, sprite.image
            )
            sprite.set_position(x - self.cam_x, y - self.cam_y)

        for character_struct in self.character_structs:
            character_struct.sprite_group.update(dt)

    def generate_map_renderables(self, ground: bool):
        """We can statically generate the blit coords once in the beginning,
        avoiding a bunch of coordinate conversions."""
        ground_ids = self.world.map.get_ground_layer_ids()
        for layer in range(self.world.map.get_tile_layer_count()):
            if ground and layer not in ground_ids or not ground and layer in ground_ids:
                continue
            x_offset, y_offset = self.world.map.get_layer_offsets(layer)
            for x in range(0, self.world.map.width):
                for y in range(0, self.world.map.height):
                    blit_image = self.world.map.get_tile_image(x, y, layer)
                    if blit_image:
                        blit_x, blit_y = self.calculate_draw_coordinates(
                            x, y, blit_image
                        )
                        yield MapRenderable(
                            layer=layer,
                            blit_image=blit_image,
                            blit_coords=(blit_x + x_offset, blit_y + y_offset),
                        )

    def calculate_draw_coordinates(
        self,
        x: float,
        y: float,
        image: pygame.Surface,
    ):
        cartesian_x = x * self.world.map.tile_width // 2
        cartesian_y = y * self.world.map.tile_width // 2
        iso_x, iso_y = cartesian_to_isometric(cartesian_x, cartesian_y)
        x = iso_x + self.camera_offset_x - image.get_width() // 2
        y = iso_y + self.camera_offset_y - image.get_height() // 2
        return (x, y)

    def update_player_sprite(self):
        sprite = CharacterSprite(self.world.player.character_type_short)
        sprite.set_position(
            self.screen_width // 2 - sprite.image.get_width() // 2,
            self.screen_height // 2 - sprite.image.get_height() // 2,
        )
        self.player_struct.sprite = sprite
        self.player_struct.sprite_group.empty()
        self.player_struct.sprite_group.add(sprite)

    def recalculate_screen_scale_derivatives(self):
        self.screen_width = WIDTH // self.screen_scale
        self.screen_height = HEIGHT // self.screen_scale
        self.camera_offset_x = self.screen_width // 2
        self.camera_offset_y = self.screen_height // 2

    def handle_character_added(self, character: Character):
        sprite = CharacterSprite(character.character_type_short)
        self.character_structs.append(
            CharacterStruct(character, sprite, pygame.sprite.Group(sprite), None)
        )

    def handle_character_attacked(self, character: Character):
        for cstruct in self.character_structs:
            if cstruct.character == character:
                cstruct.sprite.change_animation("attack")
                return
