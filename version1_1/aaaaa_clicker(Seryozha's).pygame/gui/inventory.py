import os
import pygame
from PIL import Image as PILImage
from gui import Screen, Button, get_font, render_text, strip_emoji


class InventoryScreen(Screen):
    def __init__(self, app):
        super().__init__(app)
        self.active_tab = "potions"
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.animation_dir = os.path.join(self.base_dir, "animation")
        self.images_dir = os.path.join(self.base_dir, "images")

        self.potion_img = None
        self.potion_empty_img = None
        self._load_potion_images()

        self.skin_thumbs = {}
        self._load_skin_thumbnails()

        self.btn_tab_potions = None
        self.btn_tab_skins = None
        self.btn_use_potion = None
        self.skin_rects = {}
        self._potion_timer = 0

        self._build_tabs()

    def _load_potion_images(self):
        for name, fname in [("full", "potionthatgives2xcoins.png"),
                            ("empty", "emptypotionthatgives2xcoins.png")]:
            path = os.path.join(self.images_dir, fname)
            if os.path.exists(path):
                try:
                    img = PILImage.open(path).convert("RGBA").resize((80, 80), PILImage.Resampling.LANCZOS)
                    data = img.tobytes()
                    surf = pygame.image.fromstring(data, img.size, "RGBA").convert_alpha()
                    if name == "full":
                        self.potion_img = surf
                    else:
                        self.potion_empty_img = surf
                except Exception as e:
                    print(f"Potion image load error ({fname}): {e}")

    def _load_skin_thumbnails(self):
        ball_skins = ["ball1.png", "ball2.png", "ball3.png", "ball4.png"]
        basket_skins = ["basket.png", "basket2.png", "basket3.png", "basket4.png"]
        for fname in ball_skins + basket_skins:
            path = os.path.join(self.animation_dir, fname)
            if not os.path.exists(path):
                continue
            try:
                img = PILImage.open(path).convert("RGBA")
                mask = img.getchannel("A").point(lambda a: 255 if a > 100 else 0)
                bbox = mask.getbbox()
                if bbox:
                    img = img.crop(bbox)
                w, h = img.size
                box = 56
                scale = min(box / float(w), box / float(h))
                nw = max(1, int(w * scale))
                nh = max(1, int(h * scale))
                img = img.resize((nw, nh), PILImage.Resampling.LANCZOS)
                data = img.tobytes()
                surf = pygame.image.fromstring(data, img.size, "RGBA").convert_alpha()
                self.skin_thumbs[fname] = surf
            except Exception:
                pass

    def _build_tabs(self):
        tr = self.app.translations[self.app.current_lang]
        self.btn_tab_potions = Button(
            (40, 60, 200, 38), tr["tab_potions"], font_size=13,
            bg_color=(200, 230, 255) if self.active_tab == "potions" else (220, 220, 220),
            callback=lambda: self._switch_tab("potions"))
        self.btn_tab_skins = Button(
            (260, 60, 200, 38), tr["tab_skins"], font_size=13,
            bg_color=(200, 230, 255) if self.active_tab == "skins" else (220, 220, 220),
            callback=lambda: self._switch_tab("skins"))
        self.btn_use_potion = Button(
            (40, 340, 160, 35), tr["potion_inactive"], font_size=11,
            bg_color=(180, 180, 180), callback=self._use_potion)

    def _switch_tab(self, name):
        self.active_tab = name
        self._build_tabs()

    def _use_potion(self):
        tr = self.app.translations[self.app.current_lang]
        if self.app.game.activate_potion():
            self._potion_timer = 180
            self.btn_use_potion.set_text(tr["use"])

    def handle_event(self, event):
        self.btn_tab_potions.handle_event(event)
        self.btn_tab_skins.handle_event(event)

        if self.active_tab == "potions":
            self.btn_use_potion.handle_event(event)
        elif self.active_tab == "skins":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for (kind, fname), rect in self.skin_rects.items():
                    if rect.collidepoint(event.pos):
                        key = "skin_ball" if kind == "ball" else "skin_basket"
                        self.app.settings[key] = fname
                        self.app.save_settings()
                        self.app.apply_skins()
                        break

    def update(self):
        if self._potion_timer > 0:
            self._potion_timer -= 1

    def draw(self, surface):
        tr = self.app.translations[self.app.current_lang]
        font_title = get_font(18, bold=True)
        font_label = get_font(13)
        font_small = get_font(11)

        render_text(surface, tr["inventory"], font_title, (0, 0, 0), 40, 15, 520)

        self.btn_tab_potions.draw(surface)
        self.btn_tab_skins.draw(surface)

        if self.active_tab == "potions":
            self._draw_potions_tab(surface, tr, font_label, font_small)
        else:
            self._draw_skins_tab(surface, tr, font_label, font_small)

    def _draw_potions_tab(self, surface, tr, font_label, font_small):
        card_rect = pygame.Rect(40, 115, 300, 180)
        pygame.draw.rect(surface, (255, 255, 200), card_rect, border_radius=8)
        pygame.draw.rect(surface, (200, 180, 50), card_rect, 2, border_radius=8)

        is_active = self.app.game.is_potion_active()
        img = self.potion_empty_img if is_active else self.potion_img
        if img:
            surface.blit(img, (55, 145))
        else:
            font_emoji = get_font(32)
            render_text(surface, "E", font_emoji, (100, 100, 100), 75, 165)

        render_text(surface, tr["potion"], font_label, (0, 0, 0), 150, 140, 180)

        self.btn_use_potion.set_text(tr["use"] if is_active else tr["potion_inactive"])
        self.btn_use_potion.draw(surface)

        time_left = self.app.game.get_potion_time_left()
        if time_left > 0:
            timer_text = tr["potion_active"].format(time_left)
            render_text(surface, timer_text, font_small, (0, 120, 0), 55, 255, 270)
        else:
            render_text(surface, tr["potion_inactive"], font_small, (100, 100, 100), 55, 255, 270)

        if self._potion_timer > 0 and self._potion_timer > 120:
            overlay = pygame.Surface((300, 180), pygame.SRCALPHA)
            overlay.fill((0, 255, 0, 60))
            surface.blit(overlay, card_rect.topleft)

    def _draw_skins_tab(self, surface, tr, font_label, font_small):
        current_ball = self.app.settings.get("skin_ball", "")
        current_basket = self.app.settings.get("skin_basket", "")
        self.skin_rects = {}

        owned_balls = self.app.settings.get("inventory_balls", [])
        owned_baskets = self.app.settings.get("inventory_baskets", [])

        render_text(surface, tr["skins_balls"] + ":", font_label, (0, 0, 0), 40, 110, 520)
        x_start = 40
        for i, fname in enumerate(owned_balls):
            rect = pygame.Rect(x_start + i * 110, 140, 100, 110)
            is_sel = (fname == current_ball)
            border_color = (0, 120, 215) if is_sel else (180, 180, 180)
            bg_color = (220, 240, 255) if is_sel else (240, 240, 240)
            pygame.draw.rect(surface, bg_color, rect, border_radius=6)
            pygame.draw.rect(surface, border_color, rect, 2, border_radius=6)

            thumb = self.skin_thumbs.get(fname)
            if thumb:
                tx = rect.centerx - thumb.get_width() // 2
                ty = rect.y + 10
                surface.blit(thumb, (tx, ty))

            name_label = fname.replace(".png", "")
            render_text(surface, name_label, font_small, (80, 80, 80),
                        rect.centerx - 15, rect.bottom - 18)
            self.skin_rects[("ball", fname)] = rect

        render_text(surface, tr["skins_baskets"] + ":", font_label, (0, 0, 0), 40, 265, 520)
        for i, fname in enumerate(owned_baskets):
            rect = pygame.Rect(x_start + i * 110, 295, 100, 110)
            is_sel = (fname == current_basket)
            border_color = (0, 120, 215) if is_sel else (180, 180, 180)
            bg_color = (220, 240, 255) if is_sel else (240, 240, 240)
            pygame.draw.rect(surface, bg_color, rect, border_radius=6)
            pygame.draw.rect(surface, border_color, rect, 2, border_radius=6)

            thumb = self.skin_thumbs.get(fname)
            if thumb:
                tx = rect.centerx - thumb.get_width() // 2
                ty = rect.y + 10
                surface.blit(thumb, (tx, ty))

            name_label = fname.replace(".png", "")
            render_text(surface, name_label, font_small, (80, 80, 80),
                        rect.centerx - 15, rect.bottom - 18)
            self.skin_rects[("basket", fname)] = rect
