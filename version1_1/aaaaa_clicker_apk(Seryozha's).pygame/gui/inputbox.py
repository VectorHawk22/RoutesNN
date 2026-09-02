# -*- coding: utf-8 -*-
"""Promo-code input: a Kivy TextInput styled for the board."""
from kivy.uix.textinput import TextInput

from gui.screen import Screen


class InputBox(TextInput):
    def __init__(self, rect, font_size=15, max_length=32, placeholder="",
                 callback=None, **kwargs):
        x, y, w, h = Screen.flip_rect(rect)
        super().__init__(
            pos=(x, y),
            size=(w, h),
            font_size=font_size,
            hint_text=placeholder,
            multiline=False,
            background_color=(1, 1, 1, 1),
            background_normal="",
            background_active="",
            cursor_color=(0, 0, 0, 1),
            foreground_color=(0, 0, 0, 1),
            hint_text_color=(0.6, 0.6, 0.6, 1),
            **kwargs,
        )
        self.rect = rect
        self._callback = callback
        self.max_text_length = max_length
        try:
            self.padding = (10, 8)
        except Exception:
            pass
        self.bind(on_text_validate=self._validate)

    def _validate(self, *args):
        if self._callback:
            self._callback(self.text)

    def clear(self):
        self.text = ""

    @property
    def active(self):
        return self.focus

    @active.setter
    def active(self, value):
        self.focus = value