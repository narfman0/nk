from math import atan2

import pygame
from loguru import logger
from nk_shared import builders
from nk_shared.models.character import Character
from nk_shared.proto import Direction
from pygame import Surface
from pygame.event import Event

from nk.game.listeners import WorldListener
from nk.game_state import GameState
from nk.settings import HEIGHT, WIDTH
from nk.ui.game.camera import Camera
from nk.ui.game.character_sprite import CharacterSprite
from nk.ui.game.character_struct import (
    CharacterStruct,
    CharacterStructRemoveStruct,
    update_character_structs,
)
from nk.ui.game.character_struct import (
    update_position as update_character_sprite_position,
)
from nk.ui.game.gui import GameGui
from nk.ui.game.input import (
    ActionEnum,
    read_input_player_actions,
    read_input_player_move_direction,
)
from nk.ui.game.models import UIInterface
from nk.ui.game.renderables import (
    SpriteRenderable,
    create_renderable_list,
    renderables_generate_key,
)
from nk.ui.game.renderables_generator import (
    generate_environment_renderables,
    generate_map_renderables,
    generate_projectile_renderables,
)
from nk.ui.screen import Screen, ScreenManager
from nk.util.math import cartesian_to_isometric, isometric_to_cartesian

DEFAULT_SCREEN_SCALE = 5
TIME_TO_REMOVE = 5


# pylint: disable-next=too-many-instance-attributes
class GameScreen(Screen, UIInterface, WorldListener):
    """UI screen for game state"""

    def __init__(self, screen_manager: ScreenManager, game_state: GameState):
        super().__init__()
        self.screen_manager = screen_manager
        self.game_state = game_state
        self.world = game_state.world
        self.network = game_state.network
        self._camera = Camera(game_state.world, 0, 0)
        self.screen_scale = DEFAULT_SCREEN_SCALE
        self.recalculate_screen_scale_derivatives()
        self.game_state.character_msg_handler.listeners.append(self)
        self.world.listeners.append(self)
        player_sprite = CharacterSprite(self.world.player.character_type_short)
        self.player_struct = CharacterStruct(self.world.player, player_sprite)
        self.character_structs = {self.world.player.uuid: self.player_struct}
        self.character_struct_remove_queue: list[CharacterStructRemoveStruct] = []
        self.game_gui = GameGui()

    def update(self, dt: float, events: list[Event]):
        player_move_direction = self.update_input(events)
        self.world.update(dt, player_move_direction)
        self._camera.update()
        self.update_character_struct_remove_queue(dt)
        update_character_structs(dt, self.character_structs, self)
        self.game_state.update(dt)
        self.game_gui.update(dt)

    def update_input(self, events: list[Event]) -> Direction | None:
        player_actions = read_input_player_actions(events)
        self.handle_player_actions(player_actions)
        player_move_direction = read_input_player_move_direction()
        if player_move_direction:
            self.world.player.facing_direction = player_move_direction
        return player_move_direction

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
        if ActionEnum.RELOAD in player_actions:
            self.world.player.reload()
            self.network.send(builders.build_character_reloaded(self.world.player))
            logger.info("Player reloading")
        if ActionEnum.ZOOM_OUT in player_actions:
            self.change_screen_scale(-1)
        if ActionEnum.ZOOM_IN in player_actions:
            self.change_screen_scale(1)

    def change_screen_scale(self, difference: int):
        previous_screen_scale = self.screen_scale
        self.screen_scale = min(6, max(2, self.screen_scale + difference))
        if previous_screen_scale != self.screen_scale:
            self.recalculate_screen_scale_derivatives()

    def draw(self, dest_surface: Surface):  # pylint: disable=arguments-renamed
        curtime = pygame.time.get_ticks()
        renderables = self.map_renderables.copy()
        for renderable in generate_projectile_renderables(self.world, self):
            renderables.add(renderable)
        for character_struct in self.character_structs.values():
            if not self.camera.is_visible(
                character_struct.sprite.rect.centerx + self._camera.x,
                character_struct.sprite.rect.centery + self._camera.y,
            ):
                continue
            img_height = character_struct.sprite.image.get_height()
            bottom_y = (
                character_struct.sprite.rect.top + img_height // 2 + self._camera.y
            )
            key = renderables_generate_key(self.world.map.get_1f_layer_id(), bottom_y)
            renderables.add(SpriteRenderable(key, character_struct.sprite_group))

        surface = Surface(size=(self.screen_width, self.screen_height))
        for ground_renderable in self.ground_renderables:
            blit_x, blit_y = ground_renderable.blit_coords
            if not self.camera.is_visible(blit_x, blit_y):
                continue
            blit_coords = (blit_x - self._camera.x, blit_y - self._camera.y)
            surface.blit(ground_renderable.blit_image, blit_coords)

        for renderable in renderables:
            renderable.draw(surface, self._camera)

        endtime = pygame.time.get_ticks()
        pygame.transform.scale_by(
            surface, dest_surface=dest_surface, factor=self.screen_scale
        )
        self.game_gui.draw(
            self.world.player,
            dest_surface,
            len(renderables),
            endtime - curtime,
        )

    def recalculate_screen_scale_derivatives(self):
        self.screen_width = WIDTH // self.screen_scale
        self.screen_height = HEIGHT // self.screen_scale
        self.camera_offset_x = self.screen_width // 2
        self.camera_offset_y = self.screen_height // 2
        self.camera.update_screen_width_height(self.screen_width, self.screen_height)
        self.ground_renderables = list(
            generate_map_renderables(self, ground=True, tilemap=self.world.map)
        )
        self.map_renderables = create_renderable_list()
        self.map_renderables += list(
            generate_map_renderables(self, ground=False, tilemap=self.world.map)
        )
        self.map_renderables += list(
            generate_environment_renderables(self, self.world.zone.environment_features)
        )

    def calculate_draw_coordinates(
        self, x: float, y: float, image: Surface
    ) -> tuple[float, float]:
        x *= self.world.map.tile_width // 2
        y *= self.world.map.tile_width // 2
        iso_x, iso_y = cartesian_to_isometric(x, y)
        x = iso_x + self.camera_offset_x - image.get_width() // 2
        y = iso_y + self.camera_offset_y - image.get_height() // 2
        return (x, y)

    def calculate_world_coordinates(self, x: float, y: float) -> tuple[float, float]:
        x -= self.camera_offset_x * self.screen_scale
        y -= self.camera_offset_y * self.screen_scale
        return isometric_to_cartesian(
            x / self.world.map.tile_width // 2,
            y / self.world.map.tile_width // 2,
        )

    def character_attacked(self, character: Character):
        struct = self.character_structs.get(character.uuid)
        if struct:
            struct.sprite.change_animation("attack")

    def character_added(self, character: Character):
        sprite = CharacterSprite(character.character_type_short)
        update_character_sprite_position(character, sprite, self)
        self.character_structs[character.uuid] = CharacterStruct(character, sprite)

    def character_removed(self, character: Character):
        struct = self.character_structs.get(character.uuid)
        if struct:
            remove_struct = CharacterStructRemoveStruct(struct, TIME_TO_REMOVE)
            self.character_struct_remove_queue.append(remove_struct)

    def update_character_struct_remove_queue(self, dt: float):
        for struct in list(self.character_struct_remove_queue):
            struct.time_until_removal -= dt
            if struct.time_until_removal <= 0:
                self.character_structs.pop(struct.character_struct.character.uuid, None)
                self.character_struct_remove_queue.remove(struct)

    @property
    def camera(self):
        return self._camera
