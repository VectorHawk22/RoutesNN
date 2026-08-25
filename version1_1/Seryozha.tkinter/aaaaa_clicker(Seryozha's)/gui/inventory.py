import tkinter as tk
import os
from PIL import Image, ImageTk


class InventoryManager:
    def __init__(self, parent, game, translations, current_lang):
        self.parent = parent
        self.game = game
        self.translations = translations
        self.current_lang = current_lang
        self.tr = self.translations[self.current_lang]

        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.animation_dir = os.path.join(self.base_dir, "animation")

        # Фрейм инвентаря
        self.inventory_frame = tk.Frame(parent.left_frame)

        # Атрибуты для зелья
        self.potion_frame = None
        self.potion_btn = None
        self.potion_timer_label = None
        self.photo = None
        self.empty_photo = None
        self.image_label = None
        self.update_id = None

        # Вкладки и скины
        self.active_tab = "potions"
        self.tab_buttons = {}
        self.tab_container = None
        self.skin_items = {}
        self.section_labels = {}
        self._thumb_refs = []

        self.ball_skins = ["ball1.png", "ball2.png", "ball3.png", "ball4.png"]
        self.basket_skins = ["basket.png", "basket2.png", "basket3.png", "basket4.png"]

    # ================= OPEN / CLOSE =================
    def open(self):
        """Открытие инвентаря"""
        self.tr = self.translations[self.current_lang]

        for widget in self.inventory_frame.winfo_children():
            widget.destroy()

        self.inventory_frame.pack(fill=tk.BOTH, expand=True)

        # Заголовок
        tk.Label(
            self.inventory_frame,
            text=self.tr["inventory"],
            font=("Arial", 16, "bold")
        ).pack(pady=(15, 5))

        # Панель вкладок
        tab_bar = tk.Frame(self.inventory_frame)
        tab_bar.pack(pady=(0, 10))

        self.tab_buttons = {
            "potions": tk.Button(
                tab_bar,
                text=self.tr["tab_potions"],
                font=("Arial", 11, "bold"),
                width=14,
                command=lambda: self.show_tab("potions")
            ),
            "skins": tk.Button(
                tab_bar,
                text=self.tr["tab_skins"],
                font=("Arial", 11, "bold"),
                width=14,
                command=lambda: self.show_tab("skins")
            ),
        }
        self.tab_buttons["potions"].pack(side=tk.LEFT, padx=6)
        self.tab_buttons["skins"].pack(side=tk.LEFT, padx=6)

        # Контейнер содержимого вкладки
        self.tab_container = tk.Frame(self.inventory_frame)
        self.tab_container.pack(fill=tk.BOTH, expand=True)

        self.show_tab(self.active_tab)

        # Показываем кнопку назад
        self.parent._show_back_button(self.close)

    def show_tab(self, name):
        """Переключение вкладок"""
        self.active_tab = name

        # Подсветка активной вкладки
        for key, btn in self.tab_buttons.items():
            if key == name:
                btn.config(bg="lightblue", relief="solid", bd=2)
            else:
                btn.config(bg="SystemButtonFace", relief="flat", bd=1)

        # Очищаем контейнер
        for widget in self.tab_container.winfo_children():
            widget.destroy()

        # Останавливаем таймер зелья при уходе со вкладки
        self.stop_updates()

        self.skin_items = {}
        self.section_labels = {}

        if name == "potions":
            self.build_potions_tab()
        else:
            self.build_skins_tab()

    def build_potions_tab(self):
        """Содержимое вкладки зелий"""
        # Фрейм зелья
        self.potion_frame = tk.Frame(
            self.tab_container,
            relief="ridge",
            bd=3,
            bg="lightyellow",
            highlightbackground="gold",
            highlightthickness=2,
            width=250,
            height=170
        )
        self.potion_frame.pack(pady=20, padx=(20, 10), anchor="w")
        self.potion_frame.pack_propagate(False)

        top_frame = tk.Frame(self.potion_frame, bg="lightyellow")
        top_frame.place(x=10, y=10, width=230, height=100)

        image_frame = tk.Frame(top_frame, bg="lightyellow", width=80, height=80)
        image_frame.pack(side=tk.LEFT, padx=(0, 10))
        image_frame.pack_propagate(False)

        self.load_images()

        is_active = self.game.is_potion_active()
        current_img = self.empty_photo if is_active else self.photo

        if current_img:
            self.image_label = tk.Label(
                image_frame,
                image=current_img,
                bg="lightyellow"
            )
            self.image_label.image = current_img
        else:
            self.image_label = tk.Label(
                image_frame,
                text="🧪",
                font=("Arial", 32),
                bg="lightyellow"
            )
        self.image_label.pack(expand=True)

        text_frame = tk.Frame(top_frame, bg="lightyellow")
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(
            text_frame,
            text=self.tr["potion"],
            bg="lightyellow",
            font=("Arial", 10, "bold"),
            anchor="w"
        ).pack(fill=tk.X, pady=(0, 5))

        self.potion_btn = tk.Button(
            text_frame,
            font=("Arial", 9),
            width=14,
            command=self.use_potion
        )
        self.potion_btn.pack(anchor="w")

        self.potion_timer_label = tk.Label(
            self.potion_frame,
            text="",
            bg="lightyellow",
            fg="black",
            font=("Arial", 9),
            anchor="w",
            justify="left"
        )
        self.potion_timer_label.place(x=10, y=115, width=230, height=45)

        self.update_button()
        self.update_timer()
        self.start_updates()

    def build_skins_tab(self):
        """Содержимое вкладки скинов"""
        body = tk.Frame(self.tab_container)
        body.pack(padx=15, pady=5, fill=tk.BOTH, expand=True)

        # === МЯЧИ ===
        self.section_labels["balls"] = tk.Label(
            body,
            text="🏀 " + self.tr["skins_balls"] + ":",
            font=("Arial", 11, "bold"),
            anchor="w"
        )
        self.section_labels["balls"].pack(fill=tk.X, pady=(0, 5))

        balls_row = tk.Frame(body)
        balls_row.pack(pady=(0, 12))
        for i, fname in enumerate(self.ball_skins, start=1):
            self._make_skin_item(balls_row, "ball", fname, str(i))

        # === КОРЗИНЫ ===
        self.section_labels["baskets"] = tk.Label(
            body,
            text="🧺 " + self.tr["skins_baskets"] + ":",
            font=("Arial", 11, "bold"),
            anchor="w"
        )
        self.section_labels["baskets"].pack(fill=tk.X, pady=(0, 5))

        baskets_row = tk.Frame(body)
        baskets_row.pack()
        for i, fname in enumerate(self.basket_skins, start=1):
            self._make_skin_item(baskets_row, "basket", fname, str(i))

        self.update_skin_highlights()

    def _make_skin_item(self, parent_row, kind, filename, caption):
        """Создание элемента выбора скина"""
        selected_file = self.parent.settings.get(
            "skin_ball" if kind == "ball" else "skin_basket", ""
        )
        is_selected = (filename == selected_file)

        item = tk.Frame(
            parent_row,
            width=86,
            height=100,
            bd=2,
            relief="solid",
            highlightthickness=2,
            highlightbackground="#0078D7" if is_selected else "#cccccc",
            bg="#eaf4ff" if is_selected else "SystemButtonFace"
        )
        item.pack(side=tk.LEFT, padx=7)
        item.pack_propagate(False)

        thumb = self._load_thumb(os.path.join(self.animation_dir, filename))
        if thumb:
            img_label = tk.Label(item, image=thumb, bg=item.cget("bg"))
            img_label.image = thumb
            self._thumb_refs.append(thumb)
        else:
            img_label = tk.Label(item, text="❔", font=("Arial", 20), bg=item.cget("bg"))
        img_label.pack(expand=True)

        tk.Label(item, text=caption, font=("Arial", 9), bg=item.cget("bg")).pack(pady=(0, 3))

        for w in (item, img_label):
            w.bind("<Button-1>", lambda e, k=kind, f=filename: self.select_skin(k, f))

        self.skin_items[(kind, filename)] = item

    def _load_thumb(self, path, box=56):
        """Миниатюра скина: обрезка прозрачных полей + вписывание в квадрат"""
        try:
            if not os.path.exists(path):
                return None
            img = Image.open(path).convert("RGBA")
            mask = img.getchannel("A").point(lambda a: 255 if a > 100 else 0)
            bbox = mask.getbbox()
            if bbox:
                img = img.crop(bbox)
            w, h = img.size
            scale = min(box / float(w), box / float(h))
            size = (max(1, int(w * scale)), max(1, int(h * scale)))
            img = img.resize(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"⚠️ Ошибка миниатюры {path}: {e}")
            return None

    def select_skin(self, kind, filename):
        """Выбор скина мяча или корзины"""
        key = "skin_ball" if kind == "ball" else "skin_basket"
        self.parent.settings[key] = filename
        self.parent.save_settings()
        self.parent.apply_skins()
        self.update_skin_highlights()

    def update_skin_highlights(self):
        """Обновление подсветки выбранных скинов"""
        current_ball = self.parent.settings.get("skin_ball", "")
        current_basket = self.parent.settings.get("skin_basket", "")

        for (kind, filename), item in self.skin_items.items():
            current = current_ball if kind == "ball" else current_basket
            is_selected = (filename == current)
            item.config(
                highlightbackground="#0078D7" if is_selected else "#cccccc",
                bg="#eaf4ff" if is_selected else "SystemButtonFace"
            )
            for child in item.winfo_children():
                child.config(bg=item.cget("bg"))

    # ================= IMAGES =================
    def load_images(self):
        """Загрузка изображений зелья из папки images"""
        try:
            images_dir = os.path.join(self.base_dir, "images")

            full_path = os.path.join(images_dir, "potionthatgives2xcoins.png")
            empty_path = os.path.join(images_dir, "emptypotionthatgives2xcoins.png")

            if os.path.exists(full_path):
                img = Image.open(full_path).resize((80, 80), Image.Resampling.LANCZOS)
                self.photo = ImageTk.PhotoImage(img)
            else:
                print(f"⚠️ Файл не найден: {full_path}")

            if os.path.exists(empty_path):
                img = Image.open(empty_path).resize((80, 80), Image.Resampling.LANCZOS)
                self.empty_photo = ImageTk.PhotoImage(img)
            else:
                print(f"⚠️ Файл не найден: {empty_path}")

        except Exception as e:
            print(f"⚠️ Ошибка загрузки изображений зелья: {e}")

    # ================= NAVIGATION =================
    def close(self):
        """Закрытие инвентаря"""
        self.stop_updates()
        self.inventory_frame.pack_forget()
        self.parent.show_game()
        self.parent._hide_back_button()
        self.parent.update_ui()

    # ================= POTION =================
    def use_potion(self):
        """Использование зелья"""
        if self.game.activate_potion():
            self.update_button()
            self.update_timer()
            self.update_image()
            self.parent.update_ui()
            self.parent.label_result.config(text="🧪 Эффект x2 активирован!", fg="green")

            self.potion_frame.config(bg="lightgreen")
            self.potion_timer_label.config(bg="lightgreen")
            self.parent.root.after(3000, self._reset_colors)
        else:
            self.parent.label_result.config(text="⏳ Эффект уже активен!", fg="orange")

    def _reset_colors(self):
        """Сброс цветов после анимации"""
        if self.potion_frame:
            self.potion_frame.config(bg="lightyellow")
        if self.potion_timer_label:
            self.potion_timer_label.config(bg="lightyellow")

    def update_button(self):
        """Обновление состояния кнопки"""
        tr = self.translations[self.current_lang]
        is_active = self.game.is_potion_active()

        if self.potion_btn:
            if is_active:
                self.potion_btn.config(text=tr["use"], state="disabled")
            else:
                self.potion_btn.config(text=tr["potion_inactive"], state="normal")

    def update_timer(self):
        """Обновление таймера"""
        tr = self.translations[self.current_lang]
        time_left = self.game.get_potion_time_left()

        if self.potion_timer_label:
            if time_left > 0:
                self.potion_timer_label.config(
                    text=tr["potion_active"].format(time_left),
                    bg="lightgreen"
                )
            else:
                self.potion_timer_label.config(text="", bg="lightyellow")

    def update_image(self):
        """Обновление изображения зелья"""
        if not self.image_label:
            return

        is_active = self.game.is_potion_active()
        current_img = self.empty_photo if is_active else self.photo

        if current_img:
            self.image_label.config(image=current_img)
            self.image_label.image = current_img

    def start_updates(self):
        """Запуск периодического обновления"""
        if self.active_tab != "potions":
            return
        self.update_timer()
        self.update_button()
        self.update_image()
        self.update_id = self.parent.root.after(1000, self.start_updates)

    def stop_updates(self):
        """Остановка обновления"""
        if self.update_id:
            try:
                self.parent.root.after_cancel(self.update_id)
            except:
                pass
            self.update_id = None

    # ================= LANGUAGE =================
    def update_language(self, new_lang):
        """Обновление языка"""
        self.current_lang = new_lang
        self.tr = self.translations[self.current_lang]

        if hasattr(self, 'potion_btn') and self.potion_btn:
            self.update_button()

        if "potions" in self.tab_buttons:
            self.tab_buttons["potions"].config(text=self.tr["tab_potions"])
        if "skins" in self.tab_buttons:
            self.tab_buttons["skins"].config(text=self.tr["tab_skins"])

        if "balls" in self.section_labels:
            self.section_labels["balls"].config(text="🏀 " + self.tr["skins_balls"] + ":")
        if "baskets" in self.section_labels:
            self.section_labels["baskets"].config(text="🧺 " + self.tr["skins_baskets"] + ":")
