# -*- coding: utf-8 -*-
"""Kivy-native push button for the virtual board."""
from kivy.graphics import Color, RoundedRectangle, Line, Rectangle, InstructionGroup
from kivy.uix.widget import Widget

from gui.utils import make_label, strip_emoji
from gui.screen import Screen


class KButton(Widget):
    def __init__(self, rect, text, font_size=14, bg_color=(200, 200, 200),
                 text_color=(0, 0, 0), border_radius=8, callback=None,
                 bold=True, **kwargs):
        x, y, w, h = Screen.flip_rect(rect)
        super().__init__(pos=(x, y), size=(w, h), **kwargs)
        self.rect = rect
        self.text = text
        self.font_size = font_size
        self.bg_color = bg_color
        self.text_color = text_color
        self.border_radius = border_radius
        self.callback = callback
        self.bold = bold
        self.hovered = False
        self._normal_bg = bg_color
        self._texture = None
        self._dyn = InstructionGroup()
        self.canvas.add(self._dyn)
        self._render_texture()
        self._redraw()

    def _render_texture(self):
        from gui.utils import strip_emoji as _se
        txt = _se(self.text)
        if txt:
            self._texture = make_label(txt, self.font_size, self.bold,
                                       self.text_color).texture
        else:
            self._texture = None
        self._redraw()

    def _redraw(self, *args):
        self._dyn.clear()
        bg = self.bg_color if not self.hovered else tuple(
            min(255, c + 30) for c in self.bg_color)
        alpha = (bg[3] / 255.0) if len(bg) > 3 else 1.0
        self._dyn.add(Color(bg[0] / 255.0, bg[1] / 255.0, bg[2] / 255.0, alpha))
        self._dyn.add(RoundedRectangle(pos=self.pos, size=self.size,
                                       radius=[float(self.border_radius)] * 8))
        self._dyn.add(Color(0.4, 0.4, 0.4, 1.0))
        self._dyn.add(Line(rectangle=(self.x, self.y, self.width, self.height),
                           width=1))
        if self._texture is None:
            return
        tw, th = self._texture.size
        tx = self.x + (self.width - tw) / 2.0
        ty = self.y + (self.height - th) / 2.0
        self._dyn.add(Color(self.text_color[0] / 255.0,
                            self.text_color[1] / 255.0,
                            self.text_color[2] / 255.0,
                            (self.text_color[3] / 255.0)
                            if len(self.text_color) > 3 else 1.0))
        self._dyn.add(Rectangle(texture=self._texture, pos=(tx, ty),
                                size=(tw, th)))

    def set_text(self, text):
        if text != self.text:
            self.text = text
            self._render_texture()

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False
        if self.callback:
            self.callback()
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