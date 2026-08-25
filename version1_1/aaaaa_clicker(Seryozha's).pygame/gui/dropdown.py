import pygame
from gui.utils import get_font, get_font_for, strip_emoji, _has_cjk, _has_cyrillic


class Dropdown:
    def __init__(self, rect, options, font_size=13, selected=None, callback=None):
        self.rect = pygame.Rect(rect)
        self.options = options
        self.font = get_font(font_size)
        self.callback = callback
        self.selected = selected or (options[0] if options else "")
        self.open = False
        self.option_height = 30

    def set_selected(self, value):
        self.selected = value

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.open = not self.open
                return True
            elif self.open:
                for i, opt in enumerate(self.options):
                    opt_rect = pygame.Rect(self.rect.x, self.rect.bottom + i * self.option_height,
                                           self.rect.width, self.option_height)
                    if opt_rect.collidepoint(event.pos):
                        self.selected = opt
                        self.open = False
                        if self.callback:
                            self.callback(opt)
                        return True
                self.open = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button != 1:
            self.open = False
        return False

    def draw(self, surface):
        pygame.draw.rect(surface, (255, 255, 255), self.rect, border_radius=4)
        pygame.draw.rect(surface, (100, 100, 100), self.rect, 2, border_radius=4)
        txt = strip_emoji(self.selected)
        use_font = get_font_for(txt, self.font.get_linesize(), bold=self.font.get_bold()) if (_has_cjk(txt) or _has_cyrillic(txt)) else self.font
        text_surf = use_font.render(txt, True, (0, 0, 0))
        surface.blit(text_surf, (self.rect.x + 8, self.rect.centery - text_surf.get_height() // 2))
        ax = self.rect.right - 18
        ay = self.rect.centery
        if self.open:
            pygame.draw.polygon(surface, (0, 0, 0),
                                [(ax, ay + 4), (ax + 8, ay + 4), (ax + 4, ay - 4)])
        else:
            pygame.draw.polygon(surface, (0, 0, 0),
                                [(ax, ay - 4), (ax + 8, ay - 4), (ax + 4, ay + 4)])

        if self.open:
            overlay = pygame.Surface((self.rect.width, len(self.options) * self.option_height), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 240))
            surface.blit(overlay, (self.rect.x, self.rect.bottom))
            for i, opt in enumerate(self.options):
                opt_rect = pygame.Rect(self.rect.x, self.rect.bottom + i * self.option_height,
                                       self.rect.width, self.option_height)
                if opt_rect.collidepoint(pygame.mouse.get_pos()):
                    pygame.draw.rect(surface, (200, 220, 255), opt_rect)
                pygame.draw.rect(surface, (180, 180, 180), opt_rect, 1)
                opt_txt = strip_emoji(opt)
                opt_font = get_font_for(opt_txt, self.font.get_linesize(), bold=self.font.get_bold()) if (_has_cjk(opt_txt) or _has_cyrillic(opt_txt)) else self.font
                opt_surf = opt_font.render(opt_txt, True, (0, 0, 0))
                surface.blit(opt_surf, (opt_rect.x + 8,
                                        opt_rect.centery - opt_surf.get_height() // 2))
