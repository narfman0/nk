from typing import Protocol

import pygame
from loguru import logger
from nk_shared import builders
from nk_shared.proto import CharacterType

from nk.net.network import Network


class TerminalProtocol(Protocol):
    def calculate_world_coordinates(
        self, x: float, y: float
    ) -> tuple[float, float]: ...
    def calculate_absolute_world_coordinates(
        self, x: float, y: float
    ) -> tuple[float, float]: ...


class Terminal:
    def __init__(self, network: Network, protocol: TerminalProtocol):
        self.network = network
        self.protocol = protocol
        self.terminal_text: str | None = None

    def update(self, events: list[pygame.Event]) -> bool:
        if self.terminal_text is None:
            return False
        for event in events:
            if event.type == pygame.KEYDOWN:  # pylint: disable=no-member
                if event.key == pygame.K_RETURN:  # pylint: disable=no-member
                    self.handle_command(self.terminal_text)
                    self.terminal_text = None
                elif event.key == pygame.K_BACKSPACE:  # pylint: disable=no-member
                    self.terminal_text = self.terminal_text[:-1]
                else:
                    self.terminal_text += event.unicode
        return True

    def handle_command(self, command: str):
        logger.info("Terminal command: {}", command)
        if not command.startswith("/"):
            self.network.send(builders.build_text_message(command))
        command_parts = command[1:].split(" ")
        try:
            if command_parts[0] == "spawn":
                count, character_type = parse_spawn_command(command_parts)
                x, y = self.protocol.calculate_absolute_world_coordinates(
                    *pygame.mouse.get_pos()
                )
                msg = builders.build_spawn_requested(
                    x=x,
                    y=y,
                    count=count,
                    character_type=character_type,
                )
                logger.info("Sending spawn request: {}", msg.spawn_requested)
                self.network.send(msg)
        except Exception as e:  # pylint: disable=broad-except
            logger.warning(f"Error parsing terminal command: {command}, {e}")

    def activate(self):
        self.terminal_text = ""


def parse_spawn_command(command_parts: list[str]) -> tuple[int, CharacterType]:
    count = 10
    character_type = CharacterType.CHARACTER_TYPE_DROID_ASSASSIN
    if len(command_parts) > 1:
        count = int(command_parts[1])
    if len(command_parts) > 2:
        try:
            character_type = CharacterType(int(command_parts[2]))
        except Exception:  # pylint: disable=broad-except
            pass
    return count, character_type
