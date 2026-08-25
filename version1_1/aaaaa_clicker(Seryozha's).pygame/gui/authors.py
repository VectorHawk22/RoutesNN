import pygame
from gui import Screen, get_font, strip_emoji, render_text


class AuthorsScreen(Screen):
    def __init__(self, app):
        super().__init__(app)

    def draw(self, surface):
        tr = self.app.translations[self.app.current_lang]
        font_title = get_font(20, bold=True)
        font_body = get_font(14)

        render_text(surface, tr["btn_authors"], font_title, (0, 0, 0), 40, 30, 520)

        lines = [
            "",
            "Developers:",
            "",
            "  thekosmoss",
            "  artman",
            "  amonpys",
            "",
            "Project: Basketball Click",
            "2026 (c) GlitchHunters Team",
            "",
            "Version: 1.0.0",
        ]
        y = 80
        for line in lines:
            render_text(surface, line, font_body, (40, 40, 40), 60, y, 480)
            y += 24
