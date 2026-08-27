import os
import pygame
from PIL import Image as PILImage
from gui import Screen, Button, get_font, strip_emoji, render_text


SET_PRICE = 1500


BALL_ITEMS = [
    {"file": "ball2.png", "name": "Ball 2", "price": 500},
    {"file": "ball3.png", "name": "Ball 3", "price": 500},
    {"file": "ball4.png", "name": "Ball 4", "price": 500},
    {"file": "ball5.png", "name": "Ball 5", "price": 400},
]
BASKET_ITEMS = [
    {"file": "basket4.png", "name": "Hoop 4", "price": 500},
    {"file": "basket3.png", "name": "Hoop 3", "price": 800},
    {"file": "basket2.png", "name": "Hoop 2", "price": 1000},
]

BKBALL_VARIANTS = [
    {"file": "bkball1.png", "name": "BKBall 1", "price": 600},
    {"file": "bkball2.png", "name": "BKBall 2", "price": 600},
    {"file": "bkball3.png", "name": "BKBall 3", "price": 600},
    {"file": "bkball4.png", "name": "BKBall 4", "price": 600},
    {"file": "bkball5.png", "name": "BKBall 5", "price": 600},
    {"file": "bkball6.png", "name": "BKBall 6", "price": 600},
]

CSBALL_VARIANTS = [
    {"file": "csball1.png", "name": "CS Ball 1", "price": 800},
    {"file": "csball2.png", "name": "CS Ball 2", "price": 800},
    {"file": "csball3.png", "name": "CS Ball 3", "price": 800},
    {"file": "csball4.png", "name": "CS Ball 4", "price": 800},
    {"file": "csball5.png", "name": "CS Ball 5", "price": 800},
    {"file": "csball6.png", "name": "CS Ball 6", "price": 800},
    {"file": "csball7.png", "name": "CS Ball 7", "price": 800},
    {"file": "csball8.png", "name": "CS Ball 8", "price": 800},
]


class ShopScreen(Screen):
    def __init__(self, app):
        super().__init__(app)
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.animation_dir = os.path.join(self.base_dir, "animation")
        self.csball_dir = os.path.join(self.animation_dir, "custom_balls")
        self.active_tab = "balls"
        self._thumb_refs = {}
        self._bkball_thumbs = {}
        self._csball_thumbs = {}
        self.btn_upgrades = None
        self.btn_balls = None
        self.btn_baskets = None
        self.btn_black_edition = None
        self.btn_custom_balls = None
        self.item_buy_rects = []
        self.black_selected_idx = 0
        self.black_swatch_rects = []
        self.black_buy_rect = None
        self.cs_selected_idx = 0
        self.cs_swatch_rects = []
        self.cs_buy_rect = None
        try:
            self._load_thumbs()
            self._load_bkball_thumbs()
            self._load_csball_thumbs()
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

    def _load_bkball_thumbs(self):
        for variant in BKBALL_VARIANTS:
            fname = variant["file"]
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

                box_s = 32
                scale_s = min(box_s / float(w), box_s / float(h))
                nw_s = max(1, int(w * scale_s))
                nh_s = max(1, int(h * scale_s))
                swatch_img = img.resize((nw_s, nh_s), PILImage.Resampling.LANCZOS)
                swatch_surf = pygame.image.fromstring(
                    swatch_img.tobytes(), swatch_img.size, "RGBA"
                ).convert_alpha()

                box_p = 80
                scale_p = min(box_p / float(w), box_p / float(h))
                nw_p = max(1, int(w * scale_p))
                nh_p = max(1, int(h * scale_p))
                preview_img = img.resize((nw_p, nh_p), PILImage.Resampling.LANCZOS)
                preview_surf = pygame.image.fromstring(
                    preview_img.tobytes(), preview_img.size, "RGBA"
                ).convert_alpha()

                self._bkball_thumbs[fname] = {
                    "swatch": swatch_surf,
                    "preview": preview_surf,
                }
            except Exception:
                pass

    def _load_csball_thumbs(self):
        for variant in CSBALL_VARIANTS:
            fname = variant["file"]
            path = os.path.join(self.csball_dir, fname)
            if not os.path.exists(path):
                continue
            try:
                img = PILImage.open(path).convert("RGBA")
                mask = img.getchannel("A").point(lambda a: 255 if a > 100 else 0)
                bbox = mask.getbbox()
                if bbox:
                    img = img.crop(bbox)
                w, h = img.size

                box_s = 32
                scale_s = min(box_s / float(w), box_s / float(h))
                nw_s = max(1, int(w * scale_s))
                nh_s = max(1, int(h * scale_s))
                swatch_img = img.resize((nw_s, nh_s), PILImage.Resampling.LANCZOS)
                swatch_surf = pygame.image.fromstring(
                    swatch_img.tobytes(), swatch_img.size, "RGBA"
                ).convert_alpha()

                box_p = 80
                scale_p = min(box_p / float(w), box_p / float(h))
                nw_p = max(1, int(w * scale_p))
                nh_p = max(1, int(h * scale_p))
                preview_img = img.resize((nw_p, nh_p), PILImage.Resampling.LANCZOS)
                preview_surf = pygame.image.fromstring(
                    preview_img.tobytes(), preview_img.size, "RGBA"
                ).convert_alpha()

                self._csball_thumbs[fname] = {
                    "swatch": swatch_surf,
                    "preview": preview_surf,
                }
            except Exception:
                pass

    def _build_tabs(self):
        tr = self.app.translations[self.app.current_lang]
        tab_w = 95
        self.btn_upgrades = Button(
            (40, 55, tab_w, 35), tr["shop_tab_upgrades"], font_size=11,
            bg_color=(200, 230, 255) if self.active_tab == "upgrades" else (220, 220, 220),
            callback=lambda: self._switch_tab("upgrades"))
        self.btn_balls = Button(
            (140, 55, tab_w, 35), tr["shop_tab_balls"], font_size=11,
            bg_color=(200, 230, 255) if self.active_tab == "balls" else (220, 220, 220),
            callback=lambda: self._switch_tab("balls"))
        self.btn_baskets = Button(
            (240, 55, tab_w, 35), tr["shop_tab_baskets"], font_size=11,
            bg_color=(200, 230, 255) if self.active_tab == "baskets" else (220, 220, 220),
            callback=lambda: self._switch_tab("baskets"))
        is_be = self.active_tab == "black_edition"
        self.btn_black_edition = Button(
            (340, 55, 100, 35), tr["shop_tab_black_edition"], font_size=10,
            bg_color=(60, 50, 30) if is_be else (40, 40, 40),
            text_color=(220, 180, 50) if is_be else (160, 140, 80),
            callback=lambda: self._switch_tab("black_edition"))
        is_cs = self.active_tab == "custom_balls"
        self.btn_custom_balls = Button(
            (445, 55, 100, 35), tr["shop_tab_custom_balls"], font_size=10,
            bg_color=(20, 50, 80) if is_cs else (15, 30, 50),
            text_color=(100, 200, 255) if is_cs else (60, 130, 180),
            callback=lambda: self._switch_tab("custom_balls"))

    def _switch_tab(self, name):
        self.active_tab = name
        self.item_buy_rects = []
        self.black_swatch_rects = []
        self.black_buy_rect = None
        self.cs_swatch_rects = []
        self.cs_buy_rect = None
        self._build_tabs()

    def handle_event(self, event):
        self.btn_upgrades.handle_event(event)
        self.btn_balls.handle_event(event)
        self.btn_baskets.handle_event(event)
        self.btn_black_edition.handle_event(event)
        self.btn_custom_balls.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.active_tab == "black_edition":
                for i, rect in enumerate(self.black_swatch_rects):
                    if rect.collidepoint(event.pos):
                        self.black_selected_idx = i
                        return
                if self.black_buy_rect and self.black_buy_rect.collidepoint(event.pos):
                    self._buy_bkball_set()
            elif self.active_tab == "custom_balls":
                for i, rect in enumerate(self.cs_swatch_rects):
                    if rect.collidepoint(event.pos):
                        self.cs_selected_idx = i
                        return
                if self.cs_buy_rect and self.cs_buy_rect.collidepoint(event.pos):
                    self._buy_csball_set()
            else:
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

    def _buy_bkball_set(self):
        tr = self.app.translations[self.app.current_lang]
        inv = self.app.settings.get("inventory_bkballs", [])

        if all(v["file"] in inv for v in BKBALL_VARIANTS):
            return

        points = self.app.game.get_points()
        if points < SET_PRICE:
            self.app.dialog.show_info(tr["btn_shop"], tr["shop_not_enough"])
            return

        self.app.game.points -= SET_PRICE
        self.app.game.save_game()

        for v in BKBALL_VARIANTS:
            if v["file"] not in inv:
                inv.append(v["file"])
        self.app.settings["inventory_bkballs"] = inv

        self.app.save_settings()

    def _buy_csball_set(self):
        tr = self.app.translations[self.app.current_lang]
        inv = self.app.settings.get("inventory_csballs", [])

        if all(v["file"] in inv for v in CSBALL_VARIANTS):
            return

        points = self.app.game.get_points()
        if points < SET_PRICE:
            self.app.dialog.show_info(tr["btn_shop"], tr["shop_not_enough"])
            return

        self.app.game.points -= SET_PRICE
        self.app.game.save_game()

        for v in CSBALL_VARIANTS:
            if v["file"] not in inv:
                inv.append(v["file"])
        self.app.settings["inventory_csballs"] = inv

        self.app.save_settings()

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
        self.btn_black_edition.draw(surface)
        self.btn_custom_balls.draw(surface)

        self.item_buy_rects = []
        self.black_swatch_rects = []
        self.black_buy_rect = None
        self.cs_swatch_rects = []
        self.cs_buy_rect = None

        if self.active_tab == "upgrades":
            render_text(surface, tr["shop_coming_soon"], font_price, (140, 140, 140), 200, 200, 250)
        elif self.active_tab == "balls":
            inv = self.app.settings.get("inventory_balls", [])
            self._draw_items(surface, BALL_ITEMS, inv, "ball", font_name, font_price, font_small, tr)
        elif self.active_tab == "baskets":
            inv = self.app.settings.get("inventory_baskets", [])
            self._draw_items(surface, BASKET_ITEMS, inv, "basket", font_name, font_price, font_small, tr)
        elif self.active_tab == "black_edition":
            self._draw_black_edition(surface, tr, font_name, font_price, font_small)
        elif self.active_tab == "custom_balls":
            self._draw_custom_balls(surface, tr, font_name, font_price, font_small)

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

    def _draw_black_edition(self, surface, tr, font_name, font_price, font_small):
        inv = self.app.settings.get("inventory_bkballs", [])

        card_rect = pygame.Rect(40, 100, 520, 310)
        pygame.draw.rect(surface, (18, 18, 32), card_rect, border_radius=10)
        pygame.draw.rect(surface, (200, 170, 50), card_rect, 2, border_radius=10)

        title_font = get_font(18, bold=True)
        render_text(surface, "BLACK EDITION", title_font, (220, 180, 50), 40, 108, 520)
        render_text(surface, tr["black_edition_subtitle"], font_small, (140, 120, 70), 40, 132, 520)

        pygame.draw.line(surface, (80, 70, 35), (60, 152), (540, 152), 1)

        variant = BKBALL_VARIANTS[self.black_selected_idx]
        thumbs = self._bkball_thumbs.get(variant["file"])

        preview_bg = pygame.Rect(65, 168, 100, 100)
        pygame.draw.rect(surface, (30, 30, 48), preview_bg, border_radius=8)
        pygame.draw.rect(surface, (80, 70, 40), preview_bg, 1, border_radius=8)

        if thumbs and "preview" in thumbs:
            preview = thumbs["preview"]
            px = preview_bg.centerx - preview.get_width() // 2
            py = preview_bg.centery - preview.get_height() // 2
            surface.blit(preview, (px, py))

        render_text(surface, variant["name"], font_name, (200, 180, 120), 65, 275, 100)

        render_text(surface, tr["black_edition_select_color"], font_small, (140, 120, 70), 200, 162, 200)

        swatch_size = 40
        swatch_gap = 10
        grid_x = 200
        grid_y = 185

        for i, v in enumerate(BKBALL_VARIANTS):
            col = i % 3
            row = i // 3
            sx = grid_x + col * (swatch_size + swatch_gap)
            sy = grid_y + row * (swatch_size + swatch_gap)
            swatch_rect = pygame.Rect(sx, sy, swatch_size, swatch_size)

            is_selected = (i == self.black_selected_idx)
            is_owned = v["file"] in inv

            if is_selected:
                bg = (50, 45, 25)
                border = (220, 180, 50)
                bw = 2
            elif is_owned:
                bg = (25, 40, 25)
                border = (80, 180, 80)
                bw = 1
            else:
                bg = (30, 30, 48)
                border = (60, 60, 80)
                bw = 1

            pygame.draw.rect(surface, bg, swatch_rect, border_radius=5)
            pygame.draw.rect(surface, border, swatch_rect, bw, border_radius=5)

            vthumbs = self._bkball_thumbs.get(v["file"])
            if vthumbs and "swatch" in vthumbs:
                st = vthumbs["swatch"]
                stx = swatch_rect.centerx - st.get_width() // 2
                sty = swatch_rect.centery - st.get_height() // 2
                surface.blit(st, (stx, sty))

            self.black_swatch_rects.append(swatch_rect)

        pygame.draw.line(surface, (80, 70, 35), (60, 350), (540, 350), 1)

        all_owned = all(v["file"] in inv for v in BKBALL_VARIANTS)
        if all_owned:
            render_text(surface, tr["shop_set_owned"], font_name, (100, 200, 100), 60, 360, 200)
        else:
            price_text = tr["shop_price"].format(SET_PRICE)
            render_text(surface, price_text, font_price, (220, 180, 50), 60, 365, 200)

            btn_rect = pygame.Rect(400, 355, 130, 38)
            mouse_over = btn_rect.collidepoint(pygame.mouse.get_pos())
            color = (240, 200, 60) if mouse_over else (200, 170, 40)
            pygame.draw.rect(surface, color, btn_rect, border_radius=6)
            pygame.draw.rect(surface, (140, 110, 25), btn_rect, 1, border_radius=6)
            buy_txt = strip_emoji(tr["shop_set_buy"])
            buy_font = get_font(14, bold=True)
            buy_surf = buy_font.render(buy_txt, True, (30, 25, 10))
            surface.blit(buy_surf, (btn_rect.centerx - buy_surf.get_width() // 2,
                                    btn_rect.centery - buy_surf.get_height() // 2))
            self.black_buy_rect = btn_rect

    def _draw_custom_balls(self, surface, tr, font_name, font_price, font_small):
        inv = self.app.settings.get("inventory_csballs", [])

        card_rect = pygame.Rect(40, 100, 520, 310)
        pygame.draw.rect(surface, (52, 62, 80), card_rect, border_radius=10)
        pygame.draw.rect(surface, (140, 180, 220), card_rect, 2, border_radius=10)

        title_font = get_font(18, bold=True)
        render_text(surface, "CUSTOM BALLS", title_font, (180, 220, 255), 40, 108, 520)
        render_text(surface, tr["custom_balls_subtitle"], font_small, (120, 160, 200), 40, 132, 520)

        pygame.draw.line(surface, (90, 110, 140), (60, 152), (540, 152), 1)

        variant = CSBALL_VARIANTS[self.cs_selected_idx]
        thumbs = self._csball_thumbs.get(variant["file"])

        preview_bg = pygame.Rect(65, 168, 100, 100)
        pygame.draw.rect(surface, (40, 50, 68), preview_bg, border_radius=8)
        pygame.draw.rect(surface, (100, 140, 180), preview_bg, 1, border_radius=8)

        if thumbs and "preview" in thumbs:
            preview = thumbs["preview"]
            px = preview_bg.centerx - preview.get_width() // 2
            py = preview_bg.centery - preview.get_height() // 2
            surface.blit(preview, (px, py))

        render_text(surface, variant["name"], font_name, (170, 210, 250), 65, 275, 100)

        render_text(surface, tr["custom_balls_select"], font_small, (120, 160, 200), 200, 162, 200)

        swatch_size = 38
        swatch_gap = 8
        grid_x = 200
        grid_y = 185

        for i, v in enumerate(CSBALL_VARIANTS):
            col = i % 4
            row = i // 4
            sx = grid_x + col * (swatch_size + swatch_gap)
            sy = grid_y + row * (swatch_size + swatch_gap)
            swatch_rect = pygame.Rect(sx, sy, swatch_size, swatch_size)

            is_selected = (i == self.cs_selected_idx)
            is_owned = v["file"] in inv

            if is_selected:
                bg = (80, 100, 130)
                border = (180, 220, 255)
                bw = 2
            elif is_owned:
                bg = (30, 55, 40)
                border = (80, 180, 100)
                bw = 1
            else:
                bg = (40, 50, 68)
                border = (70, 90, 120)
                bw = 1

            pygame.draw.rect(surface, bg, swatch_rect, border_radius=5)
            pygame.draw.rect(surface, border, swatch_rect, bw, border_radius=5)

            vthumbs = self._csball_thumbs.get(v["file"])
            if vthumbs and "swatch" in vthumbs:
                st = vthumbs["swatch"]
                stx = swatch_rect.centerx - st.get_width() // 2
                sty = swatch_rect.centery - st.get_height() // 2
                surface.blit(st, (stx, sty))

            self.cs_swatch_rects.append(swatch_rect)

        pygame.draw.line(surface, (90, 110, 140), (60, 350), (540, 350), 1)

        all_owned = all(v["file"] in inv for v in CSBALL_VARIANTS)
        if all_owned:
            render_text(surface, tr["shop_set_owned"], font_name, (100, 200, 100), 60, 360, 200)
        else:
            price_text = tr["shop_price"].format(SET_PRICE)
            render_text(surface, price_text, font_price, (180, 220, 255), 60, 365, 200)

            btn_rect = pygame.Rect(400, 355, 130, 38)
            mouse_over = btn_rect.collidepoint(pygame.mouse.get_pos())
            color = (160, 200, 240) if mouse_over else (120, 160, 210)
            pygame.draw.rect(surface, color, btn_rect, border_radius=6)
            pygame.draw.rect(surface, (80, 110, 150), btn_rect, 1, border_radius=6)
            buy_txt = strip_emoji(tr["shop_set_buy"])
            buy_font = get_font(14, bold=True)
            buy_surf = buy_font.render(buy_txt, True, (20, 30, 50))
            surface.blit(buy_surf, (btn_rect.centerx - buy_surf.get_width() // 2,
                                    btn_rect.centery - buy_surf.get_height() // 2))
            self.cs_buy_rect = btn_rect
