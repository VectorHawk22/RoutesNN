# -*- coding: utf-8 -*-
"""Immediate-mode painter for the virtual 600x490 board.

All positions use the classic top-left coordinate system (y grows DOWN).
The painter converts them to Kivy's bottom-left canvas coordinates before
appending instructions to the target InstructionGroup.
"""
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from gui.utils import make_label, strip_emoji, _has_cjk

BOARD_W = 600
BOARD_H = 490


def _rgba(color):
    if len(color) == 3:
        r, g, b = color
        a = 255
    else:
        r, g, b, a = color
    return (r / 255.0, g / 255.0, b / 255.0, a / 255.0)


class Painter:
    def __init__(self, group, board_h=BOARD_H):
        self.g = group
        self.board_h = board_h

    def _flip(self, y, h):
        return self.board_h - y - h

    def _point(self, x, y):
        return x, self.board_h - y

    def rect(self, x, y, w, h, color):
        if w <= 0 or h <= 0:
            return
        self.g.add(Color(*_rgba(color)))
        self.g.add(Rectangle(pos=self._point(x, y + h), size=(w, h)))

    def rounded(self, x, y, w, h, color, radius=8, segments=14):
        if w <= 0 or h <= 0:
            return
        self.g.add(Color(*_rgba(color)))
        self.g.add(RoundedRectangle(
            pos=self._point(x, y + h), size=(w, h),
            radius=[float(radius)] * 8, segments=segments))

    def outline(self, x, y, w, h, color=(100, 100, 100, 255), width=1):
        self.g.add(Color(*_rgba(color)))
        self.g.add(Line(rectangle=(x, self._flip(y, h), w, h), width=width))

    def line(self, x1, y1, x2, y2, color=(0, 0, 0, 255), width=1):
        self.g.add(Color(*_rgba(color)))
        self.g.add(Line(points=list(self._point(x1, y1)) + list(self._point(x2, y2)),
                        width=width))

    def poly(self, points, color=(0, 0, 0, 255)):
        """points: list of (x, y) top-left coords."""
        flat = []
        for x, y in points:
            flat.extend(self._point(x, y))
        self.g.add(Color(*_rgba(color)))
        self.g.add(Line(points=flat, close=True, width=1))

    def image(self, texture, x, y, w=None, h=None):
        if texture is None:
            return
        if w is None:
            w = texture.width
        if h is None:
            h = texture.height
        self.g.add(Color(1, 1, 1, 1))
        self.g.add(Rectangle(texture=texture,
                             pos=self._point(x, y + h), size=(w, h)))

    # -- text ----------------------------------------------------------
    def text(self, text, size, color, x, y, bold=False, max_width=None,
             align="left"):
        """Draw text at top-left (x, y). Returns the total height used."""
        lines = _wrap_text(text, max_width, size, bold)
        acc_y = 0
        for line in lines:
            label = make_label(line, size, bold, color)
            tex = label.texture
            if tex is None:
                labelsize = getattr(label, "size", None)
                h = labelsize[1] if labelsize else int(size * 1.2)
                acc_y += h
                continue
            tw, th = tex.width, tex.height
            if align == "center":
                dx = int(x) - tw // 2
            elif align == "right":
                dx = int(x) - tw
            else:
                dx = int(x)
            row_h = max(th, label.height)
            self.g.add(Color(*_rgba(color)))
            self.g.add(Rectangle(texture=tex, pos=self._point(dx, y + acc_y + th),
                                 size=(tw, th)))
            acc_y += row_h
        return acc_y

    def text_centered_in(self, text, size, color, cx, cy, w, h, bold=False):
        """Center text inside a rect whose top-left is (cx, cy)."""
        label = make_label(text, size, bold, color)
        tex = label.texture
        if tex is None:
            return
        tw, th = tex.width, tex.height
        dx = int(cx + (w - tw) / 2)
        dy = int(cy + (h - th) / 2)
        self.g.add(Color(*_rgba(color)))
        self.g.add(Rectangle(texture=tex, pos=self._point(dx, dy + th), size=(tw, th)))


def _wrap_text(text, max_width, size, bold):
    text = strip_emoji(text)
    if max_width is None:
        return text.split("\n")
    result = []
    for para in text.split("\n"):
        if not para:
            result.append("")
            continue
        cur = ""
        for word in _split_words(para):
            probe = (cur + " " + word).strip() if cur else word
            if cur and _width_of(probe, size, bold) > max_width:
                result.append(cur)
                cur = word
            else:
                cur = probe
        if cur:
            result.append(cur)
    return result


def _split_words(text):
    if any(_has_cjk(c) for c in text):
        return list(text)
    return text.split(" ")


def _width_of(text, size, bold):
    label = make_label(text, size, bold)
    if label.texture is None:
        return int(size * len(text))
    return label.texture.width