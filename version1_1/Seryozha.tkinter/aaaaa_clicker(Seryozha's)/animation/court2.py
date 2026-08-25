import os
import tkinter as tk
from PIL import Image, ImageTk

from animation.rim_config import get_rim_calibration


class CourtFail:
    def __init__(self, canvas, ball_file="ball3.png", basket_file="basket.png"):
        self.canvas = canvas
        self.base_dir = os.path.dirname(os.path.abspath(__file__))

        # Выбранные скины
        self.ball_file = ball_file
        self.basket_file = basket_file

        # Загрузка изображений (обрезаются до видимого содержимого)
        self.img_man = None
        self.img_basket = None
        self.img_ball = None
        self.ball_obj = None
        self._pil_man = None
        self._pil_basket = None
        self._pil_ball = None
        self._prepared_size = None
        self.load_images()

        # Размеры объектов (пересчитываются в prepare_images)
        self.man_w = 0
        self.man_h = 0
        self.basket_w = 0
        self.basket_h = 0

        # Параметры анимации
        self.ball_x = 0
        self.ball_y = 0
        self.target_x = 0
        self.target_y = 0
        self.step = 3
        self.ball_r = 8
        self.falling = False
        self.bouncing = False
        self.fall_speed = 5
        self.gravity = 0.5
        self.bounce_height = 0
        self.is_animating = False
        self.anim_id = None

    def _load_cropped(self, filename):
        """Загрузка изображения с обрезкой прозрачных полей"""
        path = os.path.join(self.base_dir, filename)
        if not os.path.exists(path):
            print(f"⚠️ Файл не найден: {path}")
            return None
        try:
            img = Image.open(path).convert("RGBA")
            mask = img.getchannel("A").point(lambda a: 255 if a > 100 else 0)
            bbox = mask.getbbox()
            if bbox:
                img = img.crop(bbox)
            return img
        except Exception as e:
            print(f"Ошибка загрузки {filename}: {e}")
            return None

    def load_images(self):
        """Загрузка изображений"""
        try:
            self._pil_man = self._load_cropped("man.png")
            self._pil_basket = self._load_cropped(self.basket_file)
            self._pil_ball = self._load_cropped(self.ball_file)
        except Exception as e:
            print(f"Ошибка загрузки изображений промаха: {e}")

    def set_skins(self, ball_file, basket_file):
        """Смена скинов мяча и корзины"""
        self.ball_file = ball_file
        self.basket_file = basket_file
        self.img_ball = None
        self.img_basket = None
        self._prepared_size = None
        self.load_images()

    @staticmethod
    def _fit_height(pil_img, target_h):
        """Размер с сохранением пропорций по высоте"""
        w, h = pil_img.size
        return (max(1, int(w * target_h / h)), max(1, int(target_h)))

    def prepare_images(self, canvas_width, canvas_height):
        """Подготовка PhotoImage под размер canvas (с кэшем)"""
        key = (canvas_width, canvas_height)
        if self._prepared_size == key and self.img_man and self.img_basket and self.img_ball:
            return

        sky_height = int(canvas_height * 0.65)

        # Мальчик заметно ниже кольца, мяч маленький
        man_target_h = max(16, int(sky_height * 0.60))
        basket_target_h = max(24, int(sky_height * 0.95))
        ball_target = max(10, int(man_target_h * 0.16))

        if self._pil_man:
            size = self._fit_height(self._pil_man, man_target_h)
            self.man_w, self.man_h = size
            self.img_man = ImageTk.PhotoImage(
                self._pil_man.resize(size, Image.Resampling.LANCZOS))

        if self._pil_basket:
            size = self._fit_height(self._pil_basket, basket_target_h)
            self.basket_w, self.basket_h = size
            self.img_basket = ImageTk.PhotoImage(
                self._pil_basket.resize(size, Image.Resampling.LANCZOS))

        if self._pil_ball:
            size = self._fit_height(self._pil_ball, ball_target)
            self.img_ball = ImageTk.PhotoImage(
                self._pil_ball.resize(size, Image.Resampling.LANCZOS))
            self.ball_r = max(5, size[0] // 2)

        self._prepared_size = key

    def draw_court(self):
        """Рисование поля"""
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width < 10:
            canvas_width = 420
        if canvas_height < 10:
            canvas_height = 200

        self.canvas.delete("all")

        # Небо 65%
        sky_height = int(canvas_height * 0.65)

        self.canvas.create_rectangle(0, 0, canvas_width, sky_height, fill="#42AAFF")
        self.canvas.create_rectangle(0, sky_height, canvas_width, canvas_height, fill="#D16A20")

        # Масштабируем спрайты под реальный размер canvas
        self.prepare_images(canvas_width, canvas_height)

        # Корзина (у правого края, anchor=SE)
        basket_right_x = int(canvas_width * 0.97)
        if self.img_basket:
            self.canvas.create_image(basket_right_x, sky_height, image=self.img_basket, anchor=tk.SE)
        basket_left_x = basket_right_x - self.basket_w
        self.basket_left_x = basket_left_x

        # Человек (anchor=SW)
        man_x = int(canvas_width * 0.06)
        if self.img_man:
            self.canvas.create_image(man_x, sky_height, image=self.img_man, anchor=tk.SW)

        # Мяч в руках (руки вытянуты вперёд на уровне ~65% роста)
        self.ball_x = man_x + int(self.man_w * 0.8)
        self.ball_y = sky_height - int(self.man_h * 0.65)

        # ЦЕЛЬ - кольцо (координаты зависят от выбранной картинки корзины)
        cal = get_rim_calibration(self.basket_file)
        self.target_x = basket_left_x + int(self.basket_w * cal["cx"])
        self.target_y = (sky_height - self.basket_h) + int(self.basket_h * cal["cy"])
        self.rim_front_x = basket_left_x + int(self.basket_w * cal["x0"])
        self.bounce_height = sky_height - int(self.man_h * 0.5)

        if self.img_ball:
            self.ball_obj = self.canvas.create_image(
                self.ball_x, self.ball_y,
                image=self.img_ball
            )

    def _plan_flight(self, ex, ey):
        """Расчёт физичного полёта по параболе из текущей позиции мяча в (ex, ey)"""
        sx, sy = self.ball_x, self.ball_y
        dx = max(10.0, abs(ex - sx))
        g = 0.35

        T0 = dx / float(self.step)
        vy_ideal = (sy - ey + 0.5 * g * T0 * T0) / T0

        # Потолок по высоте дуги (мяч не выходит за верх canvas)
        headroom = max(20.0, sy - self.ball_r - 2)
        vy_ceiling = (2 * g * headroom) ** 0.5

        if vy_ideal <= vy_ceiling:
            vy0 = vy_ideal
            T = T0
        else:
            # Ограничены потолком: максимальная начальная скорость,
            # время из квадратного уравнения g*T^2/2 - vy0*T + (sy-ey) = 0
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

    def start_animation(self):
        """Запуск анимации промаха"""
        self.is_animating = True
        self.falling = False
        self.bouncing = False
        self.draw_court()
        if self.ball_obj:
            # Мяч летит в ПЕРЕДНЮЮ кромку кольца и заведомо не попадает
            impact_x = self.rim_front_x + self.ball_r
            impact_y = self.target_y
            self._plan_flight(impact_x, impact_y)
            self._move_ball()

    def stop(self):
        """Остановка анимации"""
        self.is_animating = False
        if self.anim_id:
            try:
                self.canvas.after_cancel(self.anim_id)
            except:
                pass
            self.anim_id = None

    def _move_ball(self):
        """Движение мяча при промахе"""
        if not self.is_animating or not self.img_ball or not self.ball_obj:
            return

        canvas_width = self.canvas.winfo_width()
        sky_height = int(self.canvas.winfo_height() * 0.65)
        # Земля - линия поля; мяч останавливается, когда касается её нижним краем
        ground_y = sky_height - self.ball_r

        # Отскок: мяч отлетает В СТОРОНУ КОЛЬЦА (вперёд) и падает за ним
        if self.bouncing:
            if self.ball_y < ground_y:
                self.ball_x += self.flight_vx
                self.ball_y += self.flight_vy
                self.flight_vy += self.flight_g
                # не вылетать за верх, правый и левый край canvas
                if self.ball_y < self.ball_r:
                    self.ball_y = self.ball_r
                    self.flight_vy = abs(self.flight_vy) * 0.3
                if self.ball_x > canvas_width - self.ball_r:
                    self.ball_x = canvas_width - self.ball_r
                    self.flight_vx = -abs(self.flight_vx) * 0.4
                if self.ball_x < self.ball_r:
                    self.ball_x = self.ball_r
                    self.flight_vx = abs(self.flight_vx) * 0.4
                if self.ball_y > ground_y:
                    self.ball_y = ground_y
                self.canvas.coords(self.ball_obj, self.ball_x, self.ball_y)
                self.anim_id = self.canvas.after(50, self._move_ball)
                return
            else:
                self.stop()
                return

        # Полёт по параболе (гравитация)
        self.flight_t += 1.0
        if self.flight_t >= self.flight_T:
            # Удар о переднюю кромку кольца - мяч подлетает вверх и вперёд,
            # перелетает кольцо и падает с другой стороны
            self.bouncing = True
            self.flight_vx = max(1.5, abs(self.flight_vx) * 0.3)
            self.flight_vy = -5.0
        else:
            self.ball_x += self.flight_vx
            self.ball_y += self.flight_vy
            self.flight_vy += self.flight_g

        self.canvas.coords(self.ball_obj, self.ball_x, self.ball_y)
        self.anim_id = self.canvas.after(50, self._move_ball)