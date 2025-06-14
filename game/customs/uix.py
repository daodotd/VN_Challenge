from kivy.animation import Animation
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.graphics import Color, Line
from kivy.properties import (
    ListProperty,
    NumericProperty,
)
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.label import Label


class ImageWithBorder(Image):
    """Extended Image widget that can display an optional border"""

    def __init__(self, show_border=False, **kwargs):
        super().__init__(**kwargs)
        self.border = None      # Initialize border attribute

        if show_border:
            with self.canvas.before:
                Color(1, 0, 0, 1)
                self.border = Line(
                    rectangle=(self.x, self.y, self.width, self.height), width=2
                )
            self.bind(pos=self._update_border, size=self._update_border)

    def _update_border(self, _instance, _value):
        if self.border:
            self.border.rectangle = (self.x, self.y, self.width, self.height)


class CustomButton(ButtonBehavior, ImageWithBorder):
    scale = NumericProperty(1.0)

    def __init__(
            self,
            app,
            destination="",
            click_sound_path="assets/sounds/click.mp3",
            show_border=False,
            clicked_scale_max=0.02,
            **kwargs
    ):
        super(CustomButton, self).__init__(show_border=show_border, **kwargs)

        self.app = app

        self.destination = destination if destination != "" else None
        self.clicked_scale_max = clicked_scale_max

        self.click_sound = (
            SoundLoader.load(click_sound_path) if click_sound_path else None
        )

        self.scale_up: Animation | None = None
        self.scale_down: Animation | None = None

        self._calculate_size_hints()
        Window.bind(on_resize=self._on_window_resize)

        if self.click_sound:
            self.click_sound.bind(on_stop=self._trigger_screen_change)

    def _on_window_resize(self, _instance, _width, _height):
        self._calculate_size_hints()

    def _trigger_screen_change(self, _instance):
        if not self.destination:
            return

        if self.destination == "previous":
            self.app.back_screen()
        else:
            self.app.switch_screen(self.destination)

    def _calculate_size_hints(self):
        """Prepares scale-up and scale-down animations for size hint changes"""
        default_scale = (self.size_hint_x, self.size_hint_y)
        click_scale_increase = (
            self.size_hint_x + self.clicked_scale_max,
            self.size_hint_y + self.clicked_scale_max,
        )

        # Define animations for scaling down to default and scaling up when clicked
        self.scale_down = Animation(size_hint=default_scale, duration=0.2)
        self.scale_up = Animation(size_hint=click_scale_increase, duration=0.2)

    def is_point_inside_image(self, x, y):
        if not self.texture:
            return False

        # Take the real size of texture compared to the widget size
        texture_width = self.texture.width
        texture_height = self.texture.height

        # Calculate the ratio between widget and texture size
        width_ratio = self.width / texture_width
        height_ratio = self.height / texture_height

        # Choose a smaller ratio to keep the correct ratio
        scale = min(width_ratio, height_ratio)

        # Calculate the actual size of the image in widget
        real_width = texture_width * scale
        real_height = texture_height * scale

        # Calculate the central location of the image
        center_x = self.center_x
        center_y = self.center_y

        # Calculate the boundary of the real image
        left = center_x - real_width / 2
        right = center_x + real_width / 2
        bottom = center_y - real_height / 2
        top = center_y + real_height / 2

        return left <= x <= right and bottom <= y <= top

    def on_touch_down(self, touch):
        if self.disabled:
            return False

        # Only handle the touch event when it is in the real image area
        if not self.is_point_inside_image(*touch.pos):
            return False

        if self.click_sound:
            self.click_sound.play()

        if self.scale_up:
            self.scale_up.start(self)

        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        """Only release the event when it starts from the real image area"""
        if self.is_point_inside_image(*touch.pos):
            if self.scale_down:
                self.scale_down.start(self)

        return super().on_touch_up(touch)

    def jiggle_effect(self):
        """Create a Jiggle animation for the button"""
        jiggle = Animation(
            pos_hint={"x": self.pos_hint["x"] + 0.01, "y": self.pos_hint.get("y", 0.5)},
            duration=0.1,
        ) + Animation(
            pos_hint={"x": self.pos_hint["x"] - 0.01, "y": self.pos_hint.get("y", 0.5)},
            duration=0.1,
        )
        jiggle.start(self)

    def start_wiggle(self, repeat=True, duration=0.5):
        default_size_hint = (self.size_hint_x, self.size_hint_y)

        click_size_increase = (
            self.size_hint_x + self.clicked_scale_max,
            self.size_hint_y + self.clicked_scale_max,
        )

        anim = Animation(size_hint=click_size_increase, duration=duration) + Animation(
            size_hint=(
                self.size_hint_x - self.clicked_scale_max,
                self.size_hint_y - self.clicked_scale_max,
            ),
            duration=duration,
        )

        anim += Animation(size_hint=default_size_hint, duration=duration)
        anim.repeat = repeat
        anim.start(self)

    def stop_animation(self):
        Animation.cancel_all(self)

    def set_disabled_state(self, disable: bool, custom_color=None):
        """Disable the button and apply a grayscale effect if disabled, or a custom color if provided"""
        self.disabled = disable
        if disable:
            self.color = custom_color if custom_color else (0.5, 0.5, 0.5, 1)
        else:
            self.color = (1, 1, 1, 1)


class OutlinedLabel(Label):
    font_color = ListProperty([1, 0.85, 0, 1])
    outline_color = ListProperty([0, 0, 1, 1])
    outline_width = NumericProperty(3)
    custom_font_size = NumericProperty(20)

    def __init__(
            self,
            font_color=None,
            outline_color=None,
            outline_width=1,
            custom_font_size=50,
            **kwargs
    ):
        super().__init__(**kwargs)

        # Initialize outline attribute
        self.outline = None

        if font_color is None:
            font_color = [0, 0, 0, 1]
        if outline_color is None:
            outline_color = [1, 1, 1, 1]

        self.font_color = font_color
        self.outline_color = outline_color
        self.outline_width = outline_width
        self.custom_font_size = custom_font_size

        self.color = self.font_color
        self.font_size = f"{self.custom_font_size}sp"

        self.bind(
            outline_color=self.update_outline_color,
            outline_width=self.update_outline_width,
            custom_font_size=self.update_font_size,
            font_color=self.update_font_color,
        )

    def update_outline_color(self, _instance, _value):
        """Update the widget's outline color and redraw the outline"""
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.outline_color)
            self.outline = Line(
                width=self.outline_width,
                rectangle=(self.x, self.y, self.width, self.height),
            )

    def update_outline_width(self, _instance, _value):
        if self.outline:
            self.outline.width = self.outline_width

    def update_font_size(self, _instance, _value):
        self.font_size = f"{self.custom_font_size}sp"

    def update_font_color(self, _instance, _value):
        self.color = self.font_color