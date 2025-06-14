from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.animation import Animation
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.progressbar import ProgressBar
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle

from game.layouts.default_bg import WithDefaultBG

class LoadingScreen(WithDefaultBG):
    """Loading screen with animated logo, progress bar and transition effects"""

    def __init__(self, app, **kwargs):
        super(LoadingScreen, self).__init__(**kwargs)

        self.app = app
        self.progress_value = 0
        self.progress_event = None

        self.layout = FloatLayout(
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )

        # Set Background for Loading Screen
        self.bg_image = Image(
            source="assets/image/load_screen/bg.png",
            size_hint=(1, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        self.layout.add_widget(self.bg_image)

        # Add a black overlay covering the entire screen
        self.overlay = FloatLayout(size_hint=(1, 1))
        with self.overlay.canvas:
            self.overlay_color = Color(0, 0, 0, 1)  # Black (RGBA)
            self.overlay_rect = Rectangle(pos=self.overlay.pos, size=self.overlay.size)

        # Bind to allow the overlay to resize with the screen
        self.overlay.bind(size=self._update_rect, pos=self._update_rect)
        self.layout.add_widget(self.overlay)

        # Add Logo for Loading Screen
        self.team_logo = Image(
            source="assets/image/load_screen/logo.png",
            size_hint=(0.4, 0.4),
            pos_hint={"center_x": 0.5, "center_y": 0.22},
            opacity=0
        )
        self.layout.add_widget(self.team_logo)

        # Create a container for progress bar and text
        progress_container = FloatLayout(
            size_hint=(0.8, 0.3),
            pos_hint={"center_x": 0.5, "center_y": 0.1}
        )

        self.progress_bar = ProgressBar(
            max=100,
            value=0,
            size_hint=(1, 0.1),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )

        self.loading_text = Label(
            text="Đang tải... 0%",
            halign="center",
            color=(0.3, 0.3, 0.3, 1),
            font_name="bevnpro_medium",
            font_size="16sp",
            pos_hint={"center_x": 0.5, "center_y": 0.4}
        )

        progress_container.add_widget(self.progress_bar)
        progress_container.add_widget(self.loading_text)
        self.layout.add_widget(progress_container)

        self.add_widget(self.layout)

    def _update_rect(self, instance, *_):
        self.overlay_rect.pos = instance.pos
        self.overlay_rect.size = instance.size

    def on_enter(self):
        """Set a moving effect from black to light"""
        black_to_bright = Animation(a=0, duration=0.5)
        black_to_bright.bind(on_complete=self._show_logo)
        black_to_bright.start(self.overlay_color)

    def _show_logo(self, *_):
        """Set show the logo after the effect fades away"""
        logo_anim = Animation(opacity=1, duration=0.5)
        logo_anim.start(self.team_logo)

        Clock.schedule_once(self.start_loading, 0.1)

    def start_loading(self, *_):
        self.progress_event = Clock.schedule_interval(self.update_progress, 0.1)

    def update_progress(self, *_):
        """Simulate loading progress"""
        if self.progress_value < 100:
            increment = min(5, 100 - self.progress_value)
            self.progress_value += increment
            self.progress_bar.value = self.progress_value
            self.loading_text.text = f"Đang tải trò chơi... {int(self.progress_value)}%"
        else:
            Clock.unschedule(self.progress_event)  # Loading complete
            self.loading_text.text = "Đã tải xong"
            Clock.schedule_once(self.go_to_main_menu, 0.4)

    def go_to_main_menu(self, *_):
        self.app.switch_screen("main_menu")