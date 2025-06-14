from kivymd.uix.floatlayout import MDFloatLayout

from game.customs.uix import CustomButton
from game.layouts.default_bg import WithDefaultBG

class QuizGameScreen(WithDefaultBG):
    """Quiz topic selection screen with animated topic buttons"""

    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)

        self.app = app

        self.topic1_button = None
        self.topic2_button = None

        self.layout = MDFloatLayout(
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        self.setup_ui()

        self.add_widget(self.layout)

    def setup_ui(self):
        back_button = CustomButton(
            app=self.app,
            size_hint=(0.1, 0.1),
            destination="main_menu",
            source="assets/image/buttons/back.png",
            pos_hint={"center_x": 0.9, "center_y": 0.95},
        )
        self.layout.add_widget(back_button)

        # Set Topic 1 button
        self.topic1_button = CustomButton(
            app=self.app,
            destination="go_topic1",
            source="assets/image/topic/topic1.png",
            size_hint=(0.88, 0.5),
            pos_hint={"center_x": 0.5, "center_y": 0.7},
        )
        self.layout.add_widget(self.topic1_button)

        # Set Topic 2 button
        self.topic2_button = CustomButton(
            app=self.app,
            destination="go_topic2",
            source="assets/image/topic/topic2.png",
            size_hint=(0.79, 0.5),
            pos_hint={"center_x": 0.5, "center_y": 0.3},
        )
        self.layout.add_widget(self.topic2_button)

    def on_pre_enter(self, *args):
        """Start the wiggling animation for the buttons before entering the screen"""
        self.topic1_button.start_wiggle(duration=2)
        self.topic2_button.start_wiggle(duration=2)
        return super().on_pre_enter(*args)

    def on_pre_leave(self, *args):
        """Stop the wiggling animation for the buttons before leaving the screen"""
        self.topic1_button.stop_animation()
        self.topic2_button.stop_animation()
        return super().on_pre_leave(*args)