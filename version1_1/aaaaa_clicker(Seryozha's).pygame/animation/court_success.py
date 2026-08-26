import random
from animation.court_base import CourtBase


class CourtSuccess(CourtBase):
    def start_animation(self, court_w, court_h):
        self.prepare(court_w, court_h)
        variant = random.randint(0, 3)
        self._variant = variant

        self.state = "jumping_up"
        self.ball_x = float(self._rest_x)
        self.ball_y = float(self._rest_y)
        self._frame_counter = 0
        self._jump_t = 0
        self._man_offset_y = 0.0

        self.target_x = float(self._rim_x)
        self.target_y = float(self._rim_y)

        if variant == 0:
            self.step = 3
        elif variant == 1:
            self.step = 2
        elif variant == 2:
            self.step = 4
        else:
            self.step = 2

        self._plan_flight(self.target_x, self.target_y)

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
            if self._jump_t >= self._jump_duration:
                self._man_offset_y = float(self._jump_peak)
                self.state = "flying"
                self.ball_x = float(self._rest_x)
                self.ball_y = float(self._rest_y)
            return

        if self.state == "flying":
            self.flight_t += 1.0
            if self.flight_t >= self.flight_T:
                self.ball_x = self.target_x
                self.ball_y = self.target_y
                self.state = "falling"
            else:
                self.ball_x += self.flight_vx
                self.ball_y += self.flight_vy
                self.flight_vy += self.flight_g
            return

        if self.state == "falling":
            if self.ball_y < self._ground_y:
                speed = 4 if self._variant != 3 else 5
                drift = 0.3 if self._variant == 0 else (0.5 if self._variant == 1 else 0.2)
                self.ball_y = min(self.ball_y + speed, float(self._ground_y))
                self.ball_x += drift
            else:
                self.state = "jumping_down"
                self._jump_t = 0
            return

        if self.state == "jumping_down":
            self._jump_t += 1
            progress = self._jump_t / self._jump_duration
            self._man_offset_y = self._jump_peak * (1.0 - progress)
            if self._jump_t >= self._jump_duration:
                self._man_offset_y = 0.0
                self.state = "idle"
            return
