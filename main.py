from kivy.clock import Clock
from kivy.core.audio import Sound, SoundLoader
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.uix.screenmanager import FadeTransition, ScreenManager
from kivymd.app import MDApp

from game.database.config_manager import ConfigManager
from game.database.score_manager import ScoreManager
from game.screen.loading_screen import LoadingScreen
from game.screen.main_menu import MainMenu
from game.screen.select_topic_menu import QuizGameScreen
from game.screen_quiz_topic1 import Topic1Screen
from game.screen_quiz_topic1.hard import Topic1HardScreen
from game.screen_quiz_topic1.chill import Topic1ChillScreen
from game.screen_quiz_topic2 import Topic2Screen
from game.screen_quiz_topic2.hard import Topic2HardScreen
from game.screen_quiz_topic2.chill import Topic2ChillScreen
from game.utils.calculate_window import CalculateWindow
from game.screen.tiles_game_screen import TilesGameScreen

_version_ = "2.1.5"

# Debugging - Enable debug-level logging
Logger.setLevel("DEBUG")

# Set dev screen - 9:16 ratio
Window.size = CalculateWindow(380, (9, 16)).get_size()

# Init fonts
LabelBase.register(name="bevnpro_medium", fn_regular="assets/font/bevnpro_medium.ttf")
LabelBase.register(name="roboto_medium", fn_regular="assets/font/roboto_medium.ttf")

class VNChallengeApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.title = "Viet Nam Challenge"

        self.configs_manager = ConfigManager()
        self.score_manager = ScoreManager()
        self.backsound = None

        self.screen_manager = ScreenManager(transition=FadeTransition(duration=0.5))
        self._init_screen()

        # Load background music
        self.backsound: Sound = SoundLoader.load("assets/sounds/back.mp3")

        # Fade animation parameters
        self._fade_interval = 0.1
        self._fade_out_step = 0.05
        self._fade_in_step = 0.05
        self._max_volume = 0.5

    def _init_screen(self):
        """Add all game screens to the screen manager"""
        # Loading Screen
        self.screen_manager.add_widget(LoadingScreen(name="loading_screen", app=self))

        # Home Menu and Game Selection Screens
        self.screen_manager.add_widget(MainMenu(name="main_menu", app=self))
        self.screen_manager.add_widget(QuizGameScreen(name="quiz_game", app=self))
        self.screen_manager.add_widget(TilesGameScreen(name="tiles_game", app=self))

        # Select topic menu
        self.screen_manager.add_widget(Topic1Screen(name="go_topic1", app=self))
        self.screen_manager.add_widget(Topic2Screen(name="go_topic2", app=self))

        # Topic 1 - Gameplay difficulty levels
        self.screen_manager.add_widget(Topic1HardScreen(name="topic1_hard", app=self))
        self.screen_manager.add_widget(Topic1ChillScreen(name="topic1_chill", app=self))

        # Topic 2 - Gameplay difficulty levels
        self.screen_manager.add_widget(Topic2HardScreen(name="topic2_hard", app=self))
        self.screen_manager.add_widget(Topic2ChillScreen(name="topic2_chill", app=self))

    def build(self):
        """Set initial screen to loading screen"""
        self.screen_manager.current = "loading_screen"
        return self.screen_manager

    def on_start(self):
        if self.configs_manager.get("mute"):
            self.stop_backsound(immediate=True)
        else:
            self.play_backsound()

        return super().on_start()

    def on_stop(self):
        self.stop_backsound(immediate=True)
        return super().on_stop()

    def navigate_back(self):
        self.screen_manager.current = self.screen_manager.previous()

    def switch_screen(self, screen_name):
        """Switch to a specified screen"""
        if not self.screen_manager:
            raise ValueError("Screen manager is not initialized.")
        Logger.debug(f"Switching to screen: {screen_name}")     # Add debug logging
        self.screen_manager.current = screen_name

    def stop_backsound(self, immediate=False):
        """Stop the background sound with optional fade-out effect"""
        if self.backsound:
            if immediate:
                self.backsound.stop()
            else:
                Clock.schedule_interval(self._fade_out_volume, self._fade_interval)

    def _fade_out_volume(self, dt):
        """Reduce the volume down to fade-out background sound"""
        fade_step = self._fade_out_step * dt / self._fade_interval
        if self.backsound.volume > 0:
            self.backsound.volume = max(0, self.backsound.volume - fade_step)
        else:
            self.backsound.stop()
            return False
        return True

    def play_backsound(self):
        """Play the background sound with fade-in effect"""
        if self.backsound and self.backsound.state != "play":
            self.backsound.loop = True
            self.backsound.volume = 0
            self.backsound.play()
            Clock.schedule_interval(self._fade_in_volume, self._fade_interval)

    def _fade_in_volume(self, dt):
        """Increase the volume up to fade-in background sound"""
        fade_step = self._fade_in_step * dt / self._fade_interval
        if self.backsound.volume < self._max_volume:
            self.backsound.volume = min(
                self._max_volume, self.backsound.volume + fade_step
            )
            return True
        return False

if __name__ == "__main__":
    VNChallengeApp().run()
