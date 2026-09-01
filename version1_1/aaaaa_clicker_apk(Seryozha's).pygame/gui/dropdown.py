# -*- coding: utf-8 -*-
"""Kivy-native dropdown (base box + expandable option list)."""
from kivy.graphics import (Color, RoundedRectangle, Rectangle, Line,
                           InstructionGroup)
from kivy.uix.widget import Widget

from gui.utils import make_label
from gui.screen import Screen

ROW_H = 30


class KDropdown(Widget):
    """Top-left rect descriptor: (x, y, w, h). The widget grows downwards when
    the list is open so touches on the rows are received natively."""

    def __init__(self, rect, options, font_size=13, selected=None,
                 callback=None, **kwargs):
        super().__init__(**kwargs)
        self.rect = rect
        self.options = list(options)
        self.font_size = font_size
        self.callback = callback
        self.selected = selected or (self.options[0] if self.options else "")
        self.open = False
        self._texture = None
        self._dyn = InstructionGroup()
        self.canvas.add(self._dyn)
        self.reflow()

    # -- geometry ------------------------------------------------------
    def _list_h(self):
        return len(self.options) * ROW_H if self.open else 0

    def reflow(self):
        x, y, w, h = self.rect
        self.pos = (x, Screen.BOARD_H - y - h - self._list_h())
        self.size = (w, h + self._list_h())
        self._texture = make_label(self.selected, self.font_size,
                                   False, (0, 0, 0)).texture
        self._redraw()

    # -- redraw --------------------------------------------------------
    def _redraw(self, *args):
        self._dyn.clear()
        x, y, w, h = self.rect
        # base box - the widget's canvas lives in board-global (bottom-left)
        # coordinates, so use the widget's absolute pos, not local offsets.
        gx = self.x
        list_h = self._list_h()
        box_y = self.y + list_h
        self._dyn.add(Color(1, 1, 1, 1))
        self._dyn.add(RoundedRectangle(radius=[4, 4, 4, 4, 4, 4, 4, 4],
                                       pos=(gx, box_y), size=(w, h)))
        self._dyn.add(Color(0.39, 0.39, 0.39, 1))
        self._dyn.add(Line(rectangle=(gx, box_y, w, h), width=2))
        if self._texture is not None:
            tw, th = self._texture.size
            self._dyn.add(Color(0, 0, 0, 1))
            self._dyn.add(Rectangle(texture=self._texture,
                                    pos=(gx + 8, box_y + h / 2.0 - th / 2.0),
                                    size=(tw, th)))
        ax = gx + w - 18
        ay = box_y + h / 2.0 - 4
        if self.open:
            pts = [ax, ay + 8, ax + 8, ay + 8, ax + 4, ay]
        else:
            pts = [ax, ay, ax + 8, ay, ax + 4, ay + 8]
        self._dyn.add(Color(0, 0, 0, 1))
        self._dyn.add(Line(points=pts, close=True, width=1.5))

        if not self.open:
            return
        for i, opt in enumerate(self.options):
            row_y = self.y + list_h - (i + 1) * ROW_H
            if i % 2 == 0:
                self._dyn.add(Color(1, 1, 1, 0.96))
            else:
                self._dyn.add(Color(0.95, 0.95, 0.95, 0.96))
            self._dyn.add(Rectangle(pos=(gx, row_y), size=(w, ROW_H)))
            self._dyn.add(Color(0.71, 0.71, 0.71, 1))
            self._dyn.add(Line(points=[gx, row_y, gx + w, row_y], width=1))
            lab = make_label(opt, self.font_size, False, (0, 0, 0))
            if lab.texture is not None:
                tw, th = lab.texture.size
                self._dyn.add(Color(0, 0, 0, 1))
                self._dyn.add(Rectangle(texture=lab.texture,
                                        pos=(gx + 8, row_y + (ROW_H - th) / 2.0),
                                        size=(tw, th)))

    def set_selected(self, value):
        if value in self.options:
            self.selected = value
            self.reflow()

    def close(self):
        if self.open:
            self.open = False
            self.reflow()

    # -- touch ---------------------------------------------------------
    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False
        x, y, w, h = self.rect
        gx = self.x
        list_h = self._list_h()
        box_y = self.y + list_h
        if self.open:
            for i in range(len(self.options)):
                row_y = self.y + list_h - (i + 1) * ROW_H
                if row_y <= touch.y <= row_y + ROW_H:
                    self.selected = self.options[i]
                    self.open = False
                    self.reflow()
                    if self.callback:
                        self.callback(self.selected)
                    return True
        if box_y <= touch.y <= box_y + h and gx <= touch.x <= gx + w:
            self.open = not self.open
            self.reflow()
            return True
        self.open = False
        self.reflow()
        return False