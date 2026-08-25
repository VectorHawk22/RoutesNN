import pygame
from gui.utils import get_font, render_text, strip_emoji


class Dialog:
    def __init__(self):
        self.active = False
        self.title = ""
        self.message = ""
        self.buttons = []
        self.callback = None
        self._btn_rects = []
        self.yes_text = "Yes"
        self.no_text = "No"

    def show_info(self, title, message):
        self.title = title
        self.message = message
        self.buttons = [("OK", True)]
        self.callback = None
        self.active = True

    def show_confirm(self, title, message, on_yes, yes_text="Yes", no_text="No"):
        self.title = title
        self.message = message
        self.yes_text = yes_text
        self.no_text = no_text
        self.buttons = [(yes_text, True), (no_text, False)]
        self.callback = on_yes
        self.active = True

    def handle_event(self, event):
        if not self.active:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for rect, text, value in self._btn_rects:
                if rect.collidepoint(event.pos):
                    self.active = False
                    if self.callback:
                        self.callback(value)
                    return True
        return True

    def draw(self, surface):
        if not self.active:
            return
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        surface.blit(overlay, (0, 0))

        box = pygame.Rect(100, 150, 400, 190)
        pygame.draw.rect(surface, (255, 255, 255), box, border_radius=10)
        pygame.draw.rect(surface, (100, 100, 100), box, 2, border_radius=10)

        title_font = get_font(18, bold=True)
        render_text(surface, self.title, title_font, (0, 0, 0), box.x + 20, box.y + 15, box.width - 40)

        msg_font = get_font(14)
        render_text(surface, self.message, msg_font, (60, 60, 60), box.x + 20, box.y + 50, box.width - 40)

        self._btn_rects = []
        btn_w = 120
        btn_h = 35
        total_w = len(self.buttons) * btn_w + max(0, len(self.buttons) - 1) * 15
        btn_x = box.centerx - total_w // 2
        btn_y = box.bottom - 50

        btn_font = get_font(14, bold=True)
        for text, value in self.buttons:
            rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
            mouse_over = rect.collidepoint(pygame.mouse.get_pos())
            color = (220, 220, 220) if mouse_over else (200, 200, 200)
            pygame.draw.rect(surface, color, rect, border_radius=5)
            pygame.draw.rect(surface, (100, 100, 100), rect, 1, border_radius=5)
            txt = strip_emoji(text)
            txt_surf = btn_font.render(txt, True, (0, 0, 0))
            surface.blit(txt_surf, (rect.centerx - txt_surf.get_width() // 2,
                                    rect.centery - txt_surf.get_height() // 2))
            self._btn_rects.append((rect, text, value))
            btn_x += btn_w + 15
