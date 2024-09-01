from sortedcontainers import SortedKeyList

from nk.ui.game.renderables.models import Renderable


def renderables_key(a: Renderable):
    return a.key


def renderables_generate_key(y_offset: int, bottom_y: float):
    return (-y_offset << 16) + int(bottom_y)


def create_renderable_list():
    return SortedKeyList(key=renderables_key)
