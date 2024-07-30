import pygame
import yaml

from nk_shared.proto import Direction


class CharacterSprite(pygame.sprite.Sprite):
    FRAME_DURATION = 0.1

    def __init__(self, sprite_name: str, scale: float = 1, offset=(0, 0)):
        super(CharacterSprite, self).__init__()
        self.index = 0
        self.moving = False
        self.loop = True
        self.sprite_name = sprite_name
        self.offset = offset
        self.active_animation_name = "idle"
        self.direction = Direction.DIRECTION_S
        self.current_frame_time_remaining = self.FRAME_DURATION

        with open(f"../data/characters/{sprite_name}/animations.yml") as f:
            animations_yml = yaml.safe_load(f)

        path_to_nonflipped_image: dict[str, pygame.Surface] = {}
        path_to_flipped_image: dict[str, pygame.Surface] = {}
        self.images: dict[dict[list[pygame.Surface]]] = {}
        for animation_name, direction_list_path_map in animations_yml.items():
            self.images[animation_name] = {}
            for direction_str, animation_struct in direction_list_path_map.items():
                direction = Direction[f"DIRECTION_{direction_str}"]
                animation_direction_images = []
                for image_path in animation_struct["images"]:
                    path = f"../data/characters/{sprite_name}/images/{image_path}"
                    flipped = animation_struct.get("flipped")
                    if flipped:
                        path_image_map = path_to_flipped_image
                    else:
                        path_image_map = path_to_nonflipped_image
                    if path in path_image_map:
                        image = path_image_map[path]
                    else:
                        image = pygame.image.load(path).convert_alpha()
                        if scale != 1:
                            width, height = image.get_size()
                            image = pygame.transform.scale(
                                image, (int(width * scale), int(height * scale))
                            )
                        if flipped:
                            image = pygame.transform.flip(
                                image, flip_x=True, flip_y=False
                            )
                        path_image_map[path] = image
                    animation_direction_images.append(image)
                self.images[animation_name][direction] = animation_direction_images
            # let's make it easy to make animation yml, and allow ourselves just to define once for east.
            for direction in [
                Direction.DIRECTION_N,
                Direction.DIRECTION_NE,
                Direction.DIRECTION_SE,
            ]:
                if direction not in self.images[animation_name]:
                    self.images[animation_name][direction] = self.images[
                        animation_name
                    ][Direction.DIRECTION_E]
            if Direction.DIRECTION_W not in self.images[animation_name]:
                east_images = list(self.images[animation_name][Direction.DIRECTION_E])
                west_images = [
                    pygame.transform.flip(img, flip_x=True, flip_y=False)
                    for img in east_images
                ]
                for direction in [
                    Direction.DIRECTION_S,
                    Direction.DIRECTION_SW,
                    Direction.DIRECTION_W,
                    Direction.DIRECTION_NW,
                ]:
                    if direction not in self.images[animation_name]:
                        self.images[animation_name][direction] = west_images

        self.image = self.active_images[self.index]
        width, height = self.image.get_size()
        self.rect = pygame.Rect(0, 0, width, height)

    def move(self, direction):
        self.moving = True
        self.direction = direction
        self.index = 0

    def stop(self):
        self.moving = False
        self.index = 0

    def change_animation(self, animation_name: str, loop: bool = True):
        self.loop = loop
        if self.active_animation_name == animation_name:
            return
        self.index = 0
        self.active_animation_name = animation_name
        self.current_frame_time_remaining = self.FRAME_DURATION

    def update(self, dt: float):
        self.current_frame_time_remaining -= dt
        while self.current_frame_time_remaining <= 0:
            self.current_frame_time_remaining += self.FRAME_DURATION
            self.index += 1
            if self.index >= len(self.active_images):
                if self.loop:
                    self.index = 0
                else:
                    self.index = len(self.active_images) - 1
        self.image = self.active_images[self.index]

    def set_position(self, x, y):
        self.rect.left = x + self.offset[0]
        self.rect.top = y + self.offset[1]

    @property
    def active_images(self) -> list[pygame.Surface]:
        return self.images[self.active_animation_name][self.direction]
