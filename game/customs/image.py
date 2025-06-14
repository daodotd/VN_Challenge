from kivy.animation import Animation
from kivy.uix.image import Image

class CustomImage(Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.angle = 0

    def wiggle_effect(self, duration: float = 0.8):
        initial_center_x = self.pos_hint.get("center_x", 0.5)

        # Define a wiggle animation sequence by shifting center_x back and forth
        wiggle_animation = (
                Animation(pos_hint={"center_x": initial_center_x + 0.02}, duration=duration)
                + Animation(pos_hint={"center_x": initial_center_x - 0.02}, duration=duration)
                + Animation(pos_hint={"center_x": initial_center_x + 0.01}, duration=duration)
                + Animation(pos_hint={"center_x": initial_center_x - 0.01}, duration=duration)
                + Animation(pos_hint={"center_x": initial_center_x}, duration=duration)
        )

        wiggle_animation.repeat = True
        wiggle_animation.start(self)

    def clear_all_animations(self):
        Animation.cancel_all(self)
        self.angle = 0

    def zoom_in_out_effect(self, repeat=True, duration=0.5):
        default_size_hint = (self.size_hint_x, self.size_hint_y)

        click_size_increase = (
            self.size_hint_x + 0.02,
            self.size_hint_y + 0.02,
        )

        # Create zoom-in and zoom-out animation sequence
        anim = Animation(size_hint=click_size_increase, duration=duration) + Animation(
            size_hint=(
                self.size_hint_x - 0.02,
                self.size_hint_y - 0.02,
            ),
            duration=duration,
        )

        anim += Animation(size_hint=default_size_hint, duration=duration)
        anim.repeat = repeat
        anim.start(self)