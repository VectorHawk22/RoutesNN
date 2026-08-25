import tkinter as tk
from tkinter import messagebox
import json
import os


class Settings:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app

        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.settings_file = os.path.join(self.base_dir, "settings.json")

        # Единый источник настроек - словарь приложения
        self.settings = self.app.settings

        self._rebuild_id = None
        self.build_ui()

    def save_settings(self):
        """Сохранение настроек приложения в файл"""
        return self.app.save_settings()

    def get_language(self):
        return self.settings.get("language", "Русский")

    def get_sound(self):
        return self.settings.get("sound", True)

    def update_language(self, new_lang):
        """Обновление языка интерфейса (вызывается из app.set_language)"""
        self.schedule_rebuild()

    def schedule_rebuild(self):
        """Отложенная перестройка UI - чтобы не уничтожать виджеты
        внутри колбэка самого виджета"""
        if self._rebuild_id:
            try:
                self.parent.after_cancel(self._rebuild_id)
            except Exception:
                pass
        self._rebuild_id = self.parent.after(10, self._do_rebuild)

    def _do_rebuild(self):
        self._rebuild_id = None
        # Перестраиваем только если экран настроек сейчас показан
        if self.parent.winfo_ismapped():
            self.build_ui()

    def get_language_names(self):
        """Возвращает словарь с названиями языков на текущем языке"""
        # Словарь перевода названий языков
        language_names = {
            "Английский": {
                "Английский": "English",
                "Русский": "Russian",
                "Французский": "French",
                "Немецкий": "German",
                "Китайский": "Chinese"
            },
            "Русский": {
                "Английский": "Английский",
                "Русский": "Русский",
                "Французский": "Французский",
                "Немецкий": "Немецкий",
                "Китайский": "Китайский"
            },
            "Французский": {
                "Английский": "Anglais",
                "Русский": "Russe",
                "Французский": "Français",
                "Немецкий": "Allemand",
                "Китайский": "Chinois"
            },
            "Немецкий": {
                "Английский": "Englisch",
                "Русский": "Russisch",
                "Французский": "Französisch",
                "Немецкий": "Deutsch",
                "Китайский": "Chinesisch"
            },
            "Китайский": {
                "Английский": "英语",
                "Русский": "俄语",
                "Французский": "法语",
                "Немецкий": "德语",
                "Китайский": "中文"
            }
        }
        return language_names.get(self.app.current_lang, language_names["Русский"])

    def build_ui(self):
        """Построение интерфейса настроек"""
        # Очищаем parent
        for widget in self.parent.winfo_children():
            widget.destroy()

        # Получаем переводы
        tr = self.app.translations[self.app.current_lang]

        # Заголовок
        title = tk.Label(
            self.parent,
            text=tr["settings_title"],
            font=("Arial", 20, "bold")
        )
        title.pack(pady=(25, 20))

        # Язык
        language_frame = tk.Frame(self.parent)
        language_frame.pack(fill=tk.X, padx=40, pady=10)

        tk.Label(
            language_frame,
            text=tr["language_label"],
            font=("Arial", 12)
        ).pack(side=tk.LEFT)

        self.language_var = tk.StringVar(value=self.settings.get("language", "Русский"))

        # Получаем названия языков на текущем языке
        lang_names = self.get_language_names()
        available_langs = list(self.app.translations.keys())

        # Создаём список для отображения в меню
        display_langs = [lang_names.get(lang, lang) for lang in available_langs]

        # Создаём словарь для обратного преобразования
        self.lang_display_to_key = {lang_names.get(lang, lang): lang for lang in available_langs}

        # Создаём меню с переведёнными названиями
        self.language_menu = tk.OptionMenu(
            language_frame,
            self.language_var,
            *display_langs,
            command=self.on_language_change
        )
        self.language_menu.config(width=15, font=("Arial", 10))
        self.language_menu.pack(side=tk.RIGHT)

        # Устанавливаем текущее значение (отображаемое)
        current_display = lang_names.get(self.settings.get("language", "Русский"),
                                         self.settings.get("language", "Русский"))
        self.language_var.set(current_display)

        # Звук
        sound_frame = tk.Frame(self.parent)
        sound_frame.pack(fill=tk.X, padx=40, pady=10)

        tk.Label(
            sound_frame,
            text=tr["sound_label"],
            font=("Arial", 12)
        ).pack(side=tk.LEFT)

        self.sound_var = tk.BooleanVar(value=self.settings.get("sound", True))
        sound_text = tr["sound_on"] if self.sound_var.get() else tr["sound_off"]

        self.sound_check = tk.Checkbutton(
            sound_frame,
            text=sound_text,
            variable=self.sound_var,
            command=self.on_sound_toggle,
            font=("Arial", 10)
        )
        self.sound_check.pack(side=tk.RIGHT)

        # Кнопка сохранения
        save_button = tk.Button(
            self.parent,
            text=tr["save_button"],
            font=("Arial", 11, "bold"),
            bg="lightgreen",
            command=self.save_and_close
        )
        save_button.pack(fill=tk.X, padx=40, pady=(25, 8))

        # Кнопка сброса
        reset_button = tk.Button(
            self.parent,
            text=tr["reset_button"],
            font=("Arial", 11, "bold"),
            bg="lightcoral",
            command=self.reset_progress
        )
        reset_button.pack(fill=tk.X, padx=40, pady=8)

    def on_language_change(self, display_lang):
        """Обработка смены языка"""
        # Преобразуем отображаемое название в ключ
        lang_key = self.lang_display_to_key.get(display_lang, display_lang)

        # app.set_language обновит словарь, сохранит файл и вызовет
        # update_language -> отложенную перестройку UI
        self.app.set_language(lang_key)

    def on_sound_toggle(self):
        """Обработка переключения звука"""
        self.settings["sound"] = self.sound_var.get()
        self.save_settings()
        # Обновляем текст кнопки звука
        tr = self.app.translations[self.app.current_lang]
        sound_text = tr["sound_on"] if self.sound_var.get() else tr["sound_off"]
        self.sound_check.config(text=sound_text)

    def save_and_close(self):
        """Сохранение и закрытие настроек"""
        # Получаем реальный ключ языка из отображаемого названия
        display_lang = self.language_var.get()
        lang_key = self.lang_display_to_key.get(display_lang, display_lang)

        self.settings["sound"] = self.sound_var.get()
        self.settings["language"] = lang_key

        tr = self.app.translations[self.app.current_lang]

        if self.save_settings():
            messagebox.showinfo("✅", tr["save_success"])
            self.app.close_settings()
        else:
            messagebox.showerror("❌", tr["save_error"])

    def reset_progress(self):
        """Сброс прогресса игры"""
        tr = self.app.translations[self.app.current_lang]

        answer = messagebox.askyesno(
            "⚠️",
            tr["reset_confirm"]
        )

        if not answer:
            return

        try:
            self.app.game.reset_progress()
            self.app.update_ui()
            messagebox.showinfo("✅", tr["reset_done"])
        except Exception as e:
            messagebox.showerror(
                "❌",
                f"{tr['reset_error']}:\n{e}"
            )