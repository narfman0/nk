from nk_shared import proto
from nk_shared.models import Character


def build_player_disconnected(uuid: str) -> proto.Message:
    return proto.Message(player_disconnected=proto.PlayerDisconnected(uuid=uuid))


def build_player_respawned(character: Character) -> proto.Message:
    return proto.Message(
        player_respawned=proto.PlayerRespawned(
            uuid=character.uuid,
            x=character.position.x,
            y=character.position.y,
        ),
    )
