import pygame
import platform


_CJK_RANGES = (
    (0x4E00, 0x9FFF), (0x3400, 0x4DBF), (0xF900, 0xFAFF),
    (0x20000, 0x2FA1F),
)

_CYRILLIC_RANGES = (
    (0x0400, 0x04FF), (0x0500, 0x052F), (0x2DE0, 0x2DFF),
    (0xA640, 0xA69F),
)

_FONT_CJK = "Microsoft YaHei"
_FONT_CYRILLIC = "Segoe UI"
_FONT_FALLBACK = "Arial"


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


def _try_font(name, size, bold):
    try:
        f = pygame.font.SysFont(name, size, bold=bold)
        if f:
            return f
    except Exception:
        pass
    return None


def get_font(size, bold=False):
    if platform.system() == "Windows":
        f = _try_font(_FONT_CYRILLIC, size, bold)
        if f:
            return f
    return pygame.font.SysFont(_FONT_FALLBACK, size, bold=bold)


def get_font_for(text, size, bold=False):
    if _has_cjk(text):
        if platform.system() == "Windows":
            f = _try_font(_FONT_CJK, size, bold)
            if f:
                return f
    if _has_cyrillic(text):
        if platform.system() == "Windows":
            f = _try_font(_FONT_CYRILLIC, size, bold)
            if f:
                return f
    return get_font(size, bold)


def strip_emoji(text):
    clean = []
    for ch in text:
        if ord(ch) > 0xFFFF:
            continue
        clean.append(ch)
    return "".join(clean)


def render_text(surface, text, font, color, x, y, max_width=None):
    lines = strip_emoji(text).split("\n")
    y_offset = 0
    sz = font.get_linesize()
    for line in lines:
        if _has_cjk(line) or _has_cyrillic(line):
            use_font = get_font_for(line, sz, bold=font.get_bold())
        else:
            use_font = font
        surf = use_font.render(line, True, color)
        if max_width and surf.get_width() > max_width:
            words = line.split(" ")
            current = ""
            for word in words:
                test = current + (" " if current else "") + word
                if use_font.size(test)[0] > max_width and current:
                    surface.blit(use_font.render(current, True, color), (x, y + y_offset))
                    y_offset += use_font.get_linesize()
                    current = word
                else:
                    current = test
            if current:
                surface.blit(use_font.render(current, True, color), (x, y + y_offset))
                y_offset += use_font.get_linesize()
        else:
            surface.blit(surf, (x, y + y_offset))
            y_offset += use_font.get_linesize()
    return y_offset


def text_height(font, text):
    lines = strip_emoji(text).split("\n")
    return len(lines) * font.get_linesize()
