from animation.court_base import CourtBase


class CourtSuccess(CourtBase):
    def start_animation(self, court_w, court_h):
        self.prepare(court_w, court_h)
        self.state = "flying"
        self.ball_x = float(self._rest_x)
        self.ball_y = float(self._rest_y)
        self._frame_counter = 0
        self.target_x = float(self._rim_x)
        self.target_y = float(self._rim_y)
        self._plan_flight(self.target_x, self.target_y)

    def update(self):
        if self.state == "idle":
            return

        self._frame_counter += 1
        if self._frame_counter < self._tick_interval:
            return
        self._frame_counter = 0

        if self.state == "falling":
            if self.ball_y < self._ground_y:
                self.ball_y = min(self.ball_y + 3, float(self._ground_y))
            else:
                self.state = "idle"
            return

        self.flight_t += 1.0
        if self.flight_t >= self.flight_T:
            self.ball_x = self.target_x
            self.ball_y = self.target_y
            self.state = "falling"
        else:
            self.ball_x += self.flight_vx
            self.ball_y += self.flight_vy
            self.flight_vy += self.flight_g
