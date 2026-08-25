import pygame
from gui.utils import get_font, get_font_for, strip_emoji, _has_cjk, _has_cyrillic


class Checkbox:
    def __init__(self, rect, text, font_size=12, checked=True, callback=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = get_font(font_size)
        self.checked = checked
        self.callback = callback
        self.box_size = 20
        self.hovered = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.checked = not self.checked
                if self.callback:
                    self.callback(self.checked)
                return True
        return False

    def draw(self, surface):
        box_y = self.rect.centery - self.box_size // 2
        box_rect = pygame.Rect(self.rect.x, box_y, self.box_size, self.box_size)
        color = (255, 255, 255) if self.hovered else (240, 240, 240)
        pygame.draw.rect(surface, color, box_rect, border_radius=3)
        pygame.draw.rect(surface, (100, 100, 100), box_rect, 2, border_radius=3)
        if self.checked:
            inner = box_rect.inflate(-6, -6)
            pygame.draw.rect(surface, (0, 150, 0), inner, border_radius=2)
        txt = strip_emoji(self.text)
        use_font = get_font_for(txt, self.font.get_linesize(), bold=self.font.get_bold()) if (_has_cjk(txt) or _has_cyrillic(txt)) else self.font
        text_surf = use_font.render(txt, True, (0, 0, 0))
        surface.blit(text_surf, (self.rect.x + self.box_size + 8,
                                 self.rect.centery - text_surf.get_height() // 2))
