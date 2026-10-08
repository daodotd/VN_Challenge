from kivy.uix.button import Button
from kivy.uix.image import Image
from kivymd.uix.floatlayout import MDFloatLayout
import webbrowser

from game.customs.image import CustomImage
from game.customs.uix import CustomButton, OutlinedLabel
from game.layouts.default_bg import WithDefaultBG


class MainMenu(WithDefaultBG):
    """Main menu screen with game buttons, mute controls and info popup"""

    def __init__(self, app, **kwargs):
        super(MainMenu, self).__init__(**kwargs)

        self.app = app

        self.layout = MDFloatLayout(
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )

        # Set Background MainMenu
        background = Image(
            source="assets/image/main_menu/bg.png",
            size_hint=(1, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        self.layout.add_widget(background)

        # Set Logo Viet Nam Challenge
        logo = CustomImage(
            source="assets/image/main_menu/logo.png",
            size_hint=(0.8, 0.8),       # % width and height
            pos_hint={"center_x": 0.5, "center_y": 0.75},
        )
        logo.wiggle_effect(duration=1)
        self.layout.add_widget(logo)

        # Set Start button - Play Game Quiz
        start_button = CustomButton(
            app=self.app,
            destination="quiz_game",
            source="assets/image/buttons/quiz_game.png",
            size_hint=(0.48, 0.1),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        self.layout.add_widget(start_button)

        # Set 3 Tiles button - Play 3 Tiles Match Game
        tiles_button = CustomButton(
            app=self.app,
            destination="tiles_game",
            source="assets/image/buttons/tiles_game.png",
            size_hint=(0.48, 0.1),
            pos_hint={"center_x": 0.5, "center_y": 0.4},
        )
        self.layout.add_widget(tiles_button)

        # Set Exit button - Exit Game
        exit_button = CustomButton(
            app=self.app,
            source="assets/image/buttons/exit.png",
            size_hint=(0.48, 0.1),
            pos_hint={"center_x": 0.5, "center_y": 0.3},
        )
        exit_button.bind(on_release=lambda *_: self.app.stop())
        self.layout.add_widget(exit_button)

        self._init_mute()
        self._init_info_button()

        self.add_widget(self.layout)

    def _init_mute(self):
        """Set unmute and mute button - Sound of game music"""
        is_muted = self.app.configs_manager.get("mute") or False

        icon = (
            "assets/image/buttons/mute.png" if is_muted else "assets/image/buttons/unmute.png"
        )

        self.button_mute = CustomButton(
            app=self.app,
            source=icon,
            size_hint=(0.12, 0.08),
            pos_hint={"center_x": 0.1, "center_y": 0.95},
        )
        self.button_mute.bind(on_press=self._update_mute)
        self.layout.add_widget(self.button_mute)

    def _update_mute(self, *_):
        is_muted = self.app.configs_manager.get("mute") or False

        if is_muted:
            self.button_mute.source = "assets/image/buttons/unmute.png"
            self.app.play_backsound()
            self.app.configs_manager.set("mute", False)
        else:
            self.button_mute.source = "assets/image/buttons/mute.png"
            self.app.stop_backsound(immediate=True)
            self.app.configs_manager.set("mute", True)

    def _init_info_button(self):
        """Set Info Button - Bar popup information about game"""
        self.button_info = CustomButton(
            app=self.app,
            source="assets/image/buttons/info.png",
            size_hint=(0.12, 0.08),
            pos_hint={"center_x": 0.9, "center_y": 0.95},
        )
        self.button_info.bind(on_press=self._show_info_popup)
        self.layout.add_widget(self.button_info)

    def _show_info_popup(self, *_):
        popup_layout = MDFloatLayout()

        background_dim = Button(
            background_color=(0, 0, 0, 0.5),
            size_hint=(1, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        popup_layout.add_widget(background_dim)

        # Set Bar popup information
        bar_inf = Image(
            source="assets/image/buttons/bar_info.png",
            size_hint=(0.85, 0.85),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        popup_layout.add_widget(bar_inf)

        # Set Text for the content of the information- Popup Info Button
        font_size = 16      # Size font

        info_text = OutlinedLabel(
            text="by Nguyễn Đỗ Anh Đào",
            custom_font_size=font_size,
            font_name="roboto_medium",
            pos_hint={"center_x": 0.5, "center_y": 0.52}
        )
        popup_layout.add_widget(info_text)

        # Set Facebook Button - Popup Info Button
        fb_button = CustomButton(
            app=self.app,
            source="assets/image/buttons/fb.png",
            size_hint=(0.12, 0.12),
            pos_hint={"center_x": 0.35, "center_y": 0.4}
        )
        fb_button.bind(on_press=lambda _: self._open_link("https://www.facebook.com/punmon1002"))
        popup_layout.add_widget(fb_button)

        # Set Instagram Button - Popup Info Button
        ig_button = CustomButton(
            app=self.app,
            source="assets/image/buttons/ig.png",
            size_hint=(0.12, 0.12),
            pos_hint={"center_x": 0.5, "center_y": 0.4}
        )
        ig_button.bind(on_press=lambda _: self._open_link("https://www.instagram.com/punmon.102"))
        popup_layout.add_widget(ig_button)

        # Set YouTube Button - Popup Info Button
        yt_button = CustomButton(
            app=self.app,
            source="assets/image/buttons/yt.png",
            size_hint=(0.12, 0.12),
            pos_hint={"center_x": 0.65, "center_y": 0.4}
        )
        yt_button.bind(on_press=lambda _: self._open_link("https://www.youtube.com/@P9x-tech"))
        popup_layout.add_widget(yt_button)

        # Set Close Button - Popup Info Button
        close_button = CustomButton(
            app=self.app,
            source="assets/image/buttons/close.png",
            size_hint=(0.12, 0.08),
            pos_hint={"center_x": 0.5, "center_y": 0.31}
        )
        close_button.bind(on_press=lambda _: self._close_info_popup(popup_layout))
        popup_layout.add_widget(close_button)

        self.add_widget(popup_layout)

        self.info_popup = popup_layout

    @staticmethod
    def _open_link(url):
        webbrowser.open(url)

    def _close_info_popup(self, popup_layout):
        self.remove_widget(popup_layout)