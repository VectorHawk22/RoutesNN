# -*- coding: utf-8 -*-
"""Kivy port of the old pygame font helpers.

Text is rendered with kivy.core.text.CoreLabel (cached). Latin and Cyrillic
use Kivy's bundled Roboto; Chinese uses the bundled fonts/msyh.ttc when a
Chinese glyph is detected.
"""
import os

_CJK_RANGES = (
    (0x4E00, 0x9FFF), (0x3400, 0x4DBF), (0xF900, 0xFAFF),
    (0x20000, 0x2FA1F),
)

_CYRILLIC_RANGES = (
    (0x0400, 0x04FF), (0x0500, 0x052F), (0x2DE0, 0x2DFF),
    (0xA640, 0xA69F),
)

_CJK_FONT_NAME = None
_FONTS_REGISTERED = False
_LABEL_CACHE = {}


def _has_cjk(text):
    for ch in text:
        cp = ord(ch)
        for lo, hi in _CJK_RANGES:
            if lo <= cp <= hi:
                return True
    return False


def _has_cyrillic(text):
    for ch in text:
        cp = ord(ch)
        for lo, hi in _CYRILLIC_RANGES:
            if lo <= cp <= hi:
                return True
    return False


def strip_emoji(text):
    clean = []
    for ch in text:
        if ord(ch) > 0xFFFF:
            continue
        clean.append(ch)
    return "".join(clean)


def _fonts_dir():
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(here, "fonts")


def register_fonts():
    """Register bundled fonts with Kivy (Roboto ships with Kivy itself)."""
    global _CJK_FONT_NAME, _FONTS_REGISTERED
    if _FONTS_REGISTERED:
        return
    _FONTS_REGISTERED = True
    from kivy.core.text import LabelBase
    path = os.path.join(_fonts_dir(), "msyh.ttc")
    if os.path.exists(path):
        _CJK_FONT_NAME = "GameCJK"
        LabelBase.register(name="GameCJK", fn_regular=path, fn_bold=path)


def font_name_for(text):
    register_fonts()
    if _has_cjk(text) and _CJK_FONT_NAME:
        return _CJK_FONT_NAME
    return "Roboto"


def _rgba(color, alpha=1.0):
    if len(color) == 3:
        r, g, b = color
        a = alpha
    else:
        r, g, b, a = color
        a = a * alpha
    return (r / 255.0, g / 255.0, b / 255.0, a)


def make_label(text, size, bold=False, color=(0, 0, 0)):
    """Return a refreshed CoreLabel for the given text/params (cached)."""
    key = (text, int(size), bool(bold), tuple(color))
    label = _LABEL_CACHE.get(key)
    if label is None:
        from kivy.core.text import Label as CoreLabel
        label = CoreLabel(
            text=text,
            font_size=float(size),
            bold=bold,
            font_name=font_name_for(text),
            color=_rgba(color),
        )
        label.refresh()
        if len(_LABEL_CACHE) > 900:
            _LABEL_CACHE.clear()
        _LABEL_CACHE[key] = label
    return label


def text_size(text, size, bold=False):
    """Width/height of the wrapped text (roughly), in virtual pixels."""
    label = make_label(text, size, bold)
    if label.texture is None:
        return 0, 0
    return label.texture.width, label.texture.height


# Kept for API compatibility with older helpers.
def get_linesize(size, bold=False):
    return max(1, int(size * 1.2))