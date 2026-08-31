import pygame
from gui import Screen, Button, Checkbox, Dropdown, get_font, render_text, strip_emoji
from gui.inputbox import InputBox


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
        self.active_tab = "game"
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

        tab_w = 130
        is_game = self.active_tab == "game"
        is_promos = self.active_tab == "promos"
        self.btn_tab_game = Button(
            (40, 55, tab_w, 35), tr["settings_title"], font_size=12,
            bg_color=(180, 220, 255) if is_game else (220, 220, 220),
            callback=lambda: self._switch_tab("game"))
        self.btn_tab_promos = Button(
            (175, 55, tab_w, 35), tr["promos_title"], font_size=12,
            bg_color=(255, 225, 130) if is_promos else (220, 220, 220),
            callback=lambda: self._switch_tab("promos"))

        self.lang_dropdown = Dropdown(
            (300, 110, 250, 35), display_langs, font_size=13,
            selected=current_display, callback=self._on_lang_change)

        self.sound_checkbox = Checkbox(
            (300, 170, 200, 30), tr["sound_on"], font_size=13,
            checked=self.app.settings.get("sound", True),
            callback=self._on_sound_toggle)

        self.btn_save = Button(
            (40, 240, 520, 45), tr["save_button"], font_size=14,
            bg_color=(144, 238, 144), callback=self._on_save)

        self.btn_reset = Button(
            (40, 300, 520, 45), tr["reset_button"], font_size=14,
            bg_color=(240, 128, 128), callback=self._on_reset)

        self.promo_input = InputBox(
            (40, 150, 380, 38), font_size=15, max_length=32,
            placeholder="", callback=self._on_promo_activate_enter)

        self.btn_promo = Button(
            (425, 150, 135, 38), tr["promo_activate"], font_size=13,
            bg_color=(255, 215, 0), callback=self._on_promo_activate)

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
            self.app.dialog.show_info(tr["promos_title"], tr["promo_success"].format(amount))
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
        self.btn_tab_game.handle_event(event)
        self.btn_tab_promos.handle_event(event)
        if self.active_tab == "game":
            self.lang_dropdown.handle_event(event)
            self.sound_checkbox.handle_event(event)
            self.btn_save.handle_event(event)
            self.btn_reset.handle_event(event)
        else:
            self.promo_input.handle_event(event)
            self.btn_promo.handle_event(event)

    def draw(self, surface):
        tr = self.app.translations[self.app.current_lang]
        font_title = get_font(22, bold=True)
        font_label = get_font(14)

        render_text(surface, tr["settings_title"], font_title, (0, 0, 0), 40, 15, 520)

        self.btn_tab_game.draw(surface)
        self.btn_tab_promos.draw(surface)

        if self.active_tab == "game":
            render_text(surface, tr["language_label"], font_label, (0, 0, 0), 40, 115, 250)
            self.lang_dropdown.draw(surface)

            if not self.lang_dropdown.open:
                render_text(surface, tr["sound_label"], font_label, (0, 0, 0), 40, 175, 250)
                self.sound_checkbox.draw(surface)
                self.btn_save.draw(surface)
                self.btn_reset.draw(surface)
        else:
            render_text(surface, tr["promo_label"], font_label, (0, 0, 0), 40, 112, 380)
            pygame.draw.line(surface, (180, 180, 180), (40, 210), (560, 210), 1)
            self.promo_input.draw(surface)
            self.btn_promo.draw(surface)
