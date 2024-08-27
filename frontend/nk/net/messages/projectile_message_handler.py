from nk_shared.proto import Message

from nk.game.world import World


class ProjectileMessageHandler:
    def __init__(self, world: World):
        self.world = world

    def handle_projectile_created(self, message: Message):
        if message.projectile_created.origin_uuid == self.world.player.uuid:
            return
        self.world.projectile_manager.create_projectile(message.projectile_created)

    def handle_projectile_destroyed(self, message: Message):
        details = message.projectile_destroyed
        projectile = self.world.projectile_manager.get_projectile_by_uuid(details.uuid)
        if projectile:
            self.world.projectile_manager.projectiles.remove(projectile)
