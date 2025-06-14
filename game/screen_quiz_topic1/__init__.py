from kivymd.uix.floatlayout import MDFloatLayout

from game.customs.uix import CustomButton
from game.layouts.default_bg import WithDefaultBG


class Topic1Screen(WithDefaultBG):
    """Screen for Topic 1 selection with hard and chill mode options"""

    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.layout = MDFloatLayout(pos_hint={"center_x": 0.5, "center_y": 0.5})
        self.setup_ui()
        self.add_widget(self.layout)

    def setup_ui(self):
        back_button = CustomButton(
            app=self.app,
            size_hint=(0.1, 0.1),
            destination="quiz_game",
            source="assets/image/buttons/back.png",
            pos_hint={"center_x": 0.9, "center_y": 0.95},
        )
        self.layout.add_widget(back_button)

        # Set hard button - Try Hard Button
        hard_button = CustomButton(
            app=self.app,
            size_hint=(0.85, 0.6),
            destination="topic1_hard",
            source="assets/image/select_level/topic1/1.png",
            pos_hint={"center_x": 0.5, "center_y": 0.65},
        )
        self.layout.add_widget(hard_button)

        # Set chill button - Chill Guy Button
        chill_button = CustomButton(
            app=self.app,
            size_hint=(0.85, 0.6),
            destination="topic1_chill",
            source="assets/image/select_level/topic1/2.png",
            pos_hint={"center_x": 0.5, "center_y": 0.3},
        )
        self.layout.add_widget(chill_button)