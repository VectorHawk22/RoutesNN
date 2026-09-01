# -*- coding: utf-8 -*-
"""Settings screen: game settings tab + promo codes tab."""
from gui.screen import Screen
from gui.button import KButton
from gui.checkbox import KCheckbox
from gui.dropdown import KDropdown
from gui.inputbox import InputBox


class SettingsScreen(Screen):
    def __init__(self, app):
        super().__init__(app)
        self.language_names = {
            "Английский": {
                "Английский": "English", "Русский": "Russian",
                "Французский": "French", "Немецкий": "German", "Китайский": "Chinese",
            },
            "Русский": {
                "Английский": "Английский", "Русский": "Русский",
                "Французский": "Французский", "Немецкий": "Немецкий", "Китайский": "Китайский",
            },
            "Французский": {
                "Английский": "Anglais", "Русский": "Russe",
                "Французский": "Français", "Немецкий": "Allemand", "Китайский": "Chinois",
            },
            "Немецкий": {
                "Английский": "Englisch", "Русский": "Russisch",
                "Французский": "Französisch", "Немецкий": "Deutsch", "Китайский": "Chinesisch",
            },
            "Китайский": {
                "Английский": "英语", "Русский": "俄语",
                "Французский": "法语", "Немецкий": "德语", "Китайский": "中文",
            },
        }
        self.active_tab = "game"
        self.btn_tab_game = None
        self.btn_tab_promos = None
        self.lang_dropdown = None
        self.sound_checkbox = None
        self.btn_save = None
        self.btn_reset = None
        self.promo_input = None
        self.btn_promo = None
        self._build_ui()

    def _clear(self):
        for w in list(self.children):
            self.remove_widget(w)

    def _build_ui(self):
        self._clear()
        tr = self.app.translations[self.app.current_lang]
        lang_names = self.language_names.get(self.app.current_lang,
                                             self.language_names["Русский"])
        available = list(self.app.translations.keys())
        display_langs = [lang_names.get(l, l) for l in available]
        self._lang_key_map = {lang_names.get(l, l): l for l in available}
        current_display = lang_names.get(
            self.app.settings.get("language", "Русский"),
            self.app.settings.get("language", "Русский"))

        tab_w = 130
        is_game = self.active_tab == "game"
        is_promos = self.active_tab == "promos"

        self.btn_tab_game = KButton(
            (40, 55, tab_w, 35), tr["settings_title"], font_size=12,
            bg_color=(180, 220, 255) if is_game else (220, 220, 220),
            callback=lambda: self._switch_tab("game"))
        self.btn_tab_promos = KButton(
            (175, 55, tab_w, 35), tr["promos_title"], font_size=12,
            bg_color=(255, 225, 130) if is_promos else (220, 220, 220),
            callback=lambda: self._switch_tab("promos"))
        self.add_widget(self.btn_tab_game)
        self.add_widget(self.btn_tab_promos)

        if self.active_tab == "game":
            self.lang_dropdown = KDropdown(
                (300, 110, 250, 35), display_langs, font_size=13,
                selected=current_display, callback=self._on_lang_change)
            self.sound_checkbox = KCheckbox(
                (300, 170, 200, 30), tr["sound_on"], font_size=13,
                checked=self.app.settings.get("sound", True),
                callback=self._on_sound_toggle)
            self.btn_save = KButton(
                (40, 240, 520, 45), tr["save_button"], font_size=14,
                bg_color=(144, 238, 144), callback=self._on_save)
            self.btn_reset = KButton(
                (40, 300, 520, 45), tr["reset_button"], font_size=14,
                bg_color=(240, 128, 128), callback=self._on_reset)
            self.add_widget(self.lang_dropdown)
            self.add_widget(self.sound_checkbox)
            self.add_widget(self.btn_save)
            self.add_widget(self.btn_reset)
        else:
            self.promo_input = InputBox(
                (40, 150, 380, 38), font_size=15, max_length=32,
                placeholder="", callback=self._on_promo_activate_enter)
            self.btn_promo = KButton(
                (425, 150, 135, 38), tr["promo_activate"], font_size=13,
                bg_color=(255, 215, 0), callback=self._on_promo_activate)
            self.add_widget(self.promo_input)
            self.add_widget(self.btn_promo)

    def _switch_tab(self, name):
        self.active_tab = name
        self._build_ui()

    def _on_promo_activate_enter(self, text):
        if text.strip():
            self._on_promo_activate()

    def _on_promo_activate(self):
        tr = self.app.translations[self.app.current_lang]
        code = self.promo_input.text
        if not code.strip():
            self.app.dialog.show_info(tr["promos_title"], tr["promo_empty"])
            return
        amount = self.app.game.redeem_promo(code)
        self.promo_input.clear()
        if amount:
            self.app.dialog.show_info(tr["promos_title"],
                                     tr["promo_success"].format(amount))
        else:
            self.app.dialog.show_info(tr["promos_title"], tr["promo_fail"])

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
            yes_text=tr.get("dialog_yes", "Yes"),
            no_text=tr.get("dialog_no", "No"))

    def _confirm_reset(self, yes):
        if yes:
            tr = self.app.translations[self.app.current_lang]
            try:
                self.app.game.reset_progress()
                self.app.dialog.show_info(tr["reset_button"], tr["reset_done"])
            except Exception as e:
                self.app.dialog.show_info(tr["reset_button"],
                                          f"{tr['reset_error']}:\n{e}")

    def on_enter(self):
        self._build_ui()

    def touch_down(self, x, y):
        # Close the language dropdown when tapping elsewhere on screen.
        if self.lang_dropdown and self.lang_dropdown.open:
            self.lang_dropdown.close()
        return False

    def draw(self, painter):
        tr = self.app.translations[self.app.current_lang]
        painter.text(tr["settings_title"], 22, (0, 0, 0), 40, 15,
                     bold=True, max_width=520)

        if self.active_tab == "game":
            painter.text(tr["language_label"], 14, (0, 0, 0), 40, 115,
                         max_width=250)
            if self.lang_dropdown and not self.lang_dropdown.open:
                painter.text(tr["sound_label"], 14, (0, 0, 0), 40, 175,
                             max_width=250)
        else:
            painter.text(tr["promo_label"], 14, (0, 0, 0), 40, 112,
                         max_width=380)
            painter.line(40, 210, 560, 210, (180, 180, 180))