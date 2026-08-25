import pygame
from gui import Screen, Button, get_font, render_text, strip_emoji
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
        self.court_success = CourtSuccess(ball_file=skin_ball, basket_file=skin_basket)
        self.court_fail = CourtFail(ball_file=skin_ball, basket_file=skin_basket)

        self.game_state = "idle"
        self.click_count = 0
        self.challenge_timer = 0
        self.result_type = None

        self.btn_click = Button(
            (30, 350, 210, 45), "", font_size=13,
            bg_color=(173, 216, 230), callback=self._on_button_click)

        self.nav_buttons = []
        self._build_nav()
        self._update_button_text()

    def _build_nav(self):
        tr = self.app.translations[self.app.current_lang]
        self.nav_buttons = [
            Button((460, 15, 130, 80), tr["btn_inventory"], font_size=11,
                   bg_color=(240, 128, 128), callback=lambda: self.app.switch_screen("inventory")),
            Button((460, 105, 130, 80), tr["btn_shop"], font_size=11,
                   bg_color=(144, 238, 144), callback=lambda: self.app.switch_screen("shop")),
            Button((460, 195, 130, 80), tr["btn_authors"], font_size=11,
                   bg_color=(255, 255, 180), callback=lambda: self.app.switch_screen("authors")),
            Button((460, 285, 130, 80), tr["btn_settings"], font_size=11,
                   bg_color=(200, 200, 200), callback=lambda: self.app.switch_screen("settings")),
        ]

    def apply_skins(self):
        ball_file = self.app.settings.get("skin_ball", "ball1.png")
        basket_file = self.app.settings.get("skin_basket", "basket.png")
        for court in (self.court_success, self.court_fail):
            court.set_skins(ball_file, basket_file)

    def set_language(self):
        tr = self.app.translations[self.app.current_lang]
        self._update_button_text()
        self._build_nav()

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
        success, _ = self.app.game.try_add_point(self.click_count)
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

    def update(self):
        if self.game_state == "challenging":
            self.challenge_timer -= 1
            if self.challenge_timer <= 0:
                self._end_challenge()

        self.court_success.update()
        self.court_fail.update()

    def handle_event(self, event):
        self.btn_click.handle_event(event)
        for btn in self.nav_buttons:
            btn.handle_event(event)

    def draw(self, surface):
        tr = self.app.translations[self.app.current_lang]
        font_points = get_font(16, bold=True)
        font_result = get_font(12)

        if self.court_fail.is_animating:
            self.court_fail.draw(surface, COURT_X, COURT_Y, COURT_W, COURT_H)
        else:
            self.court_success.draw(surface, COURT_X, COURT_Y, COURT_W, COURT_H)

        if self.result_type == "hit":
            render_text(surface, tr["hit"], font_result, (0, 150, 0), 30, 285, 400)
        elif self.result_type == "miss":
            render_text(surface, tr["miss"], font_result, (200, 0, 0), 30, 285, 400)

        if self.game_state == "result":
            score_text = tr["score_message"].format(self.click_count)
            render_text(surface, score_text, font_result, (0, 0, 200), 30, 310, 400)

        points_text = tr["points"].format(self.app.game.get_points())
        render_text(surface, points_text, font_points, (0, 0, 0), 260, 360, 200)

        self.btn_click.draw(surface)

        for btn in self.nav_buttons:
            btn.draw(surface)
