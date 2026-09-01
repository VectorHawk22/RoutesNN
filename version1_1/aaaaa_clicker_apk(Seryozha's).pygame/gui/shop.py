# -*- coding: utf-8 -*-
"""Shop screen: upgrades/balls/baskets tabs and the premium sets."""
import os

from gui.screen import Screen
from gui.button import KButton
from gui.utils import strip_emoji
from gui.painter import Painter
from animation.assets import load_pil_cropped, pil_to_texture

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


def _thumb(path, box):
    img = load_pil_cropped(os.path.basename(path), os.path.dirname(path))
    if img is None:
        return None
    w, h = img.size
    scale = min(box / float(w), box / float(h))
    nw = max(1, int(w * scale))
    nh = max(1, int(h * scale))
    return pil_to_texture(img.resize((nw, nh)))


class ShopScreen(Screen):
    def __init__(self, app):
        super().__init__(app)
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.animation_dir = os.path.join(self.base_dir, "animation")
        self.csball_dir = os.path.join(self.animation_dir, "custom_balls")

        self.active_tab = "balls"
        self._thumbs = {}
        self._bk_thumbs = {}
        self._cs_thumbs = {}
        try:
            self._load_thumbs()
        except Exception as e:
            print(f"Shop thumbs load error: {e}")

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

        self._build_tabs()

    def _load_thumbs(self):
        for fname in [i["file"] for i in BALL_ITEMS + BASKET_ITEMS]:
            path = os.path.join(self.animation_dir, fname)
            if os.path.exists(path):
                tex = _thumb(path, 48)
                if tex:
                    self._thumbs[fname] = tex
        for v in BKBALL_VARIANTS:
            path = os.path.join(self.animation_dir, v["file"])
            if os.path.exists(path):
                s = _thumb(path, 32)
                p = _thumb(path, 80)
                if s is not None and p is not None:
                    self._bk_thumbs[v["file"]] = {"swatch": s, "preview": p}
        for v in CSBALL_VARIANTS:
            path = os.path.join(self.csball_dir, v["file"])
            if os.path.exists(path):
                s = _thumb(path, 32)
                p = _thumb(path, 80)
                if s is not None and p is not None:
                    self._cs_thumbs[v["file"]] = {"swatch": s, "preview": p}

    def _clear(self):
        for w in list(self.children):
            self.remove_widget(w)

    def _build_tabs(self):
        tr = self.app.translations[self.app.current_lang]
        tab_w = 95
        self.btn_upgrades = KButton(
            (40, 55, tab_w, 35), tr["shop_tab_upgrades"], font_size=11,
            bg_color=(200, 230, 255) if self.active_tab == "upgrades" else (220, 220, 220),
            callback=lambda: self._switch_tab("upgrades"))
        self.btn_balls = KButton(
            (140, 55, tab_w, 35), tr["shop_tab_balls"], font_size=11,
            bg_color=(200, 230, 255) if self.active_tab == "balls" else (220, 220, 220),
            callback=lambda: self._switch_tab("balls"))
        self.btn_baskets = KButton(
            (240, 55, tab_w, 35), tr["shop_tab_baskets"], font_size=11,
            bg_color=(200, 230, 255) if self.active_tab == "baskets" else (220, 220, 220),
            callback=lambda: self._switch_tab("baskets"))
        is_be = self.active_tab == "black_edition"
        self.btn_black_edition = KButton(
            (340, 55, 100, 35), tr["shop_tab_black_edition"], font_size=10,
            bg_color=(60, 50, 30) if is_be else (40, 40, 40),
            text_color=(220, 180, 50) if is_be else (160, 140, 80),
            callback=lambda: self._switch_tab("black_edition"))
        is_cs = self.active_tab == "custom_balls"
        self.btn_custom_balls = KButton(
            (445, 55, 100, 35), tr["shop_tab_custom_balls"], font_size=10,
            bg_color=(20, 50, 80) if is_cs else (15, 30, 50),
            text_color=(100, 200, 255) if is_cs else (60, 130, 180),
            callback=lambda: self._switch_tab("custom_balls"))
        for btn in (self.btn_upgrades, self.btn_balls, self.btn_baskets,
                    self.btn_black_edition, self.btn_custom_balls):
            self.add_widget(btn)

    def _switch_tab(self, name):
        self.active_tab = name
        self.item_buy_rects = []
        self.black_swatch_rects = []
        self.black_buy_rect = None
        self.cs_swatch_rects = []
        self.cs_buy_rect = None
        self._clear()
        self._build_tabs()

    def touch_down(self, x, y):
        if self.active_tab == "black_edition":
            for i, rect in enumerate(self.black_swatch_rects):
                if self._hit(rect, x, y):
                    self.black_selected_idx = i
                    return True
            if self.black_buy_rect and self._hit(self.black_buy_rect, x, y):
                self._buy_bkball_set()
                return True
        elif self.active_tab == "custom_balls":
            for i, rect in enumerate(self.cs_swatch_rects):
                if self._hit(rect, x, y):
                    self.cs_selected_idx = i
                    return True
            if self.cs_buy_rect and self._hit(self.cs_buy_rect, x, y):
                self._buy_csball_set()
                return True
        else:
            for rect, item, kind in self.item_buy_rects:
                if self._hit(rect, x, y):
                    self._buy_item(item, kind)
                    return True
        return False

    @staticmethod
    def _hit(rect, x, y):
        rx, ry, rw, rh = rect
        return rx <= x <= rx + rw and ry <= y <= ry + rh

    def _buy_item(self, item, kind):
        tr = self.app.translations[self.app.current_lang]
        points = self.app.game.get_points()
        if points < item["price"]:
            self.app.dialog.show_info(tr["btn_shop"], tr["shop_not_enough"])
            return
        self.app.game.points -= item["price"]
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
        if self.app.game.get_points() < SET_PRICE:
            self.app.dialog.show_info(tr["btn_shop"], tr["shop_not_enough"])
            return
        self.app.game.points -= SET_PRICE
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
        if self.app.game.get_points() < SET_PRICE:
            self.app.dialog.show_info(tr["btn_shop"], tr["shop_not_enough"])
            return
        self.app.game.points -= SET_PRICE
        for v in CSBALL_VARIANTS:
            if v["file"] not in inv:
                inv.append(v["file"])
        self.app.settings["inventory_csballs"] = inv
        self.app.save_settings()

    def draw(self, painter):
        tr = self.app.translations[self.app.current_lang]
        painter.text(tr["btn_shop"], 20, (0, 0, 0), 40, 15,
                     bold=True, max_width=520)

        self.item_buy_rects = []
        self.black_swatch_rects = []
        self.black_buy_rect = None
        self.cs_swatch_rects = []
        self.cs_buy_rect = None

        if self.active_tab == "upgrades":
            painter.text(tr["shop_coming_soon"], 14, (140, 140, 140),
                         200, 200, max_width=250, align="center")
        elif self.active_tab == "balls":
            inv = self.app.settings.get("inventory_balls", [])
            self._draw_items(painter, BALL_ITEMS, inv, "ball", tr)
        elif self.active_tab == "baskets":
            inv = self.app.settings.get("inventory_baskets", [])
            self._draw_items(painter, BASKET_ITEMS, inv, "basket", tr)
        elif self.active_tab == "black_edition":
            self._draw_black_edition(painter, tr)
        elif self.active_tab == "custom_balls":
            self._draw_custom_balls(painter, tr)

    def _draw_items(self, painter, items, owned, kind, tr):
        y = 105
        for item in items:
            painter.rounded(40, y, 520, 75, (245, 245, 245), radius=6)
            painter.outline(40, y, 520, 75, (180, 180, 180))

            thumb = self._thumbs.get(item["file"])
            if thumb is not None:
                ty = y + (75 - thumb.height) // 2
                painter.image(thumb, 52, ty)

            painter.text(item["name"], 14, (0, 0, 0), 115, y + 10,
                         bold=True, max_width=250)

            is_owned = item["file"] in owned
            if is_owned:
                painter.text(tr["shop_owned"], 13, (0, 150, 0),
                             115, y + 38, max_width=250)
            else:
                price_text = tr["shop_price"].format(item["price"])
                painter.text(price_text, 13, (180, 90, 0),
                             115, y + 38, max_width=250)
                btn_rect = (500 - 100, y + 18, 85, 35)
                mouse = self.app.hover_pos
                hover = self._hit(btn_rect, *mouse) if mouse else False
                color = (160, 255, 160) if hover else (144, 238, 144)
                painter.rounded(*btn_rect, color, radius=6)
                painter.outline(*btn_rect, (100, 100, 100))
                buy_txt = strip_emoji(tr["shop_buy"])
                painter.text_centered_in(buy_txt, 13, (0, 0, 0),
                                         *btn_rect)
                self.item_buy_rects.append((btn_rect, item, kind))
            y += 85

    def _draw_black_edition(self, painter, tr):
        inv = self.app.settings.get("inventory_bkballs", [])
        painter.rounded(40, 100, 520, 310, (18, 18, 32), radius=10)
        painter.outline(40, 100, 520, 310, (200, 170, 50), width=2)
        painter.text("BLACK EDITION", 18, (220, 180, 50), 40, 108,
                     bold=True, max_width=520)
        painter.text(tr["black_edition_subtitle"], 11, (140, 120, 70),
                     40, 132, max_width=520)
        painter.line(60, 152, 540, 152, (80, 70, 35))

        variant = BKBALL_VARIANTS[self.black_selected_idx]
        thumbs = self._bk_thumbs.get(variant["file"])

        painter.rounded(65, 168, 100, 100, (30, 30, 48), radius=8)
        painter.outline(65, 168, 100, 100, (80, 70, 40))
        if thumbs:
            preview = thumbs["preview"]
            px = 65 + (100 - preview.width) // 2
            py = 168 + (100 - preview.height) // 2
            painter.image(preview, px, py)
        painter.text(variant["name"], 14, (200, 180, 120), 65, 275,
                     bold=True, max_width=100)

        painter.text(tr["black_edition_select_color"], 11, (140, 120, 70),
                     200, 162, max_width=200)

        swatch_size = 40
        swatch_gap = 10
        grid_x, grid_y = 200, 185

        for i, v in enumerate(BKBALL_VARIANTS):
            col = i % 3
            row = i // 3
            sx = grid_x + col * (swatch_size + swatch_gap)
            sy = grid_y + row * (swatch_size + swatch_gap)
            swatch_rect = (sx, sy, swatch_size, swatch_size)

            is_selected = i == self.black_selected_idx
            is_owned = v["file"] in inv
            if is_selected:
                bg, border, bw = (50, 45, 25), (220, 180, 50), 2
            elif is_owned:
                bg, border, bw = (25, 40, 25), (80, 180, 80), 1
            else:
                bg, border, bw = (30, 30, 48), (60, 60, 80), 1
            painter.rounded(*swatch_rect, bg, radius=5)
            painter.outline(*swatch_rect, border, width=bw)

            vthumbs = self._bk_thumbs.get(v["file"])
            if vthumbs:
                st = vthumbs["swatch"]
                stx = sx + (swatch_size - st.width) // 2
                sty = sy + (swatch_size - st.height) // 2
                painter.image(st, stx, sty)
            self.black_swatch_rects.append(swatch_rect)

        painter.line(60, 350, 540, 350, (80, 70, 35))

        all_owned = all(v["file"] in inv for v in BKBALL_VARIANTS)
        if all_owned:
            painter.text(tr["shop_set_owned"], 14, (100, 200, 100), 60, 360,
                         bold=True, max_width=200)
        else:
            painter.text(tr["shop_price"].format(SET_PRICE), 13,
                         (220, 180, 50), 60, 365, max_width=200)
            btn_rect = (400, 355, 130, 38)
            mouse = self.app.hover_pos
            hover = self._hit(btn_rect, *mouse) if mouse else False
            color = (240, 200, 60) if hover else (200, 170, 40)
            painter.rounded(*btn_rect, color, radius=6)
            painter.outline(*btn_rect, (140, 110, 25))
            buy_txt = strip_emoji(tr["shop_set_buy"])
            painter.text_centered_in(buy_txt, 14, (30, 25, 10), *btn_rect,
                                     bold=True)
            self.black_buy_rect = btn_rect

    def _draw_custom_balls(self, painter, tr):
        inv = self.app.settings.get("inventory_csballs", [])
        painter.rounded(40, 100, 520, 310, (52, 62, 80), radius=10)
        painter.outline(40, 100, 520, 310, (140, 180, 220), width=2)
        painter.text("CUSTOM BALLS", 18, (180, 220, 255), 40, 108,
                     bold=True, max_width=520)
        painter.text(tr["custom_balls_subtitle"], 11, (120, 160, 200),
                     40, 132, max_width=520)
        painter.line(60, 152, 540, 152, (90, 110, 140))

        variant = CSBALL_VARIANTS[self.cs_selected_idx]
        thumbs = self._cs_thumbs.get(variant["file"])

        painter.rounded(65, 168, 100, 100, (40, 50, 68), radius=8)
        painter.outline(65, 168, 100, 100, (100, 140, 180))
        if thumbs:
            preview = thumbs["preview"]
            px = 65 + (100 - preview.width) // 2
            py = 168 + (100 - preview.height) // 2
            painter.image(preview, px, py)
        painter.text(variant["name"], 14, (170, 210, 250), 65, 275,
                     bold=True, max_width=100)

        painter.text(tr["custom_balls_select"], 11, (120, 160, 200),
                     200, 162, max_width=200)

        swatch_size = 38
        swatch_gap = 8
        grid_x, grid_y = 200, 185

        for i, v in enumerate(CSBALL_VARIANTS):
            col = i % 4
            row = i // 4
            sx = grid_x + col * (swatch_size + swatch_gap)
            sy = grid_y + row * (swatch_size + swatch_gap)
            swatch_rect = (sx, sy, swatch_size, swatch_size)

            is_selected = i == self.cs_selected_idx
            is_owned = v["file"] in inv
            if is_selected:
                bg, border, bw = (80, 100, 130), (180, 220, 255), 2
            elif is_owned:
                bg, border, bw = (30, 55, 40), (80, 180, 100), 1
            else:
                bg, border, bw = (40, 50, 68), (70, 90, 120), 1
            painter.rounded(*swatch_rect, bg, radius=5)
            painter.outline(*swatch_rect, border, width=bw)

            vthumbs = self._cs_thumbs.get(v["file"])
            if vthumbs:
                st = vthumbs["swatch"]
                stx = sx + (swatch_size - st.width) // 2
                sty = sy + (swatch_size - st.height) // 2
                painter.image(st, stx, sty)
            self.cs_swatch_rects.append(swatch_rect)

        painter.line(60, 350, 540, 350, (90, 110, 140))

        all_owned = all(v["file"] in inv for v in CSBALL_VARIANTS)
        if all_owned:
            painter.text(tr["shop_set_owned"], 14, (100, 200, 100), 60, 360,
                         bold=True, max_width=200)
        else:
            painter.text(tr["shop_price"].format(SET_PRICE), 13,
                         (180, 220, 255), 60, 365, max_width=200)
            btn_rect = (400, 355, 130, 38)
            mouse = self.app.hover_pos
            hover = self._hit(btn_rect, *mouse) if mouse else False
            color = (160, 200, 240) if hover else (120, 160, 210)
            painter.rounded(*btn_rect, color, radius=6)
            painter.outline(*btn_rect, (80, 110, 150))
            buy_txt = strip_emoji(tr["shop_set_buy"])
            painter.text_centered_in(buy_txt, 14, (20, 30, 50), *btn_rect,
                                     bold=True)
            self.cs_buy_rect = btn_rect

    def update(self):
        pass