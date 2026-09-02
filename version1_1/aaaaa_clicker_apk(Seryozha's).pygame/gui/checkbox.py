# -*- coding: utf-8 -*-
"""Kivy-native checkbox with label (drawn into its own canvas)."""
from kivy.graphics import Color, Rectangle, RoundedRectangle, InstructionGroup
from kivy.uix.widget import Widget

from gui.utils import make_label
from gui.screen import Screen


class KCheckbox(Widget):
    def __init__(self, rect, text, font_size=12, checked=True, callback=None,
                 box_size=20, **kwargs):
        x, y, w, h = Screen.flip_rect(rect)
        super().__init__(pos=(x, y), size=(w, h), **kwargs)
        self.rect = rect
        self.text = text
        self.font_size = font_size
        self.checked = checked
        self.callback = callback
        self.box_size = box_size
        self.hovered = False
        self._texture = None
        self._dyn = InstructionGroup()
        self.canvas.add(self._dyn)
        self._render_texture()

    def _render_texture(self):
        self._texture = None
        if self.text:
            self._texture = make_label(self.text, self.font_size,
                                       False, (0, 0, 0)).texture
        self._redraw()

    def set_text(self, text):
        if text != self.text:
            self.text = text
            self._render_texture()

    def _redraw(self, *args):
        self._dyn.clear()
        box = RoundedRectangle(radius=[3, 3, 3, 3, 3, 3, 3, 3])
        box.pos = (self.x, self.y + (self.height - self.box_size) / 2.0)
        box.size = (self.box_size, self.box_size)
        bg = (0.96, 0.96, 0.96, 1.0) if not self.hovered else (1.0, 1.0, 1.0, 1.0)
        self._dyn.add(Color(*bg))
        self._dyn.add(box)
        self._dyn.add(Color(0.39, 0.39, 0.39, 1.0))
        self._dyn.add(RoundedRectangle(radius=[2, 2, 2, 2, 2, 2, 2, 2],
                                       pos=(self.x + 1,
                                            self.y + (self.height - self.box_size) / 2.0 + 1),
                                       size=(self.box_size - 2, self.box_size - 2)))
        if self.checked:
            inner = self.box_size - 6
            self._dyn.add(Color(0.0, 0.59, 0.0, 1.0))
            self._dyn.add(Rectangle(pos=(self.x + 3,
                                         self.y + (self.height - self.box_size) / 2.0 + 3),
                                    size=(inner, inner)))
        if self._texture is not None:
            tw, th = self._texture.size
            tx = self.x + self.box_size + 8
            ty = self.y + (self.height - th) / 2.0
            self._dyn.add(Color(0, 0, 0, 1))
            self._dyn.add(Rectangle(texture=self._texture, pos=(tx, ty),
                                    size=(tw, th)))

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False
        self.checked = not self.checked
        self._redraw()
        if self.callback:
            self.callback(self.checked)
        return True

    def on_touch_move(self, touch):
        if not self.collide_point(*touch.pos):
            if self.hovered:
                self.hovered = False
                self._redraw()
            return False
        if not self.hovered:
            self.hovered = True
            self._redraw()
        return False