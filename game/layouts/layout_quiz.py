import random
import os

from kivy.clock import Clock
from kivy.core.audio import Sound, SoundLoader
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivymd.uix.floatlayout import MDFloatLayout

from game.customs.image import CustomImage
from game.customs.uix import CustomButton, OutlinedLabel
from game.layouts.default_bg import WithDefaultBG


class LayoutQuest(MDFloatLayout):
    """Custom quiz layout with timer, options, sounds, and decorations"""

    __events__ = ("on_complete", "on_timeout", "on_go_home")

    def __init__(
            self,
            app,
            background_image: str,
            home_screen: str,
            timeout_bar_image: str,
            question: str,
            correct_answer: str,
            option_a_image: str,
            option_b_image: str,
            option_c_image: str,
            background_music: str = "",
            content_font_size: str = 20,
            timeout_duration: float = 10.0,
            decorations: list[CustomImage] = None,
            question_size_hint: tuple = (None, None),
            options_size_hint: tuple = (0.9, 0.08),
            **kwargs,
    ):
        super(LayoutQuest, self).__init__(**kwargs)

        self.app = app
        self.home_screen = home_screen
        self.background_image = background_image
        self.question = question
        self.timeout_bar_image = timeout_bar_image
        self.content_font_size = content_font_size
        self.decorations = [] if decorations is None else decorations
        self.option_images = [option_a_image, option_b_image, option_c_image]

        # Save custom sizes
        self.question_size_hint = question_size_hint
        self.options_size_hint = options_size_hint

        self.timeout_duration = timeout_duration
        self.elapsed_time = 0.0
        self.remaining_time = int(timeout_duration)
        self.correct_answer = correct_answer
        self.answered = False
        self.user_answer = ""

        self.start_time = None

        self.max_score = 100    # Maximum score for a correct answer
        self.base_time = 5.0    # First 5 seconds maintain max score

        self.wrong_sound: Sound | None = SoundLoader.load("assets/sounds/fail.mp3")
        self.correct_sound: Sound | None = SoundLoader.load("assets/sounds/correct.mp3")

        self.bg_music = None

        self.timeout_event = None
        self._check_called = False

        Clock.schedule_once(self._verify_call)

    def _verify_call(self, dt):
        if not self._check_called:
            raise ValueError("Quest not initiated with call_screen()")

    def _initialize_ui(self):
        """Set UI components for the quiz layout"""
        background = Image(
            source=self.background_image,
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            fit_mode="fill",
        )
        self.add_widget(background)

        # Set Home button - Go back Main menu
        home_button = CustomButton(
            app=self.app,
            source="assets/image/buttons/home.png",
            size_hint=(0.12, 0.08),
            destination=None,
            pos_hint={"center_x": 0.1, "center_y": 0.95},
        )
        home_button.bind(on_press=self._go_to_main_menu)
        self.add_widget(home_button)

        # Create and add the timeout bar image to the screen
        timeout_bar = CustomImage(
            source=self.timeout_bar_image,
            size_hint=(0.5, 0.1),
            pos_hint={"center_x": 0.73, "center_y": 0.95},
        )
        self.add_widget(timeout_bar)

        self.timeout_label = Label(
            text=f"{int(self.timeout_duration)} Giây",
            font_name="roboto_medium",
            font_size="32sp",
            pos_hint={"center_x": 0.78, "center_y": 0.95},
        )
        self.add_widget(self.timeout_label)

        # Setup lyrics layout and option buttons
        self._create_lyrics_layout()
        self._initialize_option_buttons()

    def _create_lyrics_layout(self):
        """Create and configure the lyrics layout"""
        quest = CustomImage(
            source=self.question,
            pos_hint={"center_x": 0.5, "center_y": 0.65},
            size_hint=self.question_size_hint,
        )
        self.add_widget(quest)

        for deco in self.decorations:
            if deco.parent:
                deco.parent.remove_widget(deco)
            self.add_widget(deco)

    def _initialize_option_buttons(self):
        """Initialize answer buttons and set their positions"""
        y_position = 0.35
        self.answer_buttons = []

        for i, option_image in enumerate(self.option_images):
            button = CustomButton(
                app=self.app,
                source=option_image,
                size_hint=self.options_size_hint,
                pos_hint={"center_x": 0.5, "center_y": y_position},
                click_sound_path="",
            )
            button.bind(
                on_press=lambda btn, index=i: self._evaluate_answer(
                    chr(97 + index)
                )
            )
            self.add_widget(button)
            self.answer_buttons.append(button)
            y_position -= 0.1

    def _go_to_main_menu(self, instance):
        self.stop_quest()

        if not self.app.configs_manager.get("mute"):
            self.app.play_backsound()

        self.app.switch_screen("main_menu")

    def reset_quest(self):
        """Reset the quiz and go to Main menu screen"""
        self.stop_quest()

        if not self.app.configs_manager.get("mute"):
            self.app.play_backsound()

    def _evaluate_answer(self, answer):
        """Check if the selected answer is correct and update state"""
        if self.answered:
            return

        self.answered = True
        self.user_answer = answer
        is_correct = answer == self.correct_answer.lower()

        if self.timeout_event:
            self.timeout_event.cancel()

        # Calculate score based on time
        # Score is calculated based on accuracy and response time:
        # - Wrong answer = 0 points.
        # - Correct answer: full score if answered within first 5 seconds, then linearly decreasing over time.
        score = 0
        if is_correct:
            if self.elapsed_time <= self.base_time:
                score = self.max_score
            else:
                seconds_after_base = int(self.elapsed_time - self.base_time)
                points_per_second = self.max_score / (self.timeout_duration - self.base_time)
                deduction = int(seconds_after_base * points_per_second)
                score = max(0, int(self.max_score - deduction))

            score = int(score)

        if self.correct_sound and is_correct:
            self.correct_sound.play()
        elif self.wrong_sound and not is_correct:
            self.wrong_sound.play()

        self.disable_buttons(True)

        self.dispatch("on_complete", is_correct, answer, self.remaining_time, score)

    def disable_buttons(self, disable: bool):
        """Disable buttons and highlight correct answer"""
        colors = [
            (1, 1, 0, 1) if chr(97 + i) == self.correct_answer.lower() else (0.5, 0.5, 0.5, 1)
            for i in range(3)
        ]
        for button, color in zip(self.answer_buttons, colors):
            button.set_disabled_state(disable, custom_color=color)

    def call_screen(self):
        """Initialize and start the question screen with countdown timer"""
        self._check_called = True

        self._initialize_ui()

        self.elapsed_time = 0.0              # Reset the elapsed time
        self.start_time = Clock.get_time()   # Store the start time
        self.remaining_time = int(self.timeout_duration)
        self.timeout_label.text = f"{self.remaining_time} Giây"

        self.dispatch("on_timeout", int(self.timeout_duration))
        Clock.schedule_once(
            lambda dt: setattr(
                self, 'timeout_event', Clock.schedule_interval(self._update_timer, 0.1)
            ),
            0.1
        )

    def _update_timer(self, dt):
        """Update timer"""
        current_time = Clock.get_time()
        self.elapsed_time = current_time - self.start_time

        remaining_seconds = self.timeout_duration - self.elapsed_time
        new_remaining_time = max(0, int(remaining_seconds + 0.99))      # Add 0.99 to round up properly

        if new_remaining_time != self.remaining_time:
            self.remaining_time = new_remaining_time
            self.timeout_label.text = f"{self.remaining_time} Giây"

        if remaining_seconds <= 0:
            self.handle_timeout()

    def handle_timeout(self):
        """Handle the timer timeout"""
        if not self.answered:
            self.answered = True

            if self.wrong_sound:
                self.wrong_sound.play()
            self.disable_buttons(True)

            if self.timeout_event:
                self.timeout_event.cancel()     # Cancel the timer event

            self.dispatch("on_timeout", 0)      # Dispatch the timeout event
            self.dispatch("on_complete", False, None, 0, 0)

    def stop_quest(self):
        """Stop the current quiz session and reset timer/state"""
        if self.timeout_event:
            self.timeout_event.cancel()
            self.timeout_event = None

        # Reset internal state
        self.answered = False
        self.elapsed_time = 0.0
        self.start_time = None
        self.remaining_time = int(self.timeout_duration)

        self.timeout_label.text = f"{self.remaining_time} Giây"

        self.disable_buttons(False)

    def on_complete(self, is_correct, answer, remaining_time, score):
        pass

    def on_timeout(self, remaining_time):
        pass

    def on_go_home(self):
        pass


class LayoutFinish(MDFloatLayout):
    """Finish screen layout with score display and navigation buttons"""

    __events__ = ("on_go_home", "on_restart_quest", "on_exit")

    def __init__(self, app, group_key_store, key_store, destination, **kwargs):
        super(LayoutFinish, self).__init__(**kwargs)

        self.app = app
        self.destination = destination

        store: dict = app.score_manager.get_score(group_key_store, key_store)

        last_score: dict = store.get("last_score", {})
        score_last_score = last_score.get("score", 0)

        best_score: dict = store.get("best_score", {})
        score_best_score = best_score.get("score", 0)

        # Base background for the finish screen
        background = Image(
            source="assets/image/bg.png",
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            fit_mode="fill",
        )
        self.add_widget(background)

        # Set Background Finish
        finish_background = CustomImage(
            source="assets/image/quiz/finish/bg_finish.png",
            size_hint=(1, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            fit_mode="fill",
        )
        self.add_widget(finish_background)

        self.finish_box = CustomImage(
            source="assets/image/quiz/finish/finish_box.png",
            size_hint=(0.95, 0.95),
            pos_hint={"center_x": 0.5, "center_y": 0.64},
        )
        self.add_widget(self.finish_box)

        font_size = 26      # Font Size score and high score

        # Set Score
        self.label_score = OutlinedLabel(
            text="Tổng điểm:",
            custom_font_size=font_size,
            font_name="roboto_medium",
            pos_hint={"center_x": 0.5, "center_y": 0.7},
        )
        self.add_widget(self.label_score)
        self.label_result_score = OutlinedLabel(
            text=f"{score_last_score}",
            custom_font_size=font_size,
            font_name="roboto_medium",
            pos_hint={"center_x": 0.5, "center_y": 0.66},
        )
        self.add_widget(self.label_result_score)

        # Set High Score
        self.label_best_score = OutlinedLabel(
            text="Điểm cao nhất:",
            custom_font_size=font_size,
            font_name="roboto_medium",
            pos_hint={"center_x": 0.5, "center_y": 0.6},
        )
        self.add_widget(self.label_best_score)
        self.label_result_best_score = OutlinedLabel(
            text=f"{score_best_score}",
            custom_font_size=font_size,
            font_name="roboto_medium",
            pos_hint={"center_x": 0.5, "center_y": 0.56},
        )
        self.add_widget(self.label_result_best_score)

        # Set Replay Button - Finish
        button_restart = CustomButton(
            app=app,
            size_hint=(0.5, 0.1),
            source="assets/image/quiz/finish/replay.png",
            pos_hint={"center_x": 0.5, "center_y": 0.4},
        )
        button_restart.bind(
            on_press=lambda instance: self.dispatch("on_restart_quest")
        )
        self.add_widget(button_restart)

        # Set Main Menu Button - Finish
        button_main_menu = CustomButton(
            app=app,
            size_hint=(0.5, 0.1),
            source="assets/image/quiz/finish/main_menu.png",
            destination=None,
            pos_hint={"center_x": 0.5, "center_y": 0.3},
        )
        button_main_menu.bind(
            on_press=lambda instance: self._go_to_main_menu(app)
        )
        self.add_widget(button_main_menu)

        # Set Exit Button - Finish
        button_exit = CustomButton(
            app=app,
            size_hint=(0.5, 0.1),
            source="assets/image/quiz/finish/exit.png",
            pos_hint={"center_x": 0.5, "center_y": 0.2},
        )
        button_exit.bind(
            on_press=lambda instance: self.dispatch("on_exit")
        )
        self.add_widget(button_exit)

        self.bg_sound = SoundLoader.load("assets/sounds/finish.mp3")

        if self.bg_sound:
            self.bg_sound.volume = 1
            self.bg_sound.play()

    def _go_to_main_menu(self, app):
        if self.bg_sound:
            self.bg_sound.stop()
        app.switch_screen("main_menu")

    def on_go_home(self):
        pass

    def on_restart_quest(self):
        pass

    def on_exit(self):
        pass


class LayoutScreen(WithDefaultBG):
    """Main quiz screen manager that handles question flow, music, and game progression"""

    def __init__(
            self,
            app,
            group_key_store: str,
            key_store: str,
            questions_data: list[dict],
            home_destination: str,
            bar_timeout_src: str,
            timeout_duration=10.0,
            question_size_hint: tuple = (None, None),
            options_size_hint: tuple = (0.9, 0.08),
            questions_per_game: int = 5,
            music_directory: str = None,
            **kwargs,
    ):
        super().__init__(**kwargs)

        self.app = app
        self._questions_data = questions_data
        self._home_destination = home_destination
        self._bar_timeout_src = bar_timeout_src
        self._timeout_duration = timeout_duration
        self._group_key_store = group_key_store
        self._key_store = key_store
        self._questions_per_game = min(questions_per_game, len(questions_data))

        self._question_size_hint = question_size_hint
        self._options_size_hint = options_size_hint

        # Music folder - use the corresponding Topic folder if not explicitly specified
        self._music_directory = music_directory or f"assets/music/{group_key_store}"

        self.background_music = None
        self.available_music_files = []
        self._music_replay_schedule = None

        self.bg_image_path = "assets/image/bg.png"

        self.base_layout = MDFloatLayout()
        self.add_widget(self.base_layout)

        self.current_question_index = 0
        self.questions_cache = []
        self.current_question = None
        # Initialize start_time in __init__ to avoid the warning
        self.start_time = None
        self._next_schedule = None
        self.finish = None

        self._selected_questions = []

    def _load_available_music(self):
        self.available_music_files = []

        # Check if the folder exists
        if not os.path.exists(self._music_directory):
            print(f"Warning: Music directory {self._music_directory} does not exist")
            return

        # Browse through the folder to find all mp3 files
        for root, dirs, files in os.walk(self._music_directory):
            for file in files:
                if file.endswith(".mp3"):
                    full_path = os.path.join(root, file)
                    self.available_music_files.append(full_path)

        print(f"Found {len(self.available_music_files)} music files in {self._music_directory}")

    def _play_random_background_music(self):
        if self.background_music:
            self.background_music.stop()
            self.background_music = None
        if self._music_replay_schedule:
            self._music_replay_schedule.cancel()
            self._music_replay_schedule = None

        if not self.available_music_files:
            return

        random_music_file = random.choice(self.available_music_files)
        self.background_music = SoundLoader.load(random_music_file)

        if self.background_music and not self.app.configs_manager.get("mute"):
            self.background_music.volume = 0.5
            self.background_music.play()

            def on_music_stop(dt):
                if not self.is_quiz_complete() and not self.finish and self.background_music:
                    self._play_random_background_music()

            duration = self.background_music.length
            if duration > 0:
                self._music_replay_schedule = Clock.schedule_once(on_music_stop, duration)

    def _reset_screen_layout(self):
        """Clear the layout for the next question or screen reset"""
        self.base_layout.clear_widgets()

    def _reset_cache(self):
        self.current_question_index = 0
        self.questions_cache = []
        self.current_question = None
        self.start_time = None
        self._next_schedule = None
        self.finish = None

        self._selected_questions = []

        if self.background_music:
            self.background_music.stop()
            self.background_music = None
        if self._music_replay_schedule:
            self._music_replay_schedule.cancel()
            self._music_replay_schedule = None

    def is_quiz_complete(self):
        """Check if all questions have been answered"""
        return self.current_question_index >= self._questions_per_game

    def _show_question(self):
        """Display the current question on the screen"""
        if self.start_time is None:
            self.start_time = Clock.get_time()

        if self.current_question:
            self.base_layout.remove_widget(self.current_question)
            self.current_question = None

        if self.is_quiz_complete():
            self._finish_quiz()
            return

        # Get question from the randomly selected subset
        question_data = self._selected_questions[self.current_question_index]

        question_size = question_data.get("question_size_hint", self._question_size_hint)
        options_size = question_data.get("options_size_hint", self._options_size_hint)

        self.current_question = LayoutQuest(
            app=self.app,
            background_image=self.bg_image_path,
            home_screen=self._home_destination,
            timeout_bar_image=self._bar_timeout_src,
            content_font_size=question_data.get("font_content_size", "20sp"),
            timeout_duration=self._timeout_duration,
            question=question_data.get("question", ""),
            correct_answer=question_data.get("answer", ""),
            decorations=question_data.get("decorations", None),
            option_a_image=question_data.get("btn_a_src", ""),
            option_b_image=question_data.get("btn_b_src", ""),
            option_c_image=question_data.get("btn_c_src", ""),
            question_size_hint=question_size,    # Add size question
            options_size_hint=options_size,      # Add size options
        )
        self.current_question.call_screen()
        self.current_question.bind(on_complete=self._next_question)
        self.base_layout.add_widget(self.current_question)

    def _next_question(self, instance, is_correct, value, elapsed_time, score):
        """Process the results of the current question and move to the next"""
        if instance:
            self.questions_cache.append(
                {
                    "score": score,
                    "value": value,
                    "elapsed_time": elapsed_time,
                    "timestamp": Clock.get_time(),
                }
            )

        if self.is_quiz_complete():
            self._finish_quiz()
        else:
            self.current_question_index += 1
            self._next_schedule = Clock.schedule_once(
                lambda dt: self._show_question(), 2
            )

    def restart_quest(self):
        """Restart the quiz from the beginning"""
        self._reset_screen_layout()
        self._reset_cache()

        # Select a new set of random questions
        self._selected_questions = random.sample(self._questions_data, self._questions_per_game)

        # Reload the music list and start playing background music
        self._load_available_music()
        self._play_random_background_music()

        self.current_question_index = 0
        self._show_question()

    def exit_app(self):
        if self.background_music:
            self.background_music.stop()
        self.app.stop()

    def on_pre_enter(self):
        """Prepare the screen when it is about to be displayed"""
        if not self.app.configs_manager.get("mute"):
            self.app.stop_backsound()

        self.current_question_index = 0

        # Randomly select a subset of questions for this game
        self._selected_questions = random.sample(self._questions_data, self._questions_per_game)

        self._load_available_music()
        self._play_random_background_music()

        self._show_question()
        return super().on_pre_enter()

    def on_pre_leave(self):
        """Stop the timer when the screen is about to be left"""
        if not self.app.configs_manager.get("mute"):
            self.app.play_backsound()

        if self._next_schedule:
            self._next_schedule.cancel()
            self._next_schedule = None

        if self.current_question:
            self.current_question.stop_quest()
            self.base_layout.remove_widget(self.current_question)
            self.current_question = None

        if self.finish:
            self.base_layout.remove_widget(self.finish)
            self.finish = None

        if self.background_music:
            self.background_music.stop()
            self.background_music = None
        if self._music_replay_schedule:
            self._music_replay_schedule.cancel()
            self._music_replay_schedule = None
        self._reset_cache()

        return super().on_pre_leave()

    def _finish_quiz(self):
        """Display the finish screen with the final points"""
        if self.background_music:
            self.background_music.stop()
            self.background_music = None
        if self._music_replay_schedule:
            self._music_replay_schedule.cancel()
            self._music_replay_schedule = None

        total_score = sum(question["score"] for question in self.questions_cache)
        total_remaining_time = Clock.get_time() - self.start_time
        self.app.score_manager.save_score(
            self._group_key_store, self._key_store, total_score, total_remaining_time
        )

        self.finish = LayoutFinish(
            app=self.app,
            group_key_store=self._group_key_store,
            key_store=self._key_store,
            destination=self._home_destination,
        )

        self.finish.bind(on_go_home=lambda instance: None)
        self.finish.bind(on_restart_quest=lambda instance: self.restart_quest())
        self.finish.bind(on_exit=lambda instance: self.exit_app())

        self.base_layout.add_widget(self.finish)