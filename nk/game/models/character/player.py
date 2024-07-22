from nk.game.models.character import Character

SWAP_DURATION = 0.1


class Player(Character):
    swapping: bool = False
    swap_time_remaining: float = 0
    swap_character_type: str = None

    def update(self, dt: float):
        super().update(dt)
        if self.alive and self.swapping:
            self.swap_time_remaining -= dt
            if self.swap_time_remaining <= 0:
                self.swap_time_remaining = 0
                self.swapping = False
                self.character_type = self.swap_character_type
                self.swap_character_type = None
                self.apply_character_properties()

    def swap(self):
        if not self.alive or self.swapping:
            return
        if self.character_type == "pigsassin":
            self.swap_character_type = "droid_assassin"
        elif self.character_type == "droid_assassin":
            self.swap_character_type = "pigsassin"
        else:
            print(f"Unknown character type {self.character_type}")
        self.swap_time_remaining = SWAP_DURATION
        self.swapping = True

    def dash(self):
        if not self.swapping:
            super().dash()
