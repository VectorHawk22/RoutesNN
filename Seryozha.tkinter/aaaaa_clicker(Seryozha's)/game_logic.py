import json
import os
from datetime import datetime, timedelta
import random


class ClickerGame:
    def __init__(self):
        self.points = 0
        self.potion_active = False
        self.potion_end_time = None
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.save_file = os.path.join(self.base_dir, "save.json")
        self.load_game()

    def try_add_point(self, clicks):
        """Попытка добавить очко на основе количества кликов"""
        if clicks == 0:
            return False, 0.0

        base_chance = 0.3
        luck_factor = min(clicks * 0.05, 0.7)
        total_chance = min(base_chance + luck_factor, 0.95)
        success = random.random() < total_chance

        if success:
            points_to_add = 2 if self.is_potion_active() else 1
            self.points += points_to_add
            self.save_game()

        return success, total_chance

    def get_points(self):
        return self.points

    def is_potion_active(self):
        if self.potion_active and self.potion_end_time:
            try:
                end_time = datetime.fromisoformat(self.potion_end_time)
                if datetime.now() < end_time:
                    return True
                else:
                    self.potion_active = False
                    self.potion_end_time = None
                    self.save_game()
            except (ValueError, TypeError):
                self.potion_active = False
                self.potion_end_time = None
        return False

    def activate_potion(self):
        if not self.is_potion_active():
            end_time = datetime.now() + timedelta(minutes=10)
            self.potion_active = True
            self.potion_end_time = end_time.isoformat()
            self.save_game()
            return True
        return False

    def get_potion_time_left(self):
        if not self.is_potion_active():
            return 0
        try:
            end_time = datetime.fromisoformat(self.potion_end_time)
            left = (end_time - datetime.now()).total_seconds()
            return max(0, int(left))
        except (ValueError, TypeError):
            return 0

    def save_game(self):
        try:
            data = {
                "points": self.points,
                "potion_active": self.potion_active,
                "potion_end_time": self.potion_end_time
            }
            with open(self.save_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Ошибка сохранения: {e}")

    def load_game(self):
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.points = data.get("points", 0)
                    self.potion_active = data.get("potion_active", False)
                    self.potion_end_time = data.get("potion_end_time", None)
            except Exception as e:
                print(f"Ошибка загрузки: {e}")
                self.points = 0
                self.potion_active = False
                self.potion_end_time = None
        else:
            print("Новый прогресс (файл сохранения не найден)")

    def reset_progress(self):
        """Сброс прогресса"""
        self.points = 0
        self.potion_active = False
        self.potion_end_time = None
        self.save_game()