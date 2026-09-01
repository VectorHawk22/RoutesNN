# -*- coding: utf-8 -*-
"""Kivy entry point for Basketball Click (pygame port).

A virtual 600x490 board is rendered through a Scatter that letterboxes it into
the real window while preserving aspect ratio. All game screens are Kivy
Widgets of size 600x490 living inside a RelativeLayout child of the Scatter, so
native controls are transformed together with the board. Dynamic content
(court, grids, counters) is drawn with the immediate-mode Painter into a
cleared canvas InstructionGroup every frame. A modal dialog and the back button
are drawn into a separate overlay canvas on top.
"""
import os
import json
from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.graphics import Color, Rectangle, InstructionGroup
from kivy.graphics.transformation import Matrix
from kivy.core.window import Window
from kivy.uix.scatter import Scatter
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget

from game_logic import ClickerGame
from gui.utils import strip_emoji, register_fonts
from gui.painter import Painter, BOARD_W, BOARD_H
from gui.dialog import Dialog
from gui.game import GameScreen
from gui.settings import SettingsScreen
from gui.inventory import InventoryScreen
from gui.shop import ShopScreen
from gui.authors import AuthorsScreen
from translations import TRANSLATIONS

Config.set("graphics", "resizable", "0")
Config.set("graphics", "width", str(BOARD_W))
Config.set("graphics", "height", str(BOARD_H))

BACK_BTN_RECT = (20, 440, 560, 40)


class BoardView(Scatter):
    """Letterboxes the 600x490 board into the window and keeps touch-to-local
    and drawing in sync by exposing the board position/scale to the app."""

    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.do_translation_x = False
        self.do_translation_y = False
        self.do_rotation = False
        self.do_scale = False
        self.scale_min = 1.0
        self.scale_max = 1.0
        self.size_hint = (None, None)

    def on_size(self, *args):
        if self.app:
            self.app.rebuild_board_layout()

    def on_parent(self, *args):
        if self.app and self.parent:
            self.app.rebuild_board_layout()


class GameRoot(RelativeLayout):
    """Contains the board and the letterbox backdrop. Owns touch dispatch:
    Kivy sends touches to this root widget, which forwards them to the app's
    board-coordinate handlers."""

    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self._bg = InstructionGroup()
        self.canvas.before.add(self._bg)

    def draw_backdrop(self, color=(0, 0, 0)):
        self._bg.clear()
        self._bg.add(Color(*[c / 255.0 for c in color]))
        self._bg.add(Rectangle(pos=self.pos, size=self.size))

    def _locals(self, touch):
        x, y = self.app.to_local(touch.pos)
        if 0 <= x <= BOARD_W and 0 <= y <= BOARD_H:
            return x, y
        return None

    def on_touch_down(self, touch):
        self.app.hover_pos = touch.pos
        # Capture board coords BEFORE super() may mutate touch.pos via
        # apply_transform_2d during native-child dispatch.
        board = self._locals(touch)
        if self.app.dialog.active:
            if board is not None:
                self.app.dialog.touch_down(*board)
            return True
        # Native children (buttons, dropdown, checkbox, text input) first.
        if super().on_touch_down(touch):
            return True
        if board is None:
            return False
        return self.app.board_touch_down(*board, touch)

    def on_touch_move(self, touch):
        self.app.hover_pos = touch.pos
        if self.app.consume_dialog_touch("move"):
            return True
        board = self._locals(touch)
        if super().on_touch_move(touch):
            return True
        if board is None:
            return False
        return self.app.board_touch_move(*board, touch)

    def on_touch_up(self, touch):
        if self.app.consume_dialog_touch("up"):
            return True
        board = self._locals(touch)
        if super().on_touch_up(touch):
            return True
        if board is None:
            return False
        return self.app.board_touch_up(*board, touch)


class ClickerApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        register_fonts()
        self.settings = self._load_settings()
        self.game = ClickerGame()
        self.current_lang = self.settings.get("language", "Русский")
        self.translations = TRANSLATIONS
        self.hover_pos = None

        self.root = None
        self.board = None
        self.screens_layer = None
        self.dialog = Dialog()
        self.overlay = None
        self.overlay_frame = None
        self.screens = {}
        self.current_screen = "game"
        self.letterbox_offset = (0, 0)
        self.letterbox_scale = 1.0

    # -- app ------------------------------------------------------------
    def build(self):
        self.root = GameRoot(self)
        self.board = BoardView(self)
        self.screens_layer = RelativeLayout(size=(BOARD_W, BOARD_H),
                                            size_hint=(None, None))
        self.board.add_widget(self.screens_layer)
        self.root.add_widget(self.board)

        self.overlay = Widget(size=(BOARD_W, BOARD_H), size_hint=(None, None))
        self.screens_layer.add_widget(self.overlay)
        self.overlay_frame = InstructionGroup()
        self.overlay.canvas.add(self.overlay_frame)

        self._build_screens()
        self._switch_screen(self.current_screen)
        return self.root

    def on_start(self):
        self.clock_event = Clock.schedule_interval(self._tick, 1.0 / 60.0)
        self.autosave_event = Clock.schedule_interval(self._autosave, 5.0)
        Window.bind(on_resize=self._on_resize)
        Window.bind(on_key_down=self._on_keyboard)
        self.rebuild_board_layout()
        self.root.draw_backdrop()

    def on_stop(self):
        for ev in (getattr(self, "clock_event", None),
                   getattr(self, "autosave_event", None)):
            if ev:
                try:
                    ev.cancel()
                except Exception:
                    pass
        self.save_settings()

    def _on_resize(self, *args):
        if self.root:
            self.root.draw_backdrop()
            self.rebuild_board_layout()

    def on_touch_move(self, touch):
        self.hover_pos = touch.pos
        return super().on_touch_move(touch)

    # -- per-frame redraw ----------------------------------------------
    def _tick(self, dt):
        if self.root is None:
            return
        scr = self.screens.get(self.current_screen)
        if scr is None:
            return
        scr.update()
        scr.clear()
        painter = Painter(scr.frame)
        # Match the pygame reference: fill a light-gray board background so
        # dark text/drawings are visible instead of the Kivy window's black.
        painter.rect(0, 0, BOARD_W, BOARD_H, (240, 240, 240))
        scr.draw(painter)

        self.overlay_frame.clear()
        opainter = Painter(self.overlay_frame)
        if self.current_screen != "game":
            self._draw_back_button(opainter)
        self._draw_glitch_label(opainter)
        if self.dialog.active:
            self.dialog.draw(opainter)

    def _autosave(self, dt):
        try:
            self.save_settings()
        except Exception:
            pass

    # -- board layout ---------------------------------------------------
    def rebuild_board_layout(self):
        if self.root is None or self.board is None:
            return
        w, h = self.root.width, self.root.height
        if not w or not h:
            return
        scale = min(w / float(BOARD_W), h / float(BOARD_H))
        if scale <= 0:
            scale = 1.0
        bpx = (w - BOARD_W * scale) / 2.0
        bpy = (h - BOARD_H * scale) / 2.0

        mat = Matrix()
        mat = mat.scale(scale, scale, 1.0)
        mat = mat.translate(bpx / scale, bpy / scale, 0.0)
        self.board.transform = mat
        self.board.transform_inv = mat.inverse()
        self.board.pos = (0, 0)
        self.board.size = (BOARD_W, BOARD_H)
        self.letterbox_offset = (bpx, bpy)
        self.letterbox_scale = scale

        if self.screens_layer:
            self.screens_layer.pos = (0, 0)

    def to_local(self, screen_pos):
        """Convert a window (bottom-left) point to board top-left coords,
        inverting the Painter's y-flip (board_y = BOARD_H - window_y)."""
        px, py = self.letterbox_offset
        s = self.letterbox_scale
        bx = (screen_pos[0] - px) / s
        by = BOARD_H - ((screen_pos[1] - py) / s)
        return bx, by

    # -- screens --------------------------------------------------------
    def _build_screens(self):
        self.screens["game"] = GameScreen(self)
        self.screens["settings"] = SettingsScreen(self)
        self.screens["inventory"] = InventoryScreen(self)
        self.screens["shop"] = ShopScreen(self)
        self.screens["authors"] = AuthorsScreen(self)

    def _switch_screen(self, name):
        self.current_screen = name
        self.screens_layer.clear_widgets()
        self.screens_layer.add_widget(self.screens[name])
        self.screens_layer.add_widget(self.overlay)

    def switch_screen(self, name):
        if self.current_screen == name and name == "game":
            self.screens["game"]._reset_idle_timer()
            self._switch_screen("game")
            return
        if name == "game":
            self.screens["game"]._reset_idle_timer()
        self._switch_screen(name)
        self.screens[name].on_enter()

    # -- touch (board coordinates) -------------------------------------
    def consume_dialog_touch(self, kind):
        """The modal dialog swallows all board touches while active."""
        if not self.dialog.active:
            return False
        if kind in ("down", "move", "up"):
            return True
        return False

    def board_touch_down(self, x, y, touch):
        if self.dialog.active:
            self.dialog.touch_down(x, y)
            return True

        if self.current_screen != "game":
            bx, by, bw, bh = BACK_BTN_RECT
            if bx <= x <= bx + bw and by <= y <= by + bh:
                self.switch_screen("game")
                return True

        scr = self.screens.get(self.current_screen)
        if scr is not None and scr.touch_down(x, y):
            return True
        return False

    def board_touch_move(self, x, y, touch):
        scr = self.screens.get(self.current_screen)
        if scr is not None and scr.touch_move(x, y):
            return True
        return False

    def board_touch_up(self, x, y, touch):
        scr = self.screens.get(self.current_screen)
        if scr is not None and scr.touch_up(x, y):
            return True
        return False

    # -- helpers --------------------------------------------------------
    def _draw_back_button(self, painter):
        tr = self.translations.get(self.current_lang, TRANSLATIONS["Русский"])
        hover = False
        if self.hover_pos:
            lx, ly = self.to_local(self.hover_pos)
            bx, by, bw, bh = BACK_BTN_RECT
            hover = bx <= lx <= bx + bw and by <= ly <= by + bh
        color = (200, 220, 255) if hover else (173, 216, 230)
        painter.rounded(*BACK_BTN_RECT, color, radius=8)
        painter.outline(*BACK_BTN_RECT, (100, 100, 100))
        painter.text_centered_in(strip_emoji(tr["back"]), 14, (0, 0, 0),
                                 *BACK_BTN_RECT, bold=True)

    def _draw_glitch_label(self, painter):
        if self.current_screen != "game":
            return
        painter.text("GlitchHunters", 10, (0, 0, 200), 10, BOARD_H - 25,
                     max_width=200)

    def _on_keyboard(self, window, key, scancode, codepoint, modifier):
        if key == 27:  # ESC / Android back
            if self.dialog.active:
                self.dialog.touch_down(-1000, -1000)
                return True
            if self.current_screen != "game":
                self.switch_screen("game")
                return True
            self.stop_and_save()
            return True
        return False

    def stop_and_save(self):
        self.save_settings()
        self.stop()

    # -- settings / language -------------------------------------------
    def _load_settings(self):
        settings_file = os.path.join(self.base_dir, "settings.json")
        defaults = {
            "sound": True, "language": "Русский",
            "skin_ball": "ball1.png", "skin_basket": "basket.png",
            "inventory_balls": ["ball1.png"],
            "inventory_baskets": ["basket.png"],
            "inventory_bkballs": [], "inventory_csballs": [],
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
        try:
            self.game.save_game()
        except Exception:
            pass

    def set_language(self, lang):
        self.current_lang = lang
        self.settings["language"] = lang
        self.save_settings()
        scr = self.screens.get("game")
        if scr is not None:
            scr.set_language()

    def apply_skins(self):
        scr = self.screens.get("game")
        if scr is not None:
            scr.apply_skins()


def main():
    ClickerApp().run()


if __name__ == "__main__":
    main()
