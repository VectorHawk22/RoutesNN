import pygame
import sys
import os
import json

from game_logic import ClickerGame
from gui import get_font, strip_emoji, render_text, Dialog
from gui.game import GameScreen
from gui.settings import SettingsScreen
from gui.inventory import InventoryScreen
from gui.shop import ShopScreen
from gui.authors import AuthorsScreen
from translations import TRANSLATIONS

WIDTH = 600
HEIGHT = 490
BACK_BTN_RECT = (20, 440, 560, 40)


class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Basketball Click")

        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "animation", "icon.jpg")
        if os.path.exists(icon_path):
            try:
                icon = pygame.image.load(icon_path)
                pygame.display.set_icon(icon)
            except Exception:
                pass

        self.clock = pygame.time.Clock()
        self.running = True
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.settings = self._load_settings()
        self.game = ClickerGame()
        self.current_lang = self.settings.get("language", "Русский")
        self.translations = TRANSLATIONS

        self.dialog = Dialog()

        self.current_screen = "game"
        self.screens = {
            "game": GameScreen(self),
            "settings": None,
            "inventory": None,
            "shop": ShopScreen(self),
            "authors": AuthorsScreen(self),
        }

        self.back_btn_rect = pygame.Rect(*BACK_BTN_RECT)

        self._set_icon_caption()

    def _set_icon_caption(self):
        tr = self.translations.get(self.current_lang, TRANSLATIONS["Русский"])
        pygame.display.set_caption(strip_emoji(tr["title"]))

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.on_closing()
                    return

                if self.dialog.active:
                    self.dialog.handle_event(event)
                    continue

                if self.current_screen != "game":
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self.back_btn_rect.collidepoint(event.pos):
                            self.switch_screen("game")
                            continue

                self.screens[self.current_screen].handle_event(event)

            self.screens[self.current_screen].update()

            self.screen.fill((240, 240, 240))
            self.screens[self.current_screen].draw(self.screen)

            if self.current_screen != "game":
                self._draw_back_button()

            if self.dialog.active:
                self.dialog.draw(self.screen)

            self._draw_glitch_label()

            pygame.display.flip()
            self.clock.tick(60)

    def switch_screen(self, name):
        if name != "game":
            if name == "settings":
                self.screens["settings"] = SettingsScreen(self)
            elif name == "inventory":
                self.screens["inventory"] = InventoryScreen(self)
            elif name == "shop":
                self.screens["shop"] = ShopScreen(self)
        self.current_screen = name

    def set_language(self, lang):
        self.current_lang = lang
        self.settings["language"] = lang
        self.save_settings()
        self._set_icon_caption()
        if "game" in self.screens and self.screens["game"]:
            self.screens["game"].set_language()

    def apply_skins(self):
        if "game" in self.screens and self.screens["game"]:
            self.screens["game"].apply_skins()

    def _draw_back_button(self):
        tr = self.translations.get(self.current_lang, TRANSLATIONS["Русский"])
        mouse_over = self.back_btn_rect.collidepoint(pygame.mouse.get_pos())
        color = (200, 220, 255) if mouse_over else (173, 216, 230)
        pygame.draw.rect(self.screen, color, self.back_btn_rect, border_radius=8)
        pygame.draw.rect(self.screen, (100, 100, 100), self.back_btn_rect, 1, border_radius=8)
        font = get_font(14, bold=True)
        txt = strip_emoji(tr["back"])
        txt_surf = font.render(txt, True, (0, 0, 0))
        self.screen.blit(txt_surf, (self.back_btn_rect.centerx - txt_surf.get_width() // 2,
                                    self.back_btn_rect.centery - txt_surf.get_height() // 2))

    def _draw_glitch_label(self):
        font = get_font(10)
        txt = font.render("GlitchHunters", True, (0, 0, 200))
        self.screen.blit(txt, (10, HEIGHT - 25))

    def on_closing(self):
        self.game.save_game()
        self.save_settings()
        self.running = False
        pygame.quit()

    def _load_settings(self):
        settings_file = os.path.join(self.base_dir, "settings.json")
        defaults = {
            "sound": True, "language": "Русский",
            "skin_ball": "ball1.png", "skin_basket": "basket.png",
            "inventory_balls": ["ball1.png"], "inventory_baskets": ["basket.png"]
        }
        if not os.path.exists(settings_file):
            try:
                with open(settings_file, "w", encoding="utf-8") as f:
                    json.dump(defaults, f, ensure_ascii=False, indent=4)
            except Exception:
                pass
            return dict(defaults)
        try:
            with open(settings_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            defaults.update(data)
            return defaults
        except Exception:
            return dict(defaults)

    def save_settings(self):
        settings_file = os.path.join(self.base_dir, "settings.json")
        try:
            with open(settings_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=4)
        except Exception:
            pass


def main():
    app = App()
    app.run()


if __name__ == "__main__":
    main()
