import os
import pygame
from PIL import Image as PILImage
from animation.rim_config import get_rim_calibration
from animation.assets import load_pil_cropped, pil_to_pygame


class CourtBase:
    def __init__(self, ball_file="ball3.png", basket_file="basket.png"):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.ball_file = ball_file
        self.basket_file = basket_file

        self._pil_man = None
        self._pil_man_jump = None
        self._pil_man_ball = None
        self._pil_basket = None
        self._pil_ball = None

        self.img_man = None
        self.img_man_jump = None
        self.img_man_ball = None
        self.img_basket = None
        self.img_ball = None
        self.img_ball_rot_left = None
        self.img_ball_rot_right = None

        self._use_idle_ball_man = False

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
        self._backboard_x = 0

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

        self._man_offset_y = 0.0
        self._jump_t = 0
        self._jump_duration = 4
        self._jump_peak = -18

        self._spin_frame = 0
        self._spin_lift = 0

        self._success_fix_x = 0

        self._man_descending = False
        self._man_descend_t = 0

        self.load_images()

    def load_images(self):
        self._pil_man = load_pil_cropped("man.png", self.base_dir)
        self._pil_man_jump = load_pil_cropped("man+jump.png", self.base_dir)
        self._pil_man_ball = load_pil_cropped("man+ball.png", self.base_dir)
        self._pil_basket = load_pil_cropped(self.basket_file, self.base_dir)
        self._pil_ball = load_pil_cropped(self.ball_file, self.base_dir)

    def set_skins(self, ball_file, basket_file):
        self.ball_file = ball_file
        self.basket_file = basket_file
        self.img_ball = None
        self.img_ball_rot_left = None
        self.img_ball_rot_right = None
        self.img_basket = None
        self._prepared_size = None
        self.load_images()

    def set_idle_ball_man(self, enabled):
        self._use_idle_ball_man = enabled

    def prepare(self, court_w, court_h):
        key = (court_w, court_h)
        if self._prepared_size == key and self.img_man and self.img_man_jump and self.img_man_ball and self.img_basket and self.img_ball:
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

        if self._pil_man_jump:
            w, h = self._pil_man_jump.size
            nw = max(1, int(w * man_target_h / h))
            nh = max(1, man_target_h)
            self.img_man_jump = pil_to_pygame(self._pil_man_jump.resize((nw, nh)))

        if self._pil_man_ball:
            w, h = self._pil_man_ball.size
            nw = max(1, int(w * man_target_h / h))
            nh = max(1, man_target_h)
            self.img_man_ball = pil_to_pygame(self._pil_man_ball.resize((nw, nh)))

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

            rot_left = self._pil_ball.rotate(90, expand=True, resample=PILImage.BICUBIC)
            rl_w, rl_h = rot_left.size
            rl_nw = max(1, int(rl_w * ball_target / rl_h))
            rl_nh = max(1, ball_target)
            self.img_ball_rot_left = pil_to_pygame(rot_left.resize((rl_nw, rl_nh)))

            rot_right = self._pil_ball.rotate(-90, expand=True, resample=PILImage.BICUBIC)
            rr_w, rr_h = rot_right.size
            rr_nw = max(1, int(rr_w * ball_target / rr_h))
            rr_nh = max(1, ball_target)
            self.img_ball_rot_right = pil_to_pygame(rot_right.resize((rr_nw, rr_nh)))

            self._spin_lift = max(2, int(ball_target * 0.35))

        self._man_x = int(court_w * 0.06)
        basket_right_x = int(court_w * 0.97)
        self._basket_left_x = basket_right_x - self.basket_w

        cal = get_rim_calibration(self.basket_file)
        self._rim_x = self._basket_left_x + int(self.basket_w * cal["cx"])
        self._rim_y = (sky_h - self.basket_h) + int(self.basket_h * cal["cy"])
        self._ground_y = sky_h - self.ball_r
        self._backboard_x = self._basket_left_x + self.basket_w - 5

        self._rest_x = self._man_x + int(self.man_w * 0.97)
        self._rest_y = sky_h - int(self.man_h * 0.62)

        self._prepared_size = key

    def draw(self, surface, cx, cy, court_w, court_h):
        self.prepare(court_w, court_h)
        sky_h = self._sky_h

        pygame.draw.rect(surface, (66, 170, 255), (cx, cy, court_w, sky_h))
        pygame.draw.rect(surface, (209, 106, 32), (cx, cy + sky_h, court_w, court_h - sky_h))

        if self.img_basket:
            surface.blit(self.img_basket,
                         (cx + self._basket_left_x, cy + sky_h - self.basket_h))

        man_base_y = cy + sky_h - self.man_h
        man_draw_y = man_base_y + int(self._man_offset_y)

        if self.state in ("jumping_up", "jumping_down") and self.img_man_jump:
            surface.blit(self.img_man_jump, (cx + self._man_x, man_draw_y))
        elif self._use_idle_ball_man and self.img_man and self.state == "idle":
            surface.blit(self.img_man, (cx + self._man_x, man_draw_y))
        elif self.img_man:
            surface.blit(self.img_man, (cx + self._man_x, man_draw_y))

        if self.state == "idle":
            self.ball_x = float(self._rest_x)
            self.ball_y = float(self._rest_y)

        ball_draw_y = cy + int(self.ball_y)
        if self.state in ("jumping_up", "jumping_down"):
            ball_draw_y = cy + int(self._rest_y) + int(self._man_offset_y)

        if self.img_ball:
            bw = self.img_ball.get_width()
            bh = self.img_ball.get_height()
            if self._use_idle_ball_man and self.state == "idle":
                self._spin_frame += 1
                if self._spin_frame % 6 < 2:
                    ball_img = self.img_ball_rot_left
                elif self._spin_frame % 6 < 4:
                    ball_img = self.img_ball_rot_right
                else:
                    ball_img = self.img_ball
                if ball_img is None:
                    ball_img = self.img_ball
                bw = ball_img.get_width()
                bh = ball_img.get_height()
                surface.blit(ball_img,
                             (cx + int(self.ball_x) - bw // 2,
                              ball_draw_y - self._spin_lift - bh // 2))
            else:
                surface.blit(self.img_ball,
                             (cx + int(self.ball_x) - bw // 2,
                              ball_draw_y - bh // 2))

    def start_animation(self, court_w, court_h):
        self.prepare(court_w, court_h)
        self.state = "jumping_up"
        self.ball_x = float(self._rest_x)
        self.ball_y = float(self._rest_y)
        self._frame_counter = 0
        self._jump_t = 0
        self._man_offset_y = 0.0
        self._spin_frame = 0
        self._man_descending = False
        self._man_descend_t = 0
        self._man_descent_tick = 0
        self.target_x = float(self._rim_x)
        self.target_y = float(self._rim_y)

    def stop(self):
        self.state = "idle"
        self._frame_counter = 0
        self._jump_t = 0
        self._man_offset_y = 0.0
        self._spin_frame = 0
        self._man_descending = False
        self._man_descend_t = 0
        self._man_descent_tick = 0

    def _update_man_descent(self):
        if self._man_descending:
            self._man_descend_t += 1
            dur = self._jump_duration + 2
            progress = min(1.0, self._man_descend_t / dur)
            self._man_offset_y = self._jump_peak * (1.0 - progress)
            if progress >= 1.0:
                self._man_offset_y = 0.0
                self._man_descending = False
                self._man_descent_tick = 0
        elif self._man_descent_tick > 0:
            self._man_descent_tick += 1
            if self._man_descent_tick >= 10:
                self._man_descending = True
                self._man_descend_t = 0

    def _plan_flight(self, ex, ey):
        sx, sy = self.ball_x, self.ball_y
        dx = max(10.0, abs(ex - sx))
        g = 0.35

        T0 = dx / float(self.step)
        vy_ideal = (sy - ey + 0.5 * g * T0 * T0) / T0

        max_peak_y = float(self.ball_r + 5)
        headroom = max(10.0, sy - max_peak_y)
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

        if self.state == "jumping_up":
            self._jump_t += 1
            progress = self._jump_t / self._jump_duration
            self._man_offset_y = self._jump_peak * (1.0 - (1.0 - progress) ** 2)
            self.ball_y = float(self._rest_y) + self._man_offset_y
            if self._jump_t >= self._jump_duration:
                self._man_offset_y = float(self._jump_peak)
                self.state = "flying"
                self.ball_x = float(self._rest_x)
                self.ball_y = float(self._rest_y) + self._man_offset_y
                self._plan_flight(self.target_x, self.target_y)
                self._man_descent_tick = 1
            return

        if self.state == "flying":
            self._update_man_descent()
            self.flight_t += 1.0
            if self.flight_t >= self.flight_T:
                self.ball_x = self.target_x
                self.ball_y = self.target_y
                self.state = "jumping_down"
                self._jump_t = 0
            else:
                self.ball_x += self.flight_vx
                self.ball_y += self.flight_vy
                self.flight_vy += self.flight_g

                if self.ball_y < float(self.ball_r + 2):
                    self.ball_y = float(self.ball_r + 2)
                    self.flight_vy = abs(self.flight_vy) * 0.3

                if self.ball_x < float(self.ball_r):
                    self.ball_x = float(self.ball_r)
                    self.flight_vx = abs(self.flight_vx) * 0.5

                if self.ball_x > float(self._court_w - self.ball_r):
                    self.ball_x = float(self._court_w - self.ball_r)
                    self.flight_vx = -abs(self.flight_vx) * 0.5

                if (self.flight_vx > 0 and
                    self.ball_x + self.ball_r >= self._backboard_x):
                    self.ball_x = float(self._backboard_x - self.ball_r)
                    self.flight_vx = -abs(self.flight_vx) * 0.6
                    self.flight_vy *= 0.8
            return

        if self.state == "jumping_down":
            self._update_man_descent()
            if not self._man_descending and self._man_offset_y == 0.0:
                self.state = "idle"
            return

    @property
    def is_animating(self):
        return self.state != "idle"
