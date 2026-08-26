import random
from animation.court_base import CourtBase


class CourtFail(CourtBase):
    def __init__(self, ball_file="ball3.png", basket_file="basket.png"):
        super().__init__(ball_file, basket_file)
        self._rim_front_x = 0
        self._miss_variant = 0

    def prepare(self, court_w, court_h):
        super().prepare(court_w, court_h)
        from animation.rim_config import get_rim_calibration
        cal = get_rim_calibration(self.basket_file)
        self._rim_front_x = self._basket_left_x + int(self.basket_w * cal["x0"])

    def start_animation(self, court_w, court_h):
        self.prepare(court_w, court_h)
        variant = random.randint(0, 3)
        self._miss_variant = variant

        self.state = "flying"
        self.ball_x = float(self._rest_x)
        self.ball_y = float(self._rest_y)
        self._frame_counter = 0

        if variant == 0:
            impact_x = float(self._rim_front_x + self.ball_r)
            impact_y = float(self._rim_y)
        elif variant == 1:
            rim_back_x = self._rim_x + (self._rim_x - self._rim_front_x)
            impact_x = float(rim_back_x)
            impact_y = float(self._rim_y - 2)
        elif variant == 2:
            impact_x = float(self._rim_x - 5)
            impact_y = float(self._rim_y - 12)
        else:
            impact_x = float(self._rim_front_x - 3)
            impact_y = float(self._rim_y + 5)

        self.target_x = impact_x
        self.target_y = impact_y
        self._plan_flight(impact_x, impact_y)

    def update(self):
        if self.state == "idle":
            return

        self._frame_counter += 1
        if self._frame_counter < self._tick_interval:
            return
        self._frame_counter = 0

        if self.state == "bouncing":
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
                self.state = "idle"
            return

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
