import tkinter as tk
import os
import sys
from PIL import Image, ImageTk

# Добавляем корень проекта в пути импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game_logic import ClickerGame
from gui.settings import Settings
from gui.inventory import InventoryManager
from gui.shop import ShopManager
from gui.authors import AuthorsManager
from animation.court1 import CourtSuccess
from animation.court2 import CourtFail


class ClickerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Кликер")
        self.root.geometry("600x490")
        self.root.resizable(False, False)

        # Устанавливаем иконку приложения
        try:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "animation", "icon.jpg")
            icon = Image.open(icon_path)
            self._app_icon = ImageTk.PhotoImage(icon)
            self.root.iconphoto(True, self._app_icon)
        except Exception:
            pass

        # Определяем корневую папку проекта
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Загружаем настройки
        self.settings = self.load_settings()

        # Инициализация игры
        self.game = ClickerGame()

        # Устанавливаем язык из настроек
        self.current_lang = self.settings.get("language", "Русский")

        # Менеджеры экранов
        self.inventory_manager = None
        self.shop_manager = None
        self.authors_manager = None
        self.settings_manager = None
        self.settings_frame = None
        self.language_menu = None

        self.translations = {
            "Английский": {
                "title": "Clicker", "result": "Result: -", "hit": "🎯 Hit! +1 point!", "miss": "❌ Missed :(",
                "points": "Points: {}", "button_click": "Click!", "menu_lang": "Select language",
                "btn_inventory": "Inventory", "btn_shop": "Shop", "btn_authors": "Authors",
                "start_challenge": "Click to start!", "click_now": "CLICK NOW!",
                "score_message": "{} clicks in 1 second!", "inventory": "Inventory",
                "potion": "🧪 Double Points (10 min)", "potion_active": "Active! Time left: {} sec",
                "potion_inactive": "Use: 10 min x2", "use": "Use", "back": "Back", "btn_settings": "Settings",
                "settings_title": "⚙️ Settings",
                "language_label": "🌐 Language:",
                "sound_label": "🔊 Sound:",
                "sound_on": "On",
                "sound_off": "Off",
                "save_button": "💾 Save Settings",
                "reset_button": "🗑️ Reset Progress",
                "reset_confirm": "Are you sure you want to delete all progress?\n\nThis action cannot be undone!",
                "reset_done": "Progress successfully reset!",
                "reset_error": "Failed to reset progress",
                "tab_potions": "Potions", "tab_skins": "Skins",
                "skins_balls": "Balls", "skins_baskets": "Hoops",
                "save_success": "Settings saved!",
                "save_error": "Failed to save settings!"
            },
            "Русский": {
                "title": "Кликер", "result": "Результат: -", "hit": "🎯 Попал! +1 очко!", "miss": "❌ Промах :(",
                "points": "Очки: {}", "button_click": "Клик!", "menu_lang": "Язык",
                "btn_inventory": "Инвентарь", "btn_shop": "Магазин", "btn_authors": "Авторы",
                "start_challenge": "Нажми, и начни!", "click_now": "ЖМИ СЕЙЧАС!",
                "score_message": "{} кликов за 1 секунду!", "inventory": "Инвентарь",
                "potion": "🧪 2x очки (10 мин)", "potion_active": "Активно! Осталось: {} сек",
                "potion_inactive": "Использовать: 10 мин", "use": "Использовать", "back": "Назад",
                "btn_settings": "Настройки",
                "settings_title": "⚙️ Настройки",
                "language_label": "🌐 Язык:",
                "sound_label": "🔊 Звук:",
                "sound_on": "Включён",
                "sound_off": "Выключен",
                "save_button": "💾 Сохранить настройки",
                "reset_button": "🗑️ Сбросить прогресс",
                "reset_confirm": "Вы уверены, что хотите удалить весь прогресс?\n\nЭто действие нельзя отменить!",
                "reset_done": "Прогресс успешно сброшен!",
                "reset_error": "Не удалось сбросить прогресс",
                "tab_potions": "Зелья", "tab_skins": "Скины",
                "skins_balls": "Мячи", "skins_baskets": "Корзины",
                "save_success": "Настройки сохранены!",
                "save_error": "Не удалось сохранить настройки!"
            },
            "Французский": {
                "title": "Cliqueur", "result": "Résultat : -", "hit": "🎯 Touché ! +1 point !", "miss": "❌ Raté :(",
                "points": "Points : {}", "button_click": "Cliquez !", "menu_lang": "Choisir la langue",
                "btn_inventory": "Inventaire", "btn_shop": "Magasin", "btn_authors": "Auteurs",
                "start_challenge": "Cliquez pour commencer !", "click_now": "CLIQUEZ MAINTENANT !",
                "score_message": "{} clics en 1 seconde !", "inventory": "Inventaire",
                "potion": "🧪 Double points (10 min)", "potion_active": "Actif ! Temps restant : {} sec",
                "potion_inactive": "Utiliser : 10 min x2", "use": "Utiliser", "back": "Retour",
                "btn_settings": "Paramètres",
                "settings_title": "⚙️ Paramètres",
                "language_label": "🌐 Langue :",
                "sound_label": "🔊 Son :",
                "sound_on": "Activé",
                "sound_off": "Désactivé",
                "save_button": "💾 Enregistrer les paramètres",
                "reset_button": "🗑️ Réinitialiser la progression",
                "reset_confirm": "Êtes-vous sûr de vouloir supprimer toute la progression ?\n\nCette action est irréversible !",
                "reset_done": "Progression réinitialisée avec succès !",
                "reset_error": "Échec de la réinitialisation de la progression",
                "tab_potions": "Élixirs", "tab_skins": "Skins",
                "skins_balls": "Ballons", "skins_baskets": "Paniers",
                "save_success": "Paramètres enregistrés !",
                "save_error": "Échec de l'enregistrement des paramètres !"
            },
            "Немецкий": {
                "title": "Klicker", "result": "Ergebnis: -", "hit": "🎯 Treffer! +1 Punkt!", "miss": "❌ Daneben :(",
                "points": "Punkte: {}", "button_click": "Klick!", "menu_lang": "Sprache wählen",
                "btn_inventory": "Inventar", "btn_shop": "Laden", "btn_authors": "Autoren",
                "start_challenge": "Klicke zum Starten!", "click_now": "JETZT KLICKEN!",
                "score_message": "{} Klicks in 1 Sekunde!", "inventory": "Inventar",
                "potion": "🧪 Doppelte Punkte (10 Min)", "potion_active": "Aktiv! Verbleibend: {} Sek",
                "potion_inactive": "Benutzen: 10 Min x2", "use": "Benutzen", "back": "Zurück",
                "btn_settings": "Einstellungen",
                "settings_title": "⚙️ Einstellungen",
                "language_label": "🌐 Sprache:",
                "sound_label": "🔊 Sound:",
                "sound_on": "Ein",
                "sound_off": "Aus",
                "save_button": "💾 Einstellungen speichern",
                "reset_button": "🗑️ Fortschritt zurücksetzen",
                "reset_confirm": "Sind Sie sicher, dass Sie den gesamten Fortschritt löschen möchten?\n\nDiese Aktion kann nicht rückgängig gemacht werden!",
                "reset_done": "Fortschritt erfolgreich zurückgesetzt!",
                "reset_error": "Fehler beim Zurücksetzen des Fortschritts",
                "tab_potions": "Tränke", "tab_skins": "Skins",
                "skins_balls": "Bälle", "skins_baskets": "Körbe",
                "save_success": "Einstellungen gespeichert!",
                "save_error": "Fehler beim Speichern der Einstellungen!"
            },
            "Китайский": {
                "title": "点击器", "result": "结果: -", "hit": "🎯 击中！+1 分！", "miss": "❌ 未命中 :(",
                "points": "分数: {}", "button_click": "点击！", "menu_lang": "选择语言",
                "btn_inventory": "背包", "btn_shop": "商店", "btn_authors": "作者",
                "start_challenge": "点击开始！", "click_now": "立即点击！",
                "score_message": "1秒内点击 {} 次！", "inventory": "背包",
                "potion": "🧪 双倍积分 (10分钟)", "potion_active": "生效中！剩余时间：{} 秒",
                "potion_inactive": "使用：10分钟双倍", "use": "使用", "back": "返回",
                "btn_settings": "设置",
                "settings_title": "⚙️ 设置",
                "language_label": "🌐 语言:",
                "sound_label": "🔊 声音:",
                "sound_on": "开启",
                "sound_off": "关闭",
                "save_button": "💾 保存设置",
                "reset_button": "🗑️ 重置进度",
                "reset_confirm": "您确定要删除所有进度吗？\n\n此操作无法撤销！",
                "reset_done": "进度已成功重置！",
                "reset_error": "重置进度失败",
                "tab_potions": "药水", "tab_skins": "皮肤",
                "skins_balls": "球", "skins_baskets": "篮筐",
                "save_success": "设置已保存！",
                "save_error": "保存设置失败！"
            }
        }

        tr = self.translations[self.current_lang]

        # === ОСНОВНОЙ ЛЕЙАУТ ===
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.left_frame = tk.Frame(self.main_frame, width=440)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.left_frame.grid_propagate(False)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=0)

        # === АНИМАЦИЯ ===
        self.anim_container = tk.Frame(self.left_frame, height=280, bg="#f0f0f0")
        self.anim_container.pack(fill=tk.X, side=tk.TOP, pady=(0, 2))
        self.anim_container.pack_propagate(False)

        # Убираем чёрную рамку вокруг Canvas
        self.animation_canvas = tk.Canvas(
            self.anim_container,
            width=420,
            height=200,
            bg="#f0f0f0",
            highlightthickness=0,
            bd=0
        )
        self.animation_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Инициализация классов анимации (с выбранными скинами)
        skin_ball = self.settings.get("skin_ball", "ball3.png")
        skin_basket = self.settings.get("skin_basket", "basket.png")
        self.court_success = CourtSuccess(self.animation_canvas, ball_file=skin_ball, basket_file=skin_basket)
        self.court_fail = CourtFail(self.animation_canvas, ball_file=skin_ball, basket_file=skin_basket)
        self.root.after(150, self.redraw_animation)

        # === ИГРОВОЙ ЭКРАН ===
        self.game_frame = tk.Frame(self.left_frame)

        # Уменьшаем отступ сверху
        tk.Label(self.game_frame, text="").pack(pady=(2, 0))

        self.label_result = tk.Label(self.game_frame, text="", font=("Arial", 11))
        self.label_result.pack(pady=5)

        # Нижняя строка с кнопкой и очками
        self.bottom_row = tk.Frame(self.game_frame)
        self.bottom_row.pack(side=tk.BOTTOM, anchor="s", pady=(0, 2), fill=tk.X)

        self.button_click = tk.Button(
            self.bottom_row,
            text=tr["start_challenge"],
            font=("Arial", 12),
            width=16,
            height=1,
            bg="lightblue",
            command=self.start_challenge
        )
        self.button_click.pack(side=tk.LEFT, padx=10)

        self.label_points = tk.Label(
            self.bottom_row,
            text=tr["points"].format(self.game.get_points()),
            font=("Arial", 14, "bold")
        )
        self.label_points.pack(side=tk.LEFT, padx=10)

        # === ПРАВАЯ ПАНЕЛЬ ===
        self.right_frame = tk.Frame(self.main_frame, width=150)
        self.right_frame.grid(row=0, column=1, sticky="ns")
        self.right_frame.grid_propagate(False)

        # Конфигурация для всех кнопок справа - фиксированная ширина
        BUTTON_WIDTH = 18
        BUTTON_FONT = ("Arial", 9, "bold")
        BUTTON_PADX = (0, 5)
        BUTTON_PADY = 4

        self.btn1 = tk.Button(
            self.right_frame,
            text=tr["btn_inventory"],
            bg="lightcoral",
            font=BUTTON_FONT,
            width=BUTTON_WIDTH,
            command=self.open_inventory
        )
        self.btn1.grid(row=0, column=0, sticky="nsew", padx=BUTTON_PADX, pady=BUTTON_PADY)

        self.btn2 = tk.Button(
            self.right_frame,
            text=tr["btn_shop"],
            bg="lightgreen",
            font=BUTTON_FONT,
            width=BUTTON_WIDTH,
            command=self.open_shop
        )
        self.btn2.grid(row=1, column=0, sticky="nsew", padx=BUTTON_PADX, pady=BUTTON_PADY)

        self.btn3 = tk.Button(
            self.right_frame,
            text=tr["btn_authors"],
            bg="lightyellow",
            font=BUTTON_FONT,
            width=BUTTON_WIDTH,
            command=self.open_authors
        )
        self.btn3.grid(row=2, column=0, sticky="nsew", padx=BUTTON_PADX, pady=BUTTON_PADY)

        self.btn_settings = tk.Button(
            self.right_frame,
            text=tr["btn_settings"],
            font=BUTTON_FONT,
            bg="lightgray",
            width=BUTTON_WIDTH,
            command=self.open_settings
        )
        self.btn_settings.grid(row=3, column=0, sticky="nsew", padx=BUTTON_PADX, pady=BUTTON_PADY)

        # Настройка растягивания строк в правой панели
        for i in range(4):
            self.right_frame.grid_rowconfigure(i, weight=1)

        # === КНОПКА НАЗАД ===
        self.btn_back = tk.Button(self.root, text=tr["back"], font=("Arial", 12, "bold"), bg="lightblue", height=2,
                                  anchor="center")
        self.btn_back.pack_forget()

        # === НИЖНИЙ ТЕКСТ ===
        self.glitch_label = tk.Label(root, text="GlitchHunters", font=("Georgia", 9), fg="blue")
        self.glitch_label.place(x=10, rely=1.0, y=-30, anchor="sw")

        # === ПЕРЕМЕННЫЕ ДЛЯ ИГРЫ ===
        self.click_count = 0
        self.challenge_active = False

        # Показываем игровой экран
        self.show_game()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_settings(self):
        """Загрузка настроек из файла settings.json"""
        settings_file = os.path.join(self.base_dir, "settings.json")
        default_settings = {"sound": True, "language": "Русский"}

        if not os.path.exists(settings_file):
            try:
                import json
                with open(settings_file, "w", encoding="utf-8") as f:
                    json.dump(default_settings, f, ensure_ascii=False, indent=4)
                print("✅ Создан settings.json с настройками по умолчанию")
            except Exception as e:
                print(f"⚠️ Не удалось создать settings.json: {e}")
            return default_settings

        try:
            import json
            with open(settings_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            default_settings.update(data)
            return default_settings
        except Exception as e:
            print(f"⚠️ Ошибка загрузки настроек: {e}")
            return default_settings

    def save_settings(self):
        """Сохранение настроек"""
        settings_file = os.path.join(self.base_dir, "settings.json")
        try:
            import json
            with open(settings_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"⚠️ Ошибка сохранения настроек: {e}")

    # ================= UI HELPERS =================
    def _show_back_button(self, command_func):
        tr = self.translations[self.current_lang]
        self.btn_back.config(text=tr["back"], command=command_func)
        if not self.btn_back.winfo_ismapped():
            self.btn_back.pack(side=tk.BOTTOM, fill=tk.X)
        self.glitch_label.place_configure(y=-45)

    def _hide_back_button(self):
        if self.btn_back.winfo_ismapped():
            self.btn_back.pack_forget()
        self.glitch_label.place_configure(y=-30)

    # ================= NAVIGATION =================
    def open_inventory(self):
        self.anim_container.pack_forget()
        self.game_frame.pack_forget()
        self.right_frame.grid_remove()

        if self.inventory_manager is None:
            self.inventory_manager = InventoryManager(
                self, self.game, self.translations, self.current_lang
            )
        self.inventory_manager.open()

    def open_shop(self):
        self.anim_container.pack_forget()
        self.game_frame.pack_forget()
        self.right_frame.grid_remove()

        if self.shop_manager is None:
            self.shop_manager = ShopManager(self, self.translations, self.current_lang)
        self.shop_manager.open()

    def open_authors(self):
        self.anim_container.pack_forget()
        self.game_frame.pack_forget()
        self.right_frame.grid_remove()

        if self.authors_manager is None:
            self.authors_manager = AuthorsManager(self, self.translations, self.current_lang)
        self.authors_manager.open()

    def open_settings(self):
        self.anim_container.pack_forget()
        self.game_frame.pack_forget()
        self.right_frame.grid_remove()

        if self.settings_frame is None:
            self.settings_frame = tk.Frame(self.left_frame)
            self.settings_manager = Settings(self.settings_frame, self)

        self.settings_frame.pack(fill=tk.BOTH, expand=True)
        self._show_back_button(self.close_settings)

    def close_settings(self):
        if self.settings_frame:
            self.settings_frame.pack_forget()
        self.show_game()
        self._hide_back_button()

    # ================= GAME LOGIC =================
    def start_challenge(self):
        tr = self.translations[self.current_lang]
        self.button_click.config(text=tr["click_now"], bg="red", state="normal")
        self.label_result.config(text="", fg="black")
        self.click_count = 0
        self.challenge_active = True
        self.button_click.config(command=self.register_click)
        self.root.after(1000, self.end_challenge)

    def register_click(self):
        if self.challenge_active:
            self.click_count += 1

    def end_challenge(self):
        self.challenge_active = False
        self.button_click.config(command=self.process_result)
        tr = self.translations[self.current_lang]
        self.label_result.config(text=tr["score_message"].format(self.click_count), fg="blue")
        self.button_click.config(text=tr["button_click"], bg="lightblue")

    def process_result(self):
        success, _ = self.game.try_add_point(self.click_count)
        self.court_success.stop()
        self.court_fail.stop()

        if success:
            self.court_success.start_animation()
            self.update_ui(result=1)
        else:
            self.court_fail.start_animation()
            self.update_ui(result=2)

        tr = self.translations[self.current_lang]
        self.button_click.config(text=tr["start_challenge"], command=self.start_challenge)

    # ================= UI & LANGUAGE =================
    def apply_skins(self):
        """Применение выбранных скинов к анимациям"""
        ball_file = self.settings.get("skin_ball", "ball3.png")
        basket_file = self.settings.get("skin_basket", "basket.png")
        for court in (self.court_success, self.court_fail):
            court.set_skins(ball_file, basket_file)

        w = self.animation_canvas.winfo_width()
        h = self.animation_canvas.winfo_height()
        if w > 50 and h > 50 and not self.challenge_active:
            self.animation_canvas.delete("all")
            self.court_success.draw_court()

    def set_language(self, lang):
        self.current_lang = lang
        self.settings["language"] = lang
        self.save_settings()

        tr = self.translations[lang]
        self.root.title(tr["title"])
        self.btn_back.config(text=tr["back"])

        current = self.button_click.cget("text")
        if any(x in current for x in ["start", "начни", "commencer", "Starten", "开始"]):
            self.button_click.config(text=tr["start_challenge"])
        elif any(x in current for x in ["now", "сейчас", "maintenant", "jetzt", "立即"]):
            self.button_click.config(text=tr["click_now"])
        else:
            self.button_click.config(text=tr["button_click"])

        self.label_points.config(text=tr["points"].format(self.game.get_points()))

        self.btn1.config(text=tr["btn_inventory"])
        self.btn2.config(text=tr["btn_shop"])
        self.btn3.config(text=tr["btn_authors"])
        self.btn_settings.config(text=tr["btn_settings"])

        # Обновляем язык в менеджерах
        if self.inventory_manager:
            self.inventory_manager.update_language(lang)
        if self.shop_manager:
            self.shop_manager.update_language(lang)
        if self.authors_manager:
            self.authors_manager.update_language(lang)
        if self.settings_manager:
            self.settings_manager.update_language(lang)

    def update_ui(self, result=None):
        tr = self.translations[self.current_lang]
        self.label_points.config(text=tr["points"].format(self.game.get_points()))
        if result == 1:
            self.label_result.config(text=tr["hit"], fg="green")
        elif result == 2:
            self.label_result.config(text=tr["miss"], fg="red")

    # ================= LIFECYCLE =================
    def show_game(self):
        if self.inventory_manager and self.inventory_manager.inventory_frame:
            self.inventory_manager.inventory_frame.pack_forget()
        if self.shop_manager and self.shop_manager.shop_frame:
            self.shop_manager.shop_frame.pack_forget()
        if self.authors_manager and self.authors_manager.authors_frame:
            self.authors_manager.authors_frame.pack_forget()
        if self.settings_frame:
            self.settings_frame.pack_forget()

        self.anim_container.pack(fill=tk.X, side=tk.TOP, pady=(0, 2))
        self.anim_container.lift()
        self.game_frame.pack(fill=tk.BOTH, expand=True)
        self.right_frame.grid()

        self.update_ui()
        self.root.after(50, self.redraw_animation)

    def on_closing(self):
        self.court_success.stop()
        self.court_fail.stop()
        self.game.save_game()
        self.save_settings()
        self.root.destroy()

    def redraw_animation(self):
        w = self.animation_canvas.winfo_width()
        h = self.animation_canvas.winfo_height()
        if w > 50 and h > 50:
            self.animation_canvas.delete("all")
            self.court_success.draw_court()
        else:
            self.root.after(100, self.redraw_animation)