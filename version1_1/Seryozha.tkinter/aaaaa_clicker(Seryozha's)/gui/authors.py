import tkinter as tk


class AuthorsManager:
    def __init__(self, parent, translations, current_lang):
        self.parent = parent
        self.translations = translations
        self.current_lang = current_lang
        self.tr = self.translations[self.current_lang]

        self.authors_frame = tk.Frame(parent.left_frame)

    def open(self):
        """Открытие экрана авторов"""
        self.tr = self.translations[self.current_lang]

        # Очищаем фрейм
        for widget in self.authors_frame.winfo_children():
            widget.destroy()

        # Заголовок
        tk.Label(
            self.authors_frame,
            text=self.tr["btn_authors"],
            font=("Arial", 16, "bold")
        ).pack(pady=20)

        # Информация об авторах
        authors_text = (
            "👨‍💻 Разработчики:\n\n"
            "  • thekosmoss\n"
            "  • artman\n"
            "  • amonpys\n\n"
            "🏀 Проект: Basketball Click\n"
            "📅 2026 © GlitchHunters Team\n\n"
            "🔧 Версия: 1.0.0"
        )

        tk.Label(
            self.authors_frame,
            text=authors_text,
            font=("Arial", 11),
            justify="center",
            fg="black"
        ).pack(pady=10)

        self.authors_frame.pack(fill=tk.BOTH, expand=True)
        self.parent._show_back_button(self.close)

    def close(self):
        """Закрытие экрана авторов"""
        self.authors_frame.pack_forget()
        # Возвращаемся к игре с анимацией
        self.parent.show_game()
        self.parent._hide_back_button()
        self.parent.update_ui()

    def update_language(self, new_lang):
        """Обновление языка"""
        self.current_lang = new_lang
        self.tr = self.translations[self.current_lang]