# -*- coding: utf-8 -*-
"""Authors screen: credits text."""
from gui.screen import Screen


class AuthorsScreen(Screen):
    def __init__(self, app):
        super().__init__(app)

    def draw(self, painter):
        tr = self.app.translations[self.app.current_lang]
        painter.text(tr["btn_authors"], 20, (0, 0, 0), 40, 30,
                     bold=True, max_width=520)

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
            painter.text(line, 14, (40, 40, 40), 60, y, max_width=480)
            y += 24