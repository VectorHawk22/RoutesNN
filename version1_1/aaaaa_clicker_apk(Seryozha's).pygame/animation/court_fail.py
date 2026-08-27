import random
from animation.court_base import CourtBase


class CourtFail(CourtBase):
    def __init__(self, ball_file="ball3.png", basket_file="basket.png"):
        super().__init__(ball_file, basket_file)
        self._rim_front_x = 0
        self._rim_r = 0
        self._miss_variant = 0

    def prepare(self, court_w, court_h):
        super().prepare(court_w, court_h)
        from animation.rim_config import get_rim_calibration
        cal = get_rim_calibration(self.basket_file)
        self._rim_front_x = self._basket_left_x + int(self.basket_w * cal["x0"])
        self._rim_r = max(3, self._rim_x - self._rim_front_x)

    def start_animation(self, court_w, court_h):
        self.prepare(court_w, court_h)
        variant = random.randint(0, 3)
        self._miss_variant = variant

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

        if variant == 0:
            impact_x = float(self._rim_front_x)
            impact_y = float(self._rim_y - self.ball_r)
        elif variant == 1:
            rim_back_x = self._rim_front_x + 2 * self._rim_r
            impact_x = float(rim_back_x)
            impact_y = float(self._rim_y - 2)
        elif variant == 2:
            impact_x = float(self._rim_front_x - self.ball_r)
            impact_y = float(self._rim_y)
        else:
            impact_x = float(self._rim_front_x)
            impact_y = float(self._rim_y + self.ball_r)

        self.target_x = impact_x
        self.target_y = impact_y

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

        if self.state == "bouncing":
            self._update_man_descent()
            if self.ball_y < self._ground_y:
                self.ball_x += self.flight_vx
                self.ball_y += self.flight_vy
                self.flight_vy += self.flight_g

                if self.ball_y < self.ball_r:
                    self.ball_y = float(self.ball_r)
                    self.flight_vy = abs(self.flight_vy) * 0.45
                if self.ball_x > self._court_w - self.ball_r:
                    self.ball_x = float(self._court_w - self.ball_r)
                    self.flight_vx = -abs(self.flight_vx) * 0.5
                if self.ball_x < self.ball_r:
                    self.ball_x = float(self.ball_r)
                    self.flight_vx = abs(self.flight_vx) * 0.5
                if (self.flight_vx > 0 and
                    self.ball_x + self.ball_r >= self._backboard_x):
                    self.ball_x = float(self._backboard_x - self.ball_r)
                    self.flight_vx = -abs(self.flight_vx) * 0.5
                if self.ball_y > self._ground_y:
                    self.ball_y = float(self._ground_y)
            else:
                self.state = "jumping_down"
                self._jump_t = 0
            return

        if self.state == "flying":
            self._update_man_descent()
            self.flight_t += 1.0
            if self.flight_t >= self.flight_T:
                self.state = "bouncing"
                if self._miss_variant == 2:
                    self.flight_vx = -max(1.5, abs(self.flight_vx) * 0.35)
                    self.flight_vy = -5.0
                elif self._miss_variant == 1:
                    self.flight_vx = -max(2.0, abs(self.flight_vx) * 0.45)
                    self.flight_vy = -6.0
                elif self._miss_variant == 3:
                    self.flight_vx = -max(1.5, abs(self.flight_vx) * 0.35)
                    self.flight_vy = -5.0
                else:
                    self.flight_vx = max(2.0, abs(self.flight_vx) * 0.45)
                    self.flight_vy = -6.0
            else:
                self.ball_x += self.flight_vx
                self.ball_y += self.flight_vy
                self.flight_vy += self.flight_g

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
