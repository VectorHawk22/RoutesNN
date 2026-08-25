import tkinter as tk


class ShopManager:
    def __init__(self, parent, translations, current_lang):
        self.parent = parent
        self.translations = translations
        self.current_lang = current_lang
        self.tr = self.translations[self.current_lang]

        self.shop_frame = tk.Frame(parent.left_frame)

    def open(self):
        """Открытие магазина"""
        self.tr = self.translations[self.current_lang]

        # Очищаем фрейм
        for widget in self.shop_frame.winfo_children():
            widget.destroy()

        # Интерфейс магазина
        tk.Label(
            self.shop_frame,
            text=self.tr["btn_shop"],
            font=("Arial", 16, "bold")
        ).pack(pady=20)

        tk.Label(
            self.shop_frame,
            text="🏪 Магазин временно закрыт",
            font=("Arial", 14),
            fg="gray"
        ).pack(pady=20)

        tk.Label(
            self.shop_frame,
            text="🚧 Ведутся технические работы\n\n"
                 "Скоро здесь появятся новые товары!",
            font=("Arial", 11),
            fg="gray",
            justify="center"
        ).pack(pady=20)

        self.shop_frame.pack(fill=tk.BOTH, expand=True)
        self.parent._show_back_button(self.close)

    def close(self):
        """Закрытие магазина"""
        self.shop_frame.pack_forget()
        # Возвращаемся к игре с анимацией
        self.parent.show_game()
        self.parent._hide_back_button()
        self.parent.update_ui()

    def update_language(self, new_lang):
        """Обновление языка"""
        self.current_lang = new_lang
        self.tr = self.translations[self.current_lang]