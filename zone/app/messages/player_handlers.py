from beanie import PydanticObjectId
from betterproto import serialized_on_wire
from loguru import logger
from nk_shared import builders
from nk_shared.proto import (
    Message,
    PlayerConnected,
    PlayerDisconnected,
    PlayerJoined,
    PlayerJoinResponse,
    PlayerLeft,
)

from app.db import Character as DBCharacter
from app.messages.models import BaseMessageHandler
from app.models import Player, WorldInterface


class PlayerMessageHandler(BaseMessageHandler):
    def __init__(self, world: WorldInterface):
        self.world = world

    async def handle_message(self, msg: Message) -> bool:
        if serialized_on_wire(msg.player_connected):
            await handle_player_connected(self.world, msg.player_connected)
        elif serialized_on_wire(msg.player_disconnected):
            await handle_player_disconnected(self.world, msg.player_disconnected)
        else:
            return False
        return True


async def handle_player_disconnected(
    world: WorldInterface, details: PlayerDisconnected
):
    player = world.get_character_by_uuid(details.uuid)
    await world.publish(Message(player_left=PlayerLeft(uuid=details.uuid)))
    if player is None:
        return
    x, y = player.position.x, player.position.y  # pylint: disable=no-member
    user_id = PydanticObjectId(details.uuid)
    character = await DBCharacter.find_one(DBCharacter.user_id == user_id)
    if character:
        await character.set({DBCharacter.x: x, DBCharacter.y: y})
    else:
        await DBCharacter(user_id=user_id, x=x, y=y).insert()
    world.players.remove(player)


async def handle_player_connected(world: WorldInterface, details: PlayerConnected):
    """A player has joined. Handle initialization."""
    logger.info("Player joined: {}", details.uuid)
    player = await spawn_player(world, details.uuid)
    # pylint: disable-next=no-member
    x, y = player.position.x, player.position.y
    response = PlayerJoinResponse(uuid=player.uuid, x=x, y=y)
    await world.publish(
        Message(player_join_response=response, destination_uuid=player.uuid),
        channel=f"player-{player.uuid}",
    )
    await send_player_full_character_updates(world, player.uuid)
    await world.publish(
        Message(player_join_response=response, destination_uuid=player.uuid),
        channel=f"player-{player.uuid}",
    )
    await world.publish(Message(player_joined=PlayerJoined(uuid=player.uuid)))


async def spawn_player(world: WorldInterface, player_uuid: str) -> Player:
    """Player 'is' a Character, which i don't love, but its already
    created. Update relevant attrs."""
    character = await DBCharacter.find_one(
        DBCharacter.user_id == PydanticObjectId(player_uuid)
    )
    if character:
        x, y = character.x, character.y
    else:
        x, y = world.map.get_start_tile()
    player = Player(user_id=player_uuid, start_x=x, start_y=y)
    world.space.add(player.body, player.shape, player.hitbox_shape)
    world.players.append(player)
    return player


async def send_player_full_character_updates(world: WorldInterface, player_uuid: str):
    for character in world.enemies + world.players:
        if character.uuid == player_uuid:
            continue
        proto = builders.build_character_updated(character)
        await world.publish(proto, channel=f"player-{player_uuid}")
