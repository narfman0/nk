import os
from pygame import Event, Rect
import pygame_gui

from nk.game_state import GameState
from nk.settings import WIDTH, HEIGHT
from nk.ui.load_screen import LoadScreen
from nk.ui.screen import Screen, ScreenManager

ELEMENT_WIDTH = 256


class LoginScreen(Screen):
    def __init__(self, screen_manager: ScreenManager):
        super().__init__()
        self.screen_manager = screen_manager
        self.game_state = GameState()
        self.manager = pygame_gui.UIManager((WIDTH, HEIGHT))
        self.init_ui()

    def init_ui(self):
        top, left = HEIGHT // 2 - 64, WIDTH // 2 - ELEMENT_WIDTH // 2
        width_height = (ELEMENT_WIDTH, 50)
        pygame_gui.elements.UILabel(
            relative_rect=Rect((left, top), width_height),
            text="Email",
            manager=self.manager,
        )
        top += 64
        self.email_field = pygame_gui.elements.UITextEntryLine(
            relative_rect=Rect((left, top), width_height),
            manager=self.manager,
            placeholder_text="email",
        )
        top += 64
        pygame_gui.elements.UILabel(
            relative_rect=Rect((left, top), width_height),
            text="Password",
            manager=self.manager,
        )
        top += 64
        self.password_field = pygame_gui.elements.UITextEntryLine(
            relative_rect=Rect((left, top), width_height),
            manager=self.manager,
            placeholder_text="password",
        )
        self.password_field.set_text_hidden(True)
        top += 64
        self.login_button = pygame_gui.elements.UIButton(
            relative_rect=Rect((left, top), width_height),
            text="Login",
            manager=self.manager,
        )
        self.load_login()

    def draw(self, surface):
        self.manager.draw_ui(surface)

    def update(self, dt: float, events: list[Event]):
        super().update(dt, events)
        for event in events:
            self.manager.process_events(event)
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.login_button:
                    self.save_login()
                    self.screen_manager.pop()
                    self.screen_manager.push(
                        LoadScreen(
                            self.screen_manager,
                            self.game_state,
                            self.email_field.get_text(),
                            self.password_field.get_text(),
                        )
                    )
        self.manager.update(dt)

    def load_login(self):
        os.makedirs(self.save_root(), exist_ok=True)
        path = os.path.expanduser(os.path.join(self.save_root(), "login.txt"))
        try:
            with open(path) as login_file:
                email, passw = login_file.readlines()
                self.email_field.set_text(email.strip())
                self.password_field.set_text(passw.strip())
        except OSError:
            pass  # failed to open file, nothing saved, who cares

    def save_login(self):
        os.makedirs(self.save_root(), exist_ok=True)
        path = os.path.expanduser(os.path.join(self.save_root(), "login.txt"))
        lines = [self.email_field.get_text() + "\n", self.password_field.get_text()]
        with open(path, "w+") as login_file:
            login_file.writelines(lines)

    def save_root(self) -> str:
        return os.path.expanduser("~/.nk")
