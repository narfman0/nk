from beanie import PydanticObjectId
from betterproto import serialized_on_wire
from loguru import logger
from nk_shared.proto import (
    CharacterAttacked,
    CharacterUpdated,
    Direction,
    Message,
    PlayerConnected,
    PlayerDisconnected,
    PlayerJoined,
    PlayerJoinResponse,
    PlayerLeft,
)

from app.db import Character as DBCharacter
from app.models import Player, WorldComponentProvider


class UnknownCharacterError(Exception):
    pass


class MessageBus:
    def __init__(self, world: WorldComponentProvider):
        self.world = world

    async def handle_message(self, msg: Message):
        """Socket-level handler for messages, mostly passing through to world"""
        if serialized_on_wire(msg.player_connected):
            await self.handle_player_connected(msg.player_connected)
        elif serialized_on_wire(msg.text_message):
            await self.world.publish(msg)
        elif serialized_on_wire(msg.character_attacked):
            self.handle_character_attacked(msg.character_attacked)
        elif serialized_on_wire(msg.player_disconnected):
            await self.handle_player_disconnected(msg.player_disconnected)
        elif serialized_on_wire(msg.character_updated):
            self.handle_character_updated(msg.character_updated)
            await self.world.publish(msg)

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
            raise UnknownCharacterError(details.uuid)
        character.body.position = (details.x, details.y)
        character.moving_direction = Direction(details.moving_direction)
        character.facing_direction = Direction(details.facing_direction)
        character.body.velocity = (details.dx, details.dy)

    async def handle_player_disconnected(self, details: PlayerDisconnected):
        player = self.world.get_character_by_uuid(details.uuid)
        await self.world.publish(Message(player_left=PlayerLeft(uuid=details.uuid)))
        x, y = player.position.x, player.position.y  # pylint: disable=no-member
        user_id = PydanticObjectId(details.uuid)
        character = await DBCharacter.find_one(DBCharacter.user_id == user_id)
        if character:
            await character.set({DBCharacter.x: x, DBCharacter.y: y})
        else:
            await DBCharacter(user_id=user_id, x=x, y=y).insert()
        self.world.players.remove(player)

    async def handle_player_connected(self, details: PlayerConnected):
        """A player has joined. Handle initialization."""
        player = Player(user_id=details.uuid)
        logger.info("Player joined: {}", player)
        await self.spawn_player(player)
        # pylint: disable-next=no-member
        x, y = player.position.x, player.position.y
        response = PlayerJoinResponse(uuid=player.uuid, x=x, y=y)
        await self.world.publish(
            Message(player_join_response=response, destination_uuid=player.uuid),
            channel=f"player-{player.uuid}",
        )
        await self.world.publish(Message(player_joined=PlayerJoined(uuid=player.uuid)))

    async def spawn_player(self, player: Player) -> Player:
        """Player 'is' a Character, which i don't love, but its already
        created. Update relevant attrs."""
        character = await DBCharacter.find_one(
            DBCharacter.user_id == PydanticObjectId(player.uuid)
        )
        if character:
            x, y = character.x, character.y
        else:
            x, y = self.world.map.get_start_tile()
        player.body.position = (x, y)
        self.world.space.add(player.body, player.shape, player.hitbox_shape)
        self.world.players.append(player)
        return player
