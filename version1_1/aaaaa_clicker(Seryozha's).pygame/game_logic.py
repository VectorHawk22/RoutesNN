import json
import os
import hmac
import hashlib
from datetime import datetime, timedelta
import random

_SECRET = b"bK7x2mP9qL4wR8jN\x03\x7f"


class ClickerGame:
    def __init__(self):
        self.points = 0
        self.potion_active = False
        self.potion_end_time = None
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.save_file = os.path.join(self.base_dir, "save.json")
        self.settings_file = os.path.join(self.base_dir, "settings.json")
        self.load_game()

    def try_add_point(self, clicks):
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

    def _get_save_data(self):
        return {
            "points": self.points,
            "potion_active": self.potion_active,
            "potion_end_time": self.potion_end_time
        }

    def _get_settings_context(self):
        try:
            with open(self.settings_file, "r", encoding="utf-8") as f:
                s = json.load(f)
        except Exception:
            s = {}
        return {
            "language": s.get("language", ""),
            "skin_ball": s.get("skin_ball", ""),
            "skin_basket": s.get("skin_basket", ""),
            "inv_balls": sorted(s.get("inventory_balls", [])),
            "inv_baskets": sorted(s.get("inventory_baskets", [])),
        }

    def _compute_mac(self, save_data, context):
        blob = json.dumps(save_data, sort_keys=True, ensure_ascii=False)
        ctx = json.dumps(context, sort_keys=True, ensure_ascii=False)
        msg = blob.encode("utf-8") + b"\x00" + ctx.encode("utf-8")
        return hmac.new(_SECRET, msg, hashlib.sha256).hexdigest()

    def _read_settings(self):
        try:
            with open(self.settings_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _write_settings(self, settings):
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
        except Exception:
            pass

    def save_game(self):
        try:
            data = self._get_save_data()
            with open(self.save_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            ctx = self._get_settings_context()
            mac = self._compute_mac(data, ctx)
            settings = self._read_settings()
            settings["_v"] = mac
            self._write_settings(settings)
        except Exception as e:
            print(f"Ошибка сохранения: {e}")

    def load_game(self):
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                ctx = self._get_settings_context()
                expected = self._compute_mac(data, ctx)
                settings = self._read_settings()
                stored_mac = settings.get("_v", "")
                if stored_mac == "":
                    self.points = data.get("points", 0)
                    self.potion_active = data.get("potion_active", False)
                    self.potion_end_time = data.get("potion_end_time", None)
                    self.save_game()
                elif hmac.compare_digest(stored_mac, expected):
                    self.points = data.get("points", 0)
                    self.potion_active = data.get("potion_active", False)
                    self.potion_end_time = data.get("potion_end_time", None)
                else:
                    print("Обнаружена модификация! Прогресс сброшен.")
                    self.points = 0
                    self.potion_active = False
                    self.potion_end_time = None
                    self.save_game()
            except Exception as e:
                print(f"Ошибка загрузки: {e}")
                self.points = 0
                self.potion_active = False
                self.potion_end_time = None
        else:
            self.points = 0
            self.potion_active = False
            self.potion_end_time = None
            self.save_game()

    def reset_progress(self):
        self.points = 0
        self.potion_active = False
        self.potion_end_time = None
        self.save_game()
