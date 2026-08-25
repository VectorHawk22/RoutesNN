from animation.court_base import CourtBase


class CourtFail(CourtBase):
    def __init__(self, ball_file="ball3.png", basket_file="basket.png"):
        super().__init__(ball_file, basket_file)
        self._rim_front_x = 0

    def prepare(self, court_w, court_h):
        super().prepare(court_w, court_h)
        from animation.rim_config import get_rim_calibration
        cal = get_rim_calibration(self.basket_file)
        self._rim_front_x = self._basket_left_x + int(self.basket_w * cal["x0"])

    def start_animation(self, court_w, court_h):
        self.prepare(court_w, court_h)
        self.state = "flying"
        self.ball_x = float(self._rest_x)
        self.ball_y = float(self._rest_y)
        self._frame_counter = 0
        impact_x = float(self._rim_front_x + self.ball_r)
        impact_y = float(self._rim_y)
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
                    self.flight_vy = abs(self.flight_vy) * 0.3
                if self.ball_x > self._court_w - self.ball_r:
                    self.ball_x = float(self._court_w - self.ball_r)
                    self.flight_vx = -abs(self.flight_vx) * 0.4
                if self.ball_x < self.ball_r:
                    self.ball_x = float(self.ball_r)
                    self.flight_vx = abs(self.flight_vx) * 0.4
                if self.ball_y > self._ground_y:
                    self.ball_y = float(self._ground_y)
            else:
                self.state = "idle"
            return

        self.flight_t += 1.0
        if self.flight_t >= self.flight_T:
            self.state = "bouncing"
            self.flight_vx = max(1.5, abs(self.flight_vx) * 0.3)
            self.flight_vy = -5.0
        else:
            self.ball_x += self.flight_vx
            self.ball_y += self.flight_vy
            self.flight_vy += self.flight_g
