from nk.game.models.character import Character
from nk.game.models.direction import Direction


class NPC(Character):
    body_removal_processed: bool = False

    def ai(self, dt: float, player: Character):
        if not self.alive:
            return
        self.movement_direction = None
        if not player.alive:
            return
        # TODO update ai movement direction
        # player_dst_sqrd = self.position.get_dist_sqrd(player.position)
        # self.movement_direction = Direction.direction_to(
        #     self.position, player.position
        # )
