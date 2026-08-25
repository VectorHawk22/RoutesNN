import os
import pygame
from PIL import Image as PILImage
from gui import Screen, Button, get_font, strip_emoji, render_text


BALL_ITEMS = [
    {"file": "ball2.png", "name": "Ball 2", "price": 500},
    {"file": "ball3.png", "name": "Ball 3", "price": 500},
    {"file": "ball4.png", "name": "Ball 4", "price": 500},
]
BASKET_ITEMS = [
    {"file": "basket4.png", "name": "Hoop 4", "price": 500},
    {"file": "basket3.png", "name": "Hoop 3", "price": 800},
    {"file": "basket2.png", "name": "Hoop 2", "price": 1000},
]


class ShopScreen(Screen):
    def __init__(self, app):
        super().__init__(app)
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.animation_dir = os.path.join(self.base_dir, "animation")
        self.active_tab = "balls"
        self._thumb_refs = {}
        self.btn_upgrades = None
        self.btn_balls = None
        self.btn_baskets = None
        self.item_buy_rects = []
        try:
            self._load_thumbs()
        except Exception as e:
            print(f"Shop thumbs load error: {e}")
        self._build_tabs()

    def _load_thumbs(self):
        all_files = [item["file"] for item in BALL_ITEMS + BASKET_ITEMS]
        for fname in all_files:
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
                box = 48
                scale = min(box / float(w), box / float(h))
                nw = max(1, int(w * scale))
                nh = max(1, int(h * scale))
                img = img.resize((nw, nh), PILImage.Resampling.LANCZOS)
                data = img.tobytes()
                surf = pygame.image.fromstring(data, img.size, "RGBA").convert_alpha()
                self._thumb_refs[fname] = surf
            except Exception:
                pass

    def _build_tabs(self):
        tr = self.app.translations[self.app.current_lang]
        self.btn_upgrades = Button(
            (40, 55, 165, 35), tr["shop_tab_upgrades"], font_size=13,
            bg_color=(200, 230, 255) if self.active_tab == "upgrades" else (220, 220, 220),
            callback=lambda: self._switch_tab("upgrades"))
        self.btn_balls = Button(
            (217, 55, 165, 35), tr["shop_tab_balls"], font_size=13,
            bg_color=(200, 230, 255) if self.active_tab == "balls" else (220, 220, 220),
            callback=lambda: self._switch_tab("balls"))
        self.btn_baskets = Button(
            (394, 55, 165, 35), tr["shop_tab_baskets"], font_size=13,
            bg_color=(200, 230, 255) if self.active_tab == "baskets" else (220, 220, 220),
            callback=lambda: self._switch_tab("baskets"))

    def _switch_tab(self, name):
        self.active_tab = name
        self.item_buy_rects = []
        self._build_tabs()

    def handle_event(self, event):
        self.btn_upgrades.handle_event(event)
        self.btn_balls.handle_event(event)
        self.btn_baskets.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for rect, item, kind in self.item_buy_rects:
                if rect.collidepoint(event.pos):
                    self._buy_item(item, kind)
                    break

    def _buy_item(self, item, kind):
        tr = self.app.translations[self.app.current_lang]
        points = self.app.game.get_points()
        if points < item["price"]:
            self.app.dialog.show_info(tr["btn_shop"], tr["shop_not_enough"])
            return

        self.app.game.points -= item["price"]
        self.app.game.save_game()

        inv_key = "inventory_balls" if kind == "ball" else "inventory_baskets"
        inv = self.app.settings.get(inv_key, [])
        if item["file"] not in inv:
            inv.append(item["file"])
            self.app.settings[inv_key] = inv

        self.app.save_settings()
        self._build_tabs()

    def update(self):
        pass

    def draw(self, surface):
        tr = self.app.translations[self.app.current_lang]
        font_title = get_font(20, bold=True)
        font_name = get_font(14, bold=True)
        font_price = get_font(13)
        font_small = get_font(11)

        render_text(surface, tr["btn_shop"], font_title, (0, 0, 0), 40, 15, 520)

        self.btn_upgrades.draw(surface)
        self.btn_balls.draw(surface)
        self.btn_baskets.draw(surface)

        self.item_buy_rects = []

        if self.active_tab == "upgrades":
            render_text(surface, tr["shop_coming_soon"], font_price, (140, 140, 140), 200, 200, 250)
        elif self.active_tab == "balls":
            inv = self.app.settings.get("inventory_balls", [])
            self._draw_items(surface, BALL_ITEMS, inv, "ball", font_name, font_price, font_small, tr)
        elif self.active_tab == "baskets":
            inv = self.app.settings.get("inventory_baskets", [])
            self._draw_items(surface, BASKET_ITEMS, inv, "basket", font_name, font_price, font_small, tr)

    def _draw_items(self, surface, items, owned, kind, font_name, font_price, font_small, tr):
        y = 105
        for item in items:
            frame_rect = pygame.Rect(40, y, 520, 75)
            pygame.draw.rect(surface, (245, 245, 245), frame_rect, border_radius=6)
            pygame.draw.rect(surface, (180, 180, 180), frame_rect, 1, border_radius=6)

            thumb = self._thumb_refs.get(item["file"])
            if thumb:
                tx = frame_rect.x + 12
                ty = frame_rect.centery - thumb.get_height() // 2
                surface.blit(thumb, (tx, ty))

            name_x = frame_rect.x + 75
            render_text(surface, item["name"], font_name, (0, 0, 0), name_x, y + 10)

            is_owned = item["file"] in owned
            if is_owned:
                render_text(surface, tr["shop_owned"], font_price, (0, 150, 0), name_x, y + 35)
            else:
                price_text = tr["shop_price"].format(item["price"])
                render_text(surface, price_text, font_price, (180, 90, 0), name_x, y + 35)

                btn_rect = pygame.Rect(frame_rect.right - 100, y + 18, 85, 35)
                mouse_over = btn_rect.collidepoint(pygame.mouse.get_pos())
                color = (160, 255, 160) if mouse_over else (144, 238, 144)
                pygame.draw.rect(surface, color, btn_rect, border_radius=6)
                pygame.draw.rect(surface, (100, 100, 100), btn_rect, 1, border_radius=6)
                buy_txt = strip_emoji(tr["shop_buy"])
                buy_surf = font_small.render(buy_txt, True, (0, 0, 0))
                surface.blit(buy_surf, (btn_rect.centerx - buy_surf.get_width() // 2,
                                        btn_rect.centery - buy_surf.get_height() // 2))
                self.item_buy_rects.append((btn_rect, item, kind))

            y += 85
