# -*- coding: utf-8 -*-
"""Inventory screen: potions tab + skins (balls/hoops) tab with scrolling."""
import os

from gui.screen import Screen
from gui.button import KButton
from gui.utils import make_label
from gui.painter import Painter, BOARD_W
from animation.assets import load_pil_cropped, pil_to_texture

# Content view for the skins tab must not reach the Back button (which starts
# at board y=440). Stop before it so scrolled cells never draw over it.
_SKIN_VIEW_BOTTOM = 437

BALL_SKINS = ["ball1.png", "ball2.png", "ball3.png", "ball4.png", "ball5.png"]
BASKET_SKINS = ["basket.png", "basket2.png", "basket3.png", "basket4.png"]
BKBALL_SKINS = ["bkball1.png", "bkball2.png", "bkball3.png",
                "bkball4.png", "bkball5.png", "bkball6.png"]
CSBALL_SKINS = [f"csball{i}.png" for i in range(1, 9)]


def _thumb_texture(path, box=56):
    try:
        img = load_pil_cropped(os.path.basename(path), os.path.dirname(path))
        if img is None:
            return None
        w, h = img.size
        scale = min(box / float(w), box / float(h))
        nw = max(1, int(w * scale))
        nh = max(1, int(h * scale))
        return pil_to_texture(img.resize((nw, nh)))
    except Exception:
        return None


class InventoryScreen(Screen):
    def __init__(self, app):
        super().__init__(app)
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.animation_dir = os.path.join(self.base_dir, "animation")
        self.csball_dir = os.path.join(self.animation_dir, "custom_balls")
        self.images_dir = os.path.join(self.base_dir, "images")

        self.active_tab = "potions"
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

        self.skin_scroll = 0
        self._scroll_dragging = False
        self._scroll_drag_offset = 0
        self._scrollbar_thumb = None
        self._scroll_view_top = 135
        self._scroll_view_bottom = _SKIN_VIEW_BOTTOM
        self._scroll_track_h = 0
        self._scroll_track_rect = None

        self._build_ui()

    def _load_potion_images(self):
        for name, fname in [("full", "potionthatgives2xcoins.png"),
                            ("empty", "emptypotionthatgives2xcoins.png")]:
            path = os.path.join(self.images_dir, fname)
            if os.path.exists(path):
                try:
                    tex = _thumb_texture(path, box=80)
                    if name == "full":
                        self.potion_img = tex
                    else:
                        self.potion_empty_img = tex
                except Exception as e:
                    print(f"Potion image load error ({fname}): {e}")

    def _load_skin_thumbnails(self):
        for fname in BALL_SKINS + BASKET_SKINS + BKBALL_SKINS:
            path = os.path.join(self.animation_dir, fname)
            if os.path.exists(path):
                tex = _thumb_texture(path)
                if tex:
                    self.skin_thumbs[fname] = tex
        for fname in CSBALL_SKINS:
            path = os.path.join(self.csball_dir, fname)
            if os.path.exists(path):
                tex = _thumb_texture(path)
                if tex:
                    self.skin_thumbs[fname] = tex

    def _clear(self):
        for w in list(self.children):
            self.remove_widget(w)

    def _build_ui(self):
        self._clear()
        tr = self.app.translations[self.app.current_lang]
        self.btn_tab_potions = KButton(
            (40, 60, 200, 38), tr["tab_potions"], font_size=13,
            bg_color=(200, 230, 255) if self.active_tab == "potions" else (220, 220, 220),
            callback=lambda: self._switch_tab("potions"))
        self.btn_tab_skins = KButton(
            (260, 60, 200, 38), tr["tab_skins"], font_size=13,
            bg_color=(200, 230, 255) if self.active_tab == "skins" else (220, 220, 220),
            callback=lambda: self._switch_tab("skins"))
        self.add_widget(self.btn_tab_potions)
        self.add_widget(self.btn_tab_skins)

        if self.active_tab == "potions":
            self.btn_use_potion = KButton(
                (40, 340, 160, 35), tr["potion_inactive"], font_size=11,
                bg_color=(180, 180, 180), callback=self._use_potion)
            self.add_widget(self.btn_use_potion)

    def _switch_tab(self, name):
        self.active_tab = name
        if name != "skins":
            self.skin_scroll = 0
        self._build_ui()

    def _use_potion(self):
        if self.app.game.activate_potion():
            self._potion_timer = 180
            tr = self.app.translations[self.app.current_lang]
            self.btn_use_potion.set_text(tr["use"])

    # -- skin grid helpers --------------------------------------------
    def _skins_content_bottom(self):
        nball = (len(self.app.settings.get("inventory_balls", [])) +
                 len(self.app.settings.get("inventory_bkballs", [])) +
                 len(self.app.settings.get("inventory_csballs", [])))
        nbasket = len(self.app.settings.get("inventory_baskets", []))
        rows = (nball + 4) // 5 if nball else 0
        grid_h = rows * (100 + 6)
        baskets_y = 135 + grid_h + 15
        return baskets_y + 25 + (100 if nbasket else 0) + 8

    def _skins_max_scroll(self):
        return max(0, self._skins_content_bottom() - _SKIN_VIEW_BOTTOM)

    # -- touch --------------------------------------------------------
    def touch_down(self, x, y):
        if self.active_tab != "skins":
            return False
        max_scroll = self._skins_max_scroll()
        if self._scrollbar_thumb and self._rect_hit(self._scrollbar_thumb, x, y):
            self._scroll_dragging = True
            self._scroll_drag_offset = y - self._scrollbar_thumb[1]
            self.skin_scroll = max(0, min(max_scroll, self.skin_scroll))
            return True
        for (kind, fname), rect in self.skin_rects.items():
            if self._rect_hit(rect, x, y):
                key = "skin_ball" if kind == "ball" else "skin_basket"
                self.app.settings[key] = fname
                self.app.save_settings()
                self.app.apply_skins()
                return True
        self.touch_scroll(x, y)
        return False

    def touch_scroll(self, x, y, source="position"):
        max_scroll = self._skins_max_scroll()
        if source == "wheel":
            step = 40 if y > 0 else -40
            self.skin_scroll = max(0, min(max_scroll, self.skin_scroll + step))
        else:
            view_top = self._scroll_view_top
            view_bottom = self._scroll_view_bottom
            track_h = max(1, view_bottom - view_top)
            if max_scroll > 0 and self._scroll_track_h and (y - view_top) >= 0:
                frac = (y - view_top) / self._scroll_track_h
                self.skin_scroll = max(0, min(max_scroll, frac * max_scroll))
        return True

    def touch_move(self, x, y):
        if self.active_tab != "skins" or not self._scroll_dragging:
            return False
        max_scroll = self._skins_max_scroll()
        view_top = self._scroll_view_top
        track_h = max(1, self._scroll_track_h)
        if track_h > 0:
            frac = max(0.0,
                       min(1.0, (y - self._scroll_drag_offset - view_top) / track_h))
            self.skin_scroll = max(0, int(frac * max_scroll))
        return True

    def touch_up(self, x, y):
        self._scroll_dragging = False
        return False

    @staticmethod
    def _rect_hit(rect, x, y):
        rx, ry, rw, rh = rect
        return rx <= x <= rx + rw and ry <= y <= ry + rh

    def handle_wheel(self, delta):
        if self.active_tab == "skins":
            self.touch_scroll(0, delta, source="wheel")
            return True
        return False

    # -- draw ---------------------------------------------------------
    def update(self):
        if self._potion_timer > 0:
            self._potion_timer -= 1

    def draw(self, painter):
        tr = self.app.translations[self.app.current_lang]
        painter.text(tr["inventory"], 18, (0, 0, 0), 40, 15, bold=True,
                     max_width=520)
        if self.active_tab == "potions":
            self._draw_potions_tab(painter, tr)
        else:
            self._draw_skins_tab(painter, tr)

    def _draw_potions_tab(self, painter, tr):
        painter.rounded(40, 115, 300, 180, (255, 255, 200), radius=8)
        painter.outline(40, 115, 300, 180, (200, 180, 50), width=2)

        is_active = self.app.game.is_potion_active()
        tex = self.potion_empty_img if is_active else self.potion_img
        if tex is not None:
            painter.image(tex, 55, 145)
        else:
            painter.text("E", 32, (100, 100, 100), 75, 165)

        painter.text(tr["potion"], 13, (0, 0, 0), 150, 140, max_width=180)

        if self.btn_use_potion is not None:
            self.btn_use_potion.set_text(
                tr["use"] if is_active else tr["potion_inactive"])

        time_left = self.app.game.get_potion_time_left()
        if time_left > 0:
            painter.text(tr["potion_active"].format(time_left), 11,
                         (0, 120, 0), 55, 255, max_width=270)
        else:
            painter.text(tr["potion_inactive"], 11, (100, 100, 100),
                         55, 255, max_width=270)

        if self._potion_timer > 120:
            painter.rect(40, 115, 300, 180, (0, 255, 0, 60))

    def _draw_skins_tab(self, painter, tr):
        current_ball = self.app.settings.get("skin_ball", "")
        current_basket = self.app.settings.get("skin_basket", "")
        self.skin_rects = {}

        owned_balls = self.app.settings.get("inventory_balls", [])
        owned_baskets = self.app.settings.get("inventory_baskets", [])
        owned_bkballs = self.app.settings.get("inventory_bkballs", [])
        owned_csballs = self.app.settings.get("inventory_csballs", [])

        all_ball_skins = list(owned_balls) + list(owned_bkballs) + list(owned_csballs)

        max_scroll = self._skins_max_scroll()
        self.skin_scroll = max(0, min(max_scroll, self.skin_scroll))
        scroll = self.skin_scroll

        cell_w = 90
        cell_h = 100
        gap = 6
        cols = 5
        x_start = 40
        y_start = 135
        view_top = 105
        view_bottom = _SKIN_VIEW_BOTTOM

        painter.text(tr["skins_balls"] + ":", 13, (0, 0, 0),
                     40, 110 - scroll, max_width=520)

        for i, fname in enumerate(all_ball_skins):
            col = i % cols
            row = i // cols
            x = x_start + col * (cell_w + gap)
            y = y_start + row * (cell_h + gap) - scroll
            if y + cell_h < view_top or y > view_bottom:
                continue
            self._draw_skin_cell(painter, x, y, cell_w, cell_h, fname,
                                 fname == current_ball, "ball")

        baskets_y = y_start + ((len(all_ball_skins) + cols - 1) // cols) * (cell_h + gap) + 15 - scroll
        painter.text(tr["skins_baskets"] + ":", 13, (0, 0, 0),
                     40, baskets_y, max_width=520)
        for i, fname in enumerate(owned_baskets):
            x = 40 + i * 110
            y = baskets_y + 25
            if y + 100 < view_top or y > view_bottom:
                continue
            self._draw_skin_cell(painter, x, y, 100, 100, fname,
                                 fname == current_basket, "basket")

        self._draw_scrollbar(painter, view_top, view_bottom, max_scroll)

    def _draw_skin_cell(self, painter, x, y, cell_w, cell_h, fname, is_sel, kind):
        border_color = (0, 120, 215) if is_sel else (180, 180, 180)
        bg_color = (220, 240, 255) if is_sel else (240, 240, 240)
        painter.rounded(x, y, cell_w, cell_h, bg_color, radius=6)
        painter.outline(x, y, cell_w, cell_h, border_color, width=2)

        thumb = self.skin_thumbs.get(fname)
        if thumb is not None:
            painter.image(thumb, x + (cell_w - thumb.width) // 2, y + 8)

        name_label = fname.replace(".png", "")
        painter.text(name_label, 11, (80, 80, 80),
                     x + (cell_w - 30) // 2, y + cell_h - 18, max_width=70)

        self.skin_rects[(kind, fname)] = (x, y, cell_w, cell_h)

    def _draw_scrollbar(self, painter, view_top, view_bottom, max_scroll):
        self._scroll_view_top = view_top
        self._scroll_view_bottom = view_bottom
        track_h = max(1, view_bottom - view_top)
        self._scroll_track_h = track_h

        if max_scroll <= 0:
            self._scrollbar_thumb = None
            return

        x = BOARD_W - 14
        painter.rounded(x, view_top, 8, track_h, (205, 205, 205), radius=4)
        self._scroll_track_rect = (x, view_top, 8, track_h)

        frac = self.skin_scroll / max_scroll
        thumb_h = max(24, int(track_h * (track_h / (max_scroll + track_h))))
        thumb_y = view_top + int(frac * (track_h - thumb_h))
        painter.rounded(x, thumb_y, 8, thumb_h, (120, 120, 120), radius=4)
        self._scrollbar_thumb = (x, thumb_y, 8, thumb_h)