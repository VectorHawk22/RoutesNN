import os
import pygame
from animation.rim_config import get_rim_calibration
from animation.assets import load_pil_cropped, pil_to_pygame


class CourtBase:
    def __init__(self, ball_file="ball3.png", basket_file="basket.png"):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.ball_file = ball_file
        self.basket_file = basket_file

        self._pil_man = None
        self._pil_basket = None
        self._pil_ball = None

        self.img_man = None
        self.img_basket = None
        self.img_ball = None

        self.man_w = 0
        self.man_h = 0
        self.basket_w = 0
        self.basket_h = 0
        self.ball_r = 8

        self._prepared_size = None
        self._court_w = 0
        self._court_h = 0
        self._sky_h = 0
        self._man_x = 0
        self._basket_left_x = 0
        self._rim_x = 0
        self._rim_y = 0
        self._ground_y = 0
        self._rest_x = 0
        self._rest_y = 0

        self.state = "idle"
        self.ball_x = 0.0
        self.ball_y = 0.0
        self.target_x = 0.0
        self.target_y = 0.0
        self.step = 3

        self.flight_vx = 0.0
        self.flight_vy = 0.0
        self.flight_g = 0.0
        self.flight_T = 0.0
        self.flight_t = 0.0

        self._frame_counter = 0
        self._tick_interval = 3

        self.load_images()

    def load_images(self):
        self._pil_man = load_pil_cropped("man.png", self.base_dir)
        self._pil_basket = load_pil_cropped(self.basket_file, self.base_dir)
        self._pil_ball = load_pil_cropped(self.ball_file, self.base_dir)

    def set_skins(self, ball_file, basket_file):
        self.ball_file = ball_file
        self.basket_file = basket_file
        self.img_ball = None
        self.img_basket = None
        self._prepared_size = None
        self.load_images()

    def prepare(self, court_w, court_h):
        key = (court_w, court_h)
        if self._prepared_size == key and self.img_man and self.img_basket and self.img_ball:
            return

        self._court_w = court_w
        self._court_h = court_h
        sky_h = int(court_h * 0.65)
        self._sky_h = sky_h

        man_target_h = max(16, int(sky_h * 0.60))
        basket_target_h = max(24, int(sky_h * 0.95))
        ball_target = max(10, int(man_target_h * 0.16))

        if self._pil_man:
            w, h = self._pil_man.size
            nw = max(1, int(w * man_target_h / h))
            nh = max(1, man_target_h)
            self.img_man = pil_to_pygame(self._pil_man.resize((nw, nh)))
            self.man_w, self.man_h = nw, nh

        if self._pil_basket:
            w, h = self._pil_basket.size
            nw = max(1, int(w * basket_target_h / h))
            nh = max(1, basket_target_h)
            self.img_basket = pil_to_pygame(self._pil_basket.resize((nw, nh)))
            self.basket_w, self.basket_h = nw, nh

        if self._pil_ball:
            w, h = self._pil_ball.size
            nw = max(1, int(w * ball_target / h))
            nh = max(1, ball_target)
            self.img_ball = pil_to_pygame(self._pil_ball.resize((nw, nh)))
            self.ball_r = max(5, nw // 2)

        self._man_x = int(court_w * 0.06)
        basket_right_x = int(court_w * 0.97)
        self._basket_left_x = basket_right_x - self.basket_w

        cal = get_rim_calibration(self.basket_file)
        self._rim_x = self._basket_left_x + int(self.basket_w * cal["cx"])
        self._rim_y = (sky_h - self.basket_h) + int(self.basket_h * cal["cy"])
        self._ground_y = sky_h - self.ball_r

        self._rest_x = self._man_x + int(self.man_w * 0.8)
        self._rest_y = sky_h - int(self.man_h * 0.65)

        self._prepared_size = key

    def draw(self, surface, cx, cy, court_w, court_h):
        self.prepare(court_w, court_h)
        sky_h = self._sky_h

        pygame.draw.rect(surface, (66, 170, 255), (cx, cy, court_w, sky_h))
        pygame.draw.rect(surface, (209, 106, 32), (cx, cy + sky_h, court_w, court_h - sky_h))

        if self.img_basket:
            surface.blit(self.img_basket,
                         (cx + self._basket_left_x, cy + sky_h - self.basket_h))

        if self.img_man:
            surface.blit(self.img_man,
                         (cx + self._man_x, cy + sky_h - self.man_h))

        if self.state == "idle":
            self.ball_x = float(self._rest_x)
            self.ball_y = float(self._rest_y)

        if self.img_ball:
            bw = self.img_ball.get_width()
            bh = self.img_ball.get_height()
            surface.blit(self.img_ball,
                         (cx + int(self.ball_x) - bw // 2,
                          cy + int(self.ball_y) - bh // 2))

    def start_animation(self, court_w, court_h):
        self.prepare(court_w, court_h)
        self.state = "flying"
        self.ball_x = float(self._rest_x)
        self.ball_y = float(self._rest_y)
        self._frame_counter = 0
        self.target_x = float(self._rim_x)
        self.target_y = float(self._rim_y)
        self._plan_flight(self.target_x, self.target_y)

    def stop(self):
        self.state = "idle"
        self._frame_counter = 0

    def _plan_flight(self, ex, ey):
        sx, sy = self.ball_x, self.ball_y
        dx = max(10.0, abs(ex - sx))
        g = 0.35

        T0 = dx / float(self.step)
        vy_ideal = (sy - ey + 0.5 * g * T0 * T0) / T0

        headroom = max(20.0, sy - self.ball_r - 2)
        vy_ceiling = (2 * g * headroom) ** 0.5

        if vy_ideal <= vy_ceiling:
            vy0 = vy_ideal
            T = T0
        else:
            vy0 = vy_ceiling
            disc = vy0 * vy0 - 2 * g * (sy - ey)
            if disc < 0:
                vy0 = (2 * g * max(1.0, sy - ey)) ** 0.5
                disc = 0.0
            T = (vy0 + disc ** 0.5) / g

        self.flight_vx = dx / T
        self.flight_vy = -vy0
        self.flight_g = g
        self.flight_T = T
        self.flight_t = 0.0

    def update(self):
        if self.state == "idle":
            return

        self._frame_counter += 1
        if self._frame_counter < self._tick_interval:
            return
        self._frame_counter = 0

        self.flight_t += 1.0
        if self.flight_t >= self.flight_T:
            self.ball_x = self.target_x
            self.ball_y = self.target_y
            self.state = "idle"
        else:
            self.ball_x += self.flight_vx
            self.ball_y += self.flight_vy
            self.flight_vy += self.flight_g

    @property
    def is_animating(self):
        return self.state != "idle"
