import pygame
from gui import Screen, Button, Checkbox, Dropdown, get_font, render_text, strip_emoji


class SettingsScreen(Screen):
    def __init__(self, app):
        super().__init__(app)
        self.language_names = {
            "Английский": {
                "Английский": "English", "Русский": "Russian",
                "Французский": "French", "Немецкий": "German", "Китайский": "Chinese"
            },
            "Русский": {
                "Английский": "Английский", "Русский": "Русский",
                "Французский": "Французский", "Немецкий": "Немецкий", "Китайский": "Китайский"
            },
            "Французский": {
                "Английский": "Anglais", "Русский": "Russe",
                "Французский": "Français", "Немецкий": "Allemand", "Китайский": "Chinois"
            },
            "Немецкий": {
                "Английский": "Englisch", "Русский": "Russisch",
                "Французский": "Französisch", "Немецкий": "Deutsch", "Китайский": "Chinesisch"
            },
            "Китайский": {
                "Английский": "英语", "Русский": "俄语",
                "Французский": "法语", "Немецкий": "德语", "Китайский": "中文"
            },
        }
        self._build_ui()

    def _build_ui(self):
        tr = self.app.translations[self.app.current_lang]
        lang_names = self.language_names.get(self.app.current_lang,
                                             self.language_names["Русский"])
        available = list(self.app.translations.keys())
        display_langs = [lang_names.get(l, l) for l in available]
        self._lang_key_map = {lang_names.get(l, l): l for l in available}

        current_display = lang_names.get(
            self.app.settings.get("language", "Русский"),
            self.app.settings.get("language", "Русский"))

        self.lang_dropdown = Dropdown(
            (300, 100, 250, 35), display_langs, font_size=13,
            selected=current_display, callback=self._on_lang_change)

        self.sound_checkbox = Checkbox(
            (300, 160, 200, 30), tr["sound_on"], font_size=13,
            checked=self.app.settings.get("sound", True),
            callback=self._on_sound_toggle)

        self.btn_save = Button(
            (40, 230, 520, 45), tr["save_button"], font_size=14,
            bg_color=(144, 238, 144), callback=self._on_save)

        self.btn_reset = Button(
            (40, 290, 520, 45), tr["reset_button"], font_size=14,
            bg_color=(240, 128, 128), callback=self._on_reset)

    def _on_lang_change(self, display):
        key = self._lang_key_map.get(display, display)
        self.app.set_language(key)
        self._build_ui()

    def _on_sound_toggle(self, checked):
        self.app.settings["sound"] = checked
        self.app.save_settings()

    def _on_save(self):
        tr = self.app.translations[self.app.current_lang]
        self.app.dialog.show_info(tr["settings_title"], tr["save_success"])

    def _on_reset(self):
        tr = self.app.translations[self.app.current_lang]
        self.app.dialog.show_confirm(
            tr["reset_button"], tr["reset_confirm"], self._confirm_reset,
            yes_text=tr.get("dialog_yes", "Yes"), no_text=tr.get("dialog_no", "No"))

    def _confirm_reset(self, yes):
        if yes:
            tr = self.app.translations[self.app.current_lang]
            try:
                self.app.game.reset_progress()
                self.app.dialog.show_info(tr["reset_button"], tr["reset_done"])
            except Exception as e:
                self.app.dialog.show_info(tr["reset_button"],
                                          f"{tr['reset_error']}:\n{e}")

    def handle_event(self, event):
        if self.lang_dropdown.handle_event(event):
            return
        self.sound_checkbox.handle_event(event)
        self.btn_save.handle_event(event)
        self.btn_reset.handle_event(event)

    def draw(self, surface):
        tr = self.app.translations[self.app.current_lang]
        font_title = get_font(22, bold=True)
        font_label = get_font(14)

        render_text(surface, tr["settings_title"], font_title, (0, 0, 0), 40, 25, 520)

        render_text(surface, tr["language_label"], font_label, (0, 0, 0), 40, 107, 250)
        self.lang_dropdown.draw(surface)

        if not self.lang_dropdown.open:
            render_text(surface, tr["sound_label"], font_label, (0, 0, 0), 40, 165, 250)
            self.sound_checkbox.draw(surface)
            self.btn_save.draw(surface)
            self.btn_reset.draw(surface)
