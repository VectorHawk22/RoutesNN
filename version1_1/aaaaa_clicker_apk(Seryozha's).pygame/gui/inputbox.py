import pygame
from gui.utils import get_font, get_font_for, strip_emoji, _has_cjk, _has_cyrillic


class InputBox:
    def __init__(self, rect, font_size=14, max_length=32, placeholder="",
                 text_color=(0, 0, 0), bg_color=(255, 255, 255),
                 border_color=(100, 100, 100), active_border_color=(0, 120, 200),
                 callback=None):
        self.rect = pygame.Rect(rect)
        self.font = get_font(font_size)
        self.max_length = max_length
        self.placeholder = placeholder
        self.text_color = text_color
        self.bg_color = bg_color
        self.border_color = border_color
        self.active_border_color = active_border_color
        self.callback = callback
        self.text = ""
        self.active = False
        self.hovered = False
        self._cursor_timer = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            was_active = self.active
            self.active = self.rect.collidepoint(event.pos)
            if was_active and not self.active:
                if self.callback:
                    self.callback("")
            return self.active
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                if self.callback:
                    self.callback(self.text)
            return True
        if event.type == pygame.TEXTINPUT and self.active:
            if len(self.text) < self.max_length:
                self.text += event.text
            return True
        return False

    def clear(self):
        self.text = ""
        self.active = False

    def draw(self, surface):
        border = self.active_border_color if self.active else self.border_color
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=5)
        pygame.draw.rect(surface, border, self.rect, 2, border_radius=5)

        clip_rect = self.rect.inflate(-12, -8)
        old_clip = surface.get_clip()
        surface.set_clip(clip_rect)

        text = self.text if self.text else self.placeholder
        color = self.text_color if self.text else (160, 160, 160)
        use_font = get_font_for(text, self.font.get_linesize(),
                                bold=self.font.get_bold()) if (_has_cjk(text) or _has_cyrillic(text)) else self.font
        txt_surf = use_font.render(strip_emoji(text), True, color)
        text_rect = txt_surf.get_rect(midleft=(self.rect.x + 10, self.rect.centery))
        surface.blit(txt_surf, text_rect)

        if self.active:
            self._cursor_timer += 1
            if (self._cursor_timer // 20) % 2 == 0:
                cx = text_rect.right + 2
                if cx < self.rect.right - 8:
                    pygame.draw.line(surface, (0, 0, 0), (cx, self.rect.y + 8),
                                     (cx, self.rect.bottom - 8), 1)

        surface.set_clip(old_clip)
