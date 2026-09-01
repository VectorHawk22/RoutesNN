# -*- coding: utf-8 -*-
"""Modal confirm/info dialog drawn as an overlay over the whole board."""
from gui.painter import Painter, BOARD_W, BOARD_H


class Dialog:
    BOX = (100, 150, 400, 190)
    BTN_H = 35
    BTN_W = 120
    BTN_GAP = 15

    def __init__(self):
        self.active = False
        self.title = ""
        self.message = ""
        self.buttons = []            # list of (text, value)
        self.callback = None
        self._btn_rects = []         # (x, y, w, h) top-left
        self.yes_text = "Yes"
        self.no_text = "No"

    def show_info(self, title, message):
        self.title = title
        self.message = message
        self.buttons = [("OK", True)]
        self.callback = None
        self.active = True
        self._layout()

    def show_confirm(self, title, message, on_yes, yes_text="Yes", no_text="No"):
        self.title = title
        self.message = message
        self.yes_text = yes_text
        self.no_text = no_text
        self.buttons = [(yes_text, True), (no_text, False)]
        self.callback = on_yes
        self.active = True
        self._layout()

    def _layout(self):
        bx, by, bw, bh = self.BOX
        n = len(self.buttons)
        total_w = n * self.BTN_W + (n - 1) * self.BTN_GAP
        start_x = bx + (bw - total_w) // 2
        btn_y = by + bh - 50
        self._btn_rects = []
        for i, (text, value) in enumerate(self.buttons):
            self._btn_rects.append((start_x + i * (self.BTN_W + self.BTN_GAP),
                                    btn_y, self.BTN_W, self.BTN_H))

    def touch_down(self, x, y):
        if not self.active:
            return False
        for (rx, ry, rw, rh), (text, value) in zip(self._btn_rects, self.buttons):
            if rx <= x <= rx + rw and ry <= y <= ry + rh:
                self.active = False
                cb = self.callback
                self.callback = None
                if cb:
                    cb(value)
                return True
        return True

    def touch_up(self, x, y):
        return self.active

    def draw(self, painter):
        if not self.active:
            return
        painter.rect(0, 0, BOARD_W, BOARD_H, (0, 0, 0, 128))
        bx, by, bw, bh = self.BOX
        painter.rounded(bx, by, bw, bh, (255, 255, 255), radius=10)
        painter.outline(bx, by, bw, bh, (100, 100, 100), width=2)
        painter.text(self.title, 18, (0, 0, 0), bx + 20, by + 15,
                     bold=True, max_width=bw - 40)
        painter.text(self.message, 14, (60, 60, 60), bx + 20, by + 50,
                     max_width=bw - 40)
        for (rx, ry, rw, rh), (text, value) in zip(self._btn_rects, self.buttons):
            painter.rounded(rx, ry, rw, rh, (200, 200, 200), radius=5)
            painter.outline(rx, ry, rw, rh, (100, 100, 100), width=1)
            painter.text_centered_in(text, 14, (0, 0, 0),
                                     rx, ry, rw, rh, bold=True)