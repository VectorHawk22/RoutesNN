# -*- coding: utf-8 -*-
"""Game screen: animated court, click challenge, score overlay, nav menu."""
import os

from gui.screen import Screen
from gui.button import KButton
from gui.painter import Painter
from gui.utils import make_label
from animation.court_success import CourtSuccess
from animation.court_fail import CourtFail

COURT_X = 25
COURT_Y = 10
COURT_W = 425
COURT_H = 265


class GameScreen(Screen):
    def __init__(self, app):
        super().__init__(app)

        skin_ball = self.app.settings.get("skin_ball", "ball1.png")
        skin_basket = self.app.settings.get("skin_basket", "basket.png")
        self.court_success = CourtSuccess(ball_file=skin_ball,
                                          basket_file=skin_basket)
        self.court_fail = CourtFail(ball_file=skin_ball,
                                    basket_file=skin_basket)

        self.game_state = "idle"
        self.click_count = 0
        self.challenge_timer = 0
        self.result_type = None

        self.btn_click = None
        self.nav_buttons = []
        self._build_click_button()
        self._build_nav()
        self._update_button_text()

        self._float_text = ""
        self._float_y = 0.0
        self._float_color = (0, 0, 0)
        self._float_timer = 0
        self._flash_timer = 0
        self._flash_color = (0, 0, 0)

        self._idle_timer = 0
        self._idle_threshold = 600

    def _build_click_button(self):
        if self.btn_click:
            self.remove_widget(self.btn_click)
        self.btn_click = KButton(
            (30, 350, 210, 45), "", font_size=13,
            bg_color=(173, 216, 230), callback=self._on_button_click)
        self.add_widget(self.btn_click)

    def _build_nav(self):
        for btn in self.nav_buttons:
            self.remove_widget(btn)
        tr = self.app.translations[self.app.current_lang]
        self.nav_buttons = [
            KButton((460, 15, 130, 80), tr["btn_inventory"], font_size=11,
                    bg_color=(240, 128, 128),
                    callback=lambda: self.app.switch_screen("inventory")),
            KButton((460, 105, 130, 80), tr["btn_shop"], font_size=11,
                    bg_color=(144, 238, 144),
                    callback=lambda: self.app.switch_screen("shop")),
            KButton((460, 195, 130, 80), tr["btn_authors"], font_size=11,
                    bg_color=(255, 255, 180),
                    callback=lambda: self.app.switch_screen("authors")),
            KButton((460, 285, 130, 80), tr["btn_settings"], font_size=11,
                    bg_color=(200, 200, 200),
                    callback=lambda: self.app.switch_screen("settings")),
        ]
        for btn in self.nav_buttons:
            self.add_widget(btn)

    def apply_skins(self):
        ball_file = self.app.settings.get("skin_ball", "ball1.png")
        basket_file = self.app.settings.get("skin_basket", "basket.png")
        for court in (self.court_success, self.court_fail):
            court.set_skins(ball_file, basket_file)

    def set_language(self):
        self._build_nav()
        self._update_button_text()

    def _reset_idle_timer(self):
        self._idle_timer = 0
        for court in (self.court_success, self.court_fail):
            court.set_idle_ball_man(False)

    def _update_button_text(self):
        tr = self.app.translations[self.app.current_lang]
        if self.game_state == "idle":
            self.btn_click.set_text(tr["start_challenge"])
            self.btn_click.bg_color = (173, 216, 230)
        elif self.game_state == "challenging":
            self.btn_click.set_text(tr["click_now"])
            self.btn_click.bg_color = (255, 100, 100)
        elif self.game_state == "result":
            self.btn_click.set_text(tr["button_click"])
            self.btn_click.bg_color = (173, 216, 230)

    def _on_button_click(self):
        self._reset_idle_timer()
        if self.game_state == "idle":
            self._start_challenge()
        elif self.game_state == "challenging":
            self.click_count += 1
        elif self.game_state == "result":
            self._process_result()

    def _start_challenge(self):
        self.game_state = "challenging"
        self.click_count = 0
        self.challenge_timer = 60
        self.result_type = None
        self._update_button_text()

    def _end_challenge(self):
        self.game_state = "result"
        self._update_button_text()

    def _process_result(self):
        success, _, added = self.app.game.try_add_point(self.click_count)
        self.court_success.stop()
        self.court_fail.stop()

        if success:
            self.court_success.start_animation(COURT_W, COURT_H)
            self.result_type = "hit"
        else:
            self.court_fail.start_animation(COURT_W, COURT_H)
            self.result_type = "miss"

        self.game_state = "idle"
        self._update_button_text()

        if success:
            self._float_text = f"+{added}"
            self._float_color = (0, 200, 0)
            self._float_y = 150.0
            self._float_timer = 40
            self._flash_timer = 12
            self._flash_color = (0, 200, 0)
        else:
            self._float_text = "MISS"
            self._float_color = (220, 50, 50)
            self._float_y = 150.0
            self._float_timer = 40
            self._flash_timer = 12
            self._flash_color = (220, 50, 50)

    def update(self):
        if self.game_state == "challenging":
            self.challenge_timer -= 1
            if self.challenge_timer <= 0:
                self._end_challenge()

        self.court_success.update()
        self.court_fail.update()

        if (self.game_state == "idle" and not self.court_success.is_animating
                and not self.court_fail.is_animating):
            self._idle_timer += 1
            if self._idle_timer >= self._idle_threshold:
                for court in (self.court_success, self.court_fail):
                    court.set_idle_ball_man(True)

        if self._float_timer > 0:
            self._float_timer -= 1
            self._float_y -= 1.2
        if self._flash_timer > 0:
            self._flash_timer -= 1

    def draw(self, painter):
        tr = self.app.translations[self.app.current_lang]

        if self.court_fail.is_animating:
            self.court_fail.draw(painter, COURT_X, COURT_Y, COURT_W, COURT_H)
        else:
            self.court_success.draw(painter, COURT_X, COURT_Y, COURT_W, COURT_H)

        if self._flash_timer > 0:
            alpha = min(255, self._flash_timer * 14)
            painter.rect(COURT_X, COURT_Y, COURT_W, COURT_H,
                         (*self._flash_color, alpha))

        if self._float_timer > 0:
            alpha = min(255, self._float_timer * 7)
            painter.text(self._float_text, 24, (*self._float_color, alpha),
                         COURT_X + COURT_W // 2, int(self._float_y),
                         bold=True, align="center")

        if self.result_type == "hit":
            painter.text(tr["hit"], 12, (0, 150, 0), 30, 285, max_width=400)
        elif self.result_type == "miss":
            painter.text(tr["miss"], 12, (200, 0, 0), 30, 285, max_width=400)

        # Live score counter inside the backboard square of Hoop 2 only.
        c = self.court_success
        basket_name = os.path.basename(c.basket_file) if c.basket_file else ""
        if basket_name == "basket2.png":
            points = self.app.game.get_points()
            score_txt = "999+" if points > 1000 else str(points)
            label = make_label(score_txt, 9, True, (200, 0, 0))
            tex = label.texture
            if tex is not None:
                tw, th = tex.width, tex.height
                bl = COURT_X + c._basket_left_x
                bt = COURT_Y + c._sky_h - c.basket_h
                bb_cx = bl + int(c.basket_w * 0.708)
                bb_cy = bt + int(c.basket_h * 0.074)
                box_w = tw + 4
                box_h = th + 2
                bx = bb_cx - box_w // 2
                by = bb_cy - box_h // 2
                painter.rect(bx, by, box_w, box_h, (255, 255, 255, 170))
                painter.image(tex, bx + 2, by + 1)

        if self.game_state == "result":
            score_text = tr["score_message"].format(self.click_count)
            painter.text(score_text, 12, (0, 0, 200), 30, 310, max_width=400)

        points_text = tr["points"].format(self.app.game.get_points())
        painter.text(points_text, 16, (0, 0, 0), 260, 360, bold=True,
                     max_width=200)