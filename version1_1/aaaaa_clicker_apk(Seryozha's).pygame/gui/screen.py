# -*- coding: utf-8 -*-
"""Base class for the game screens (Kivy Widgets on the 600x490 board)."""
from kivy.uix.widget import Widget
from kivy.graphics import InstructionGroup

from gui.painter import BOARD_W, BOARD_H


class Screen(Widget):
    """A full-board widget. Screens paint dynamic content into self.frame and
    may also add native child widgets (buttons etc.) that are drawn on top."""

    BOARD_W = BOARD_W
    BOARD_H = BOARD_H

    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.size_hint = (None, None)
        self.size = (BOARD_W, BOARD_H)
        self.pos = (0, 0)
        self.frame = InstructionGroup()
        self.canvas.add(self.frame)

    def clear(self):
        self.frame.clear()

    def on_enter(self):
        """Called by the app whenever this screen becomes active."""
        pass

    def update(self):
        """Called every frame while the screen is active."""
        pass

    def draw(self, painter):
        """Rebuild this screen's static canvas instruction set."""
        pass

    # -- touch (coordinates already in 600x490 board units) ------------
    def touch_down(self, x, y):
        return False

    def touch_move(self, x, y):
        return False

    def touch_up(self, x, y):
        return False

    # -- helpers -------------------------------------------------------
    def rebuild_widgets(self):
        """Base hook for screens that recreate text when the language changes."""
        pass

    @staticmethod
    def flip_rect(rect):
        """Convert a top-left (x, y, w, h) rect to Kivy bottom-left pos+size."""
        x, y, w, h = rect
        return x, BOARD_H - y - h, w, h