import pygame
from gui.utils import get_font, get_font_for, strip_emoji, _has_cjk, _has_cyrillic


class Button:
    def __init__(self, rect, text, font_size=14, bg_color=(200, 200, 200),
                 text_color=(0, 0, 0), border_radius=8, callback=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = get_font(font_size, bold=True)
        self.bg_color = bg_color
        self.text_color = text_color
        self.border_radius = border_radius
        self.callback = callback
        self.hovered = False
        self._flash_timer = 0

    def set_text(self, text):
        self.text = text

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self._flash_timer = 6
                if self.callback:
                    self.callback()
                return True
        return False

    def draw(self, surface):
        if self._flash_timer > 0:
            color = (255, 255, 255)
            self._flash_timer -= 1
        elif self.hovered:
            color = tuple(min(255, c + 30) for c in self.bg_color)
        else:
            color = self.bg_color
        pygame.draw.rect(surface, color, self.rect, border_radius=self.border_radius)
        pygame.draw.rect(surface, (100, 100, 100), self.rect, 1, border_radius=self.border_radius)
        txt = strip_emoji(self.text)
        use_font = get_font_for(txt, self.font.get_linesize(), bold=self.font.get_bold()) if (_has_cjk(txt) or _has_cyrillic(txt)) else self.font
        text_surf = use_font.render(txt, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
