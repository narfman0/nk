from dataclasses import dataclass
from functools import lru_cache
from math import atan2

from nk_shared.map import Map
import pygame
from loguru import logger
from nk_shared import builders
from nk_shared.models.character import Character
from nk_shared.proto import Direction
from nk_shared.util import direction_util
from nk_shared.util.math import cartesian_to_isometric, isometric_to_cartesian
from pygame.event import Event

from nk.game_state import GameState
from nk.settings import HEIGHT, NK_DATA_ROOT, WIDTH
from nk.ui.character_sprite import CharacterSprite
from nk.ui.game_gui import GameGui
from nk.ui.input import (
    ActionEnum,
    read_input_player_actions,
    read_input_player_move_direction,
)
from nk.ui.renderables import (
    BlittableRenderable,
    MapRenderable,
    SpriteRenderable,
    create_renderable_list,
    renderables_generate_key,
)
from nk.ui.screen import Screen, ScreenManager

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

        self.game_gui = GameGui()

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
        self.game_gui.update(dt)

    def handle_player_actions(self, player_actions: list[ActionEnum]):
        if ActionEnum.DASH in player_actions:
            if not self.world.player.dashing:
                self.world.player.dash()
        if ActionEnum.ATTACK in player_actions:
            if self.world.player.alive and not self.world.player.attacking:
                wx, wy = self.calculate_world_coordinates(*pygame.mouse.get_pos())
                direction = atan2(wy, wx)
                self.world.player.attack(direction)
                self.network.send(
                    builders.build_character_attacked(self.world.player, direction)
                )
                self.player_struct.sprite.change_animation("attack")
        if ActionEnum.PLAYER_HEAL in player_actions:
            self.world.player.handle_healing_received(1.0)
            logger.info("Player now has {} hp", self.world.player.hp)
        if ActionEnum.PLAYER_INVICIBILITY in player_actions:
            self.world.player.invincible = not self.world.player.invincible
            logger.info("Player invincibility set to {}", self.world.player.invincible)
        if ActionEnum.ZOOM_OUT in player_actions:
            self.screen_scale = max(3, self.screen_scale - 1)  # pylint: disable=fixme
            self.recalculate_screen_scale_derivatives()
        if ActionEnum.ZOOM_IN in player_actions:
            self.screen_scale = min(6, self.screen_scale + 1)  # pylint: disable=fixme
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
        self.game_gui.draw(self.world.player, dest_surface)

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
                character.position.x,  # pylint: disable=no-member
                character.position.y,  # pylint: disable=no-member
                sprite.image,
            )
            sprite.set_position(x - self.cam_x, y - self.cam_y)

        for character_struct in self.character_structs:
            character_struct.sprite_group.update(dt)

    def generate_projectile_renderables(self):
        for projectile in self.world.projectiles:
            image = load_projectile_image(projectile.attack_profile.image_path)
            blit_x, blit_y = self.calculate_draw_coordinates(
                projectile.x, projectile.y, image
            )
            bottom_y = blit_y - self.cam_y + image.get_height()
            yield BlittableRenderable(
                renderables_generate_key(self.world.map.get_1f_layer_id(), bottom_y),
                image,
                (blit_x - self.cam_x, blit_y - self.cam_y),
            )

    def generate_environment_renderables(self):
        for environment in self.world.zone.environment_features:
            tilemap = Map(environment.tmx_name)
            yield from self.generate_map_renderables(
                ground=False,
                tilemap=tilemap,
                tile_offset_y=environment.center_y - tilemap.height // 2,
                tile_offset_x=environment.center_x - tilemap.width // 2,
            )

    def generate_map_renderables(
        self, ground: bool, tilemap: Map, tile_offset_x: int = 0, tile_offset_y: int = 0
    ):
        """We can statically generate the blit coords once in the beginning,
        avoiding a bunch of coordinate conversions."""
        ground_ids = tilemap.get_ground_layer_ids()
        for layer in range(tilemap.get_tile_layer_count()):
            if layer not in ground_ids if ground else layer in ground_ids:
                continue
            x_offset, y_offset = tilemap.get_layer_offsets(layer)
            for x in range(0, tilemap.width):
                for y in range(0, tilemap.height):
                    blit_image = tilemap.get_tile_image(x, y, layer)
                    if blit_image:
                        blit_x, blit_y = self.calculate_draw_coordinates(
                            x + tile_offset_x, y + tile_offset_y, blit_image
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
    ) -> tuple[float, float]:
        cartesian_x = x * self.world.map.tile_width // 2
        cartesian_y = y * self.world.map.tile_width // 2
        iso_x, iso_y = cartesian_to_isometric(cartesian_x, cartesian_y)
        x = iso_x + self.camera_offset_x - image.get_width() // 2
        y = iso_y + self.camera_offset_y - image.get_height() // 2
        return (x, y)

    def calculate_world_coordinates(
        self,
        x: float,
        y: float,
    ) -> tuple[float, float]:
        cam_x = x - self.camera_offset_x * self.screen_scale
        cam_y = y - self.camera_offset_y * self.screen_scale
        tx = cam_x / self.world.map.tile_width // 2
        ty = cam_y / self.world.map.tile_width // 2
        return isometric_to_cartesian(tx, ty)

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
        self.ground_renderables = list(
            self.generate_map_renderables(ground=True, tilemap=self.world.map)
        )
        self.map_renderables = list(
            self.generate_map_renderables(ground=False, tilemap=self.world.map)
        )
        self.map_renderables.extend(list(self.generate_environment_renderables()))

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


@lru_cache
def load_projectile_image(image_path: str):
    path = f"{NK_DATA_ROOT}/projectiles/{image_path}.png"
    return pygame.image.load(path).convert_alpha()
