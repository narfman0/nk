from betterproto import serialized_on_wire
from loguru import logger
from nk_shared.proto import (
    CharacterAttacked,
    CharacterUpdated,
    Direction,
    Message,
    PlayerJoined,
    PlayerJoinResponse,
    PlayerLeft,
)

from nk.db import Character as DBCharacter
from nk.models import Player, WorldComponentProvider


class MessageComponent:
    def __init__(self, world: WorldComponentProvider):
        self.world = world

    async def handle_message(self, player: Player, msg: Message):
        """Socket-level handler for messages, mostly passing through to world"""
        if serialized_on_wire(msg.player_join_request):
            await self.handle_player_join_request(player)
        elif serialized_on_wire(msg.text_message):
            self.world.broadcast(msg, player)
        elif serialized_on_wire(msg.character_attacked):
            self.handle_character_attacked(msg.character_attacked)
        elif serialized_on_wire(msg.character_updated):
            self.handle_character_updated(msg.character_updated)
            self.world.broadcast(msg, player)

    def handle_character_attacked(self, details: CharacterAttacked):
        """Call character attack, does nothing if character does not exist"""
        character = self.world.get_character_by_uuid(details.uuid)
        if not character:
            logger.warning("No character maching uuid: {}", details.uuid)
        logger.info(details)
        character.attack(details.direction)

    def handle_character_updated(self, details: CharacterUpdated):
        """Apply message details to relevant character. If character
        does not exist, do not do anything."""
        character = self.world.get_character_by_uuid(details.uuid)
        if not character:
            logger.warning("No character maching uuid: {}", details.uuid)
        character.body.position = (details.x, details.y)
        character.moving_direction = Direction(details.moving_direction)
        character.facing_direction = Direction(details.facing_direction)
        character.body.velocity = (details.dx, details.dy)

    async def spawn_player(self, player: Player) -> Player:
        """Player 'is' a Character, which i don't love, but its already
        created. Update relevant attrs."""
        character = await DBCharacter.find_one(DBCharacter.user_id == player.uuid)
        if character:
            x, y = character.x, character.y
        else:
            x, y = self.world.get_start_tile()
        player.body.position = (x, y)
        self.world.space.add(player.body, player.shape, player.hitbox_shape)
        self.world.get_players().append(player)
        return player

    async def handle_player_disconnected(self, player: Player):
        self.world.broadcast(Message(player_left=PlayerLeft(uuid=player.uuid)), player)
        x, y = player.position.x, player.position.y  # pylint: disable=no-member
        character = await DBCharacter.find_one(DBCharacter.user_id == player.uuid)
        if character:
            await character.set({DBCharacter.x: x, DBCharacter.y: y})
        else:
            await DBCharacter(user_id=player.uuid, x=x, y=y).insert()
        logger.info("Successfully saved player post-logout")
        self.world.get_players().remove(player)

    async def handle_player_join_request(self, player: Player):
        """A player has joined. Handle initialization."""
        await self.spawn_player(player)
        logger.info("Join request success: {}", player.uuid)
        x, y = player.position.x, player.position.y
        response = PlayerJoinResponse(uuid=player.uuid, x=x, y=y)
        await player.messages.put(Message(player_join_response=response))
        self.world.broadcast(
            Message(player_joined=PlayerJoined(uuid=player.uuid)), player
        )
