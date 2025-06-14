from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.modalview import ModalView
from kivy.metrics import dp
from kivymd.uix.floatlayout import MDFloatLayout
from random import choice, shuffle

from game.customs.uix import CustomButton, OutlinedLabel
from game.layouts.default_bg import WithDefaultBG
from game.layouts.pattern_tiles import PatternFactory

class TileButton(Button):
    """Custom button representing a tile in the matching game with position, type and selection states"""

    def __init__(self, tile_id, tile_type, position, layer, z_index=0, **kwargs):
        super(TileButton, self).__init__(**kwargs)
        self.background_normal = f"assets/image/tiles/{tile_type}.png"
        self.background_down = f"assets/image/tiles/{tile_type}.png"
        self.background_color = (1, 1, 1, 1)
        self.tile_id = tile_id
        self.tile_type = tile_type
        self.position = position
        self.layer = layer
        self.z_index = z_index
        self.size_hint = (None, None)
        self.size = (dp(60), dp(60))
        self.pos_hint = {"center_x": position[0], "center_y": position[1]}
        self.selectable = True
        self.covered = False
        self.is_in_stack = False
        self.stack_below = None
        self.ignore_coverage = False

class TilesGameScreen(WithDefaultBG):
    """Main game screen managing tiles matching gameplay, UI interactions and game state logic"""

    def __init__(self, app, **kwargs):
        super(TilesGameScreen, self).__init__(**kwargs)
        self.app = app

        self.layout = MDFloatLayout(
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )

        self.tiles = []
        self.selected_tiles = []
        self.tile_types = list(range(1, 11))    # Set list tiles 1 to 10
        self.max_tiles = 8
        self.total_tiles = 120
        self.current_layer = 1
        self.max_layers = 1
        self.pattern_type = None

        # Initialize UI containers
        self.tiles_container = None
        self.collection_bar_bg = None
        self.collection_container = None
        self.pattern_label = None

        # Game audio assets
        self.select_sound = SoundLoader.load("assets/sounds/select.mp3") if SoundLoader else None
        self.match_sound = SoundLoader.load("assets/sounds/correct.mp3") if SoundLoader else None
        self.game_over_sound = SoundLoader.load("assets/sounds/fail.mp3") if SoundLoader else None
        self.win_sound = SoundLoader.load("assets/sounds/finish.mp3") if SoundLoader else None

        self.setup_ui()
        self.add_widget(self.layout)

    def setup_ui(self):
        background = Image(
            source="assets/image/tiles/bg.png",
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            fit_mode="fill",
        )
        self.layout.add_widget(background)

        back_button = CustomButton(
            app=self.app,
            size_hint=(0.1, 0.1),
            destination="main_menu",
            source="assets/image/buttons/back.png",
            pos_hint={"center_x": 0.1, "center_y": 0.95},
        )
        self.layout.add_widget(back_button)

        self.tiles_container = MDFloatLayout(
            pos_hint={"center_x": 0.5, "center_y": 0.6},
            size_hint=(0.95, 0.75)
        )
        self.layout.add_widget(self.tiles_container)

        self.collection_bar_bg = Image(
            source="assets/image/tiles/bar.png",
            size_hint=(0.9, 0.2),
            pos_hint={"center_x": 0.5, "center_y": 0.15},
        )
        self.layout.add_widget(self.collection_bar_bg)

        self.collection_container = MDFloatLayout(
            pos_hint={"center_x": 0.5, "center_y": 0.15},
            size_hint=(0.9, 0.15)
        )
        self.layout.add_widget(self.collection_container)

        self.pattern_label = OutlinedLabel(
            text="",
            custom_font_size=14,
            font_name="roboto_medium",
            pos_hint={"center_x": 0.9, "center_y": 0.95},
        )
        self.layout.add_widget(self.pattern_label)

    def on_pre_enter(self, *args):
        if not self.app.configs_manager.get("mute"):
            self.app.stop_backsound()

        self.start_new_game()
        return super().on_pre_enter(*args)

    def on_pre_leave(self, *args):
        if not self.app.configs_manager.get("mute"):
            self.app.play_backsound()
        return super().on_pre_leave(*args)

    def start_new_game(self):
        self.tiles_container.clear_widgets()
        self.collection_container.clear_widgets()
        self.tiles = []
        self.selected_tiles = []

        self.pattern_type = PatternFactory.get_random_pattern()
        self.set_pattern_type(self.pattern_type)

        self.generate_balanced_tiles()
        Clock.schedule_once(lambda dt: self.recalculate_tile_visibility(), 0)

    def set_pattern_type(self, pattern_type):
        available_patterns = PatternFactory.get_available_patterns()
        if pattern_type in available_patterns:
            self.pattern_type = pattern_type
        else:
            self.pattern_type = PatternFactory.get_random_pattern()

    def generate_balanced_tiles(self):
        """Generates tiles ensuring each type appears in multiples of 3 for proper matching"""

        self.tiles = []
        self.tiles_container.clear_widgets()

        if self.total_tiles % 3 != 0:
            self.total_tiles += (3 - (self.total_tiles % 3))

        tile_distribution = {}
        tiles_remaining = self.total_tiles

        for tile_type in self.tile_types:
            tile_distribution[tile_type] = 3
            tiles_remaining -= 3

        # Distribute remaining tiles randomly but in multiples of 3
        while tiles_remaining > 0:
            tile_type = choice(self.tile_types)
            tile_distribution[tile_type] += 3
            tiles_remaining -= 3

        all_tiles = []
        tile_id = 0

        for tile_type, count in tile_distribution.items():
            for _ in range(count):
                all_tiles.append({
                    'id': tile_id,
                    'type': tile_type,
                    'layer': 1
                })
                tile_id += 1

        shuffle(all_tiles)

        pattern_generator = PatternFactory.create_pattern_generator(
            self.pattern_type,
            self.tiles_container,
            self.on_tile_press
        )

        self.tiles = pattern_generator.create_pattern(all_tiles)

        self.sort_tiles_by_z_index()

    def sort_tiles_by_z_index(self):
        for tile in self.tiles:
            self.tiles_container.remove_widget(tile)

        self.tiles.sort(key=lambda t: t.z_index)

        for tile in self.tiles:
            self.tiles_container.add_widget(tile)

    def recalculate_tile_visibility(self):
        for tile in self.tiles:
            # Skip stack tiles which should always remain bright
            if not hasattr(tile, 'ignore_coverage') or not tile.ignore_coverage:
                tile.covered = False
                tile.background_color = (1, 1, 1, 1)
                tile.selectable = True
                tile.opacity = 1

        sorted_tiles = sorted(self.tiles, key=lambda t: -t.z_index)

        for i, lower_tile in enumerate(sorted_tiles):
            if hasattr(lower_tile, 'ignore_coverage') and lower_tile.ignore_coverage:
                continue

            # Check all tiles with higher z-index
            for higher_tile in sorted_tiles[:i]:
                if hasattr(higher_tile, 'ignore_coverage') and higher_tile.ignore_coverage:
                    continue

                # Don't check against stack tiles except the top one
                if hasattr(higher_tile, 'is_in_stack') and higher_tile.is_in_stack and higher_tile.opacity == 0:
                    continue

                if self.tiles_overlap(lower_tile, higher_tile):
                    lower_tile.covered = True
                    lower_tile.background_color = (0.6, 0.6, 0.6, 1)        # Gray out covered tiles
                    lower_tile.selectable = False
                    break

    def tiles_overlap(self, tile1, tile2):
        """Checks if two tiles overlap based on their relative positions and dimensions"""
        x1 = tile1.pos_hint["center_x"]
        y1 = tile1.pos_hint["center_y"]
        x2 = tile2.pos_hint["center_x"]
        y2 = tile2.pos_hint["center_y"]

        tile_width_relative = 60 / self.tiles_container.width
        tile_height_relative = 60 / self.tiles_container.height

        half_width = tile_width_relative / 2
        half_height = tile_height_relative / 2

        left1 = x1 - half_width
        right1 = x1 + half_width
        top1 = y1 + half_height
        bottom1 = y1 - half_height

        left2 = x2 - half_width
        right2 = x2 + half_width
        top2 = y2 + half_height
        bottom2 = y2 - half_height

        if right1 < left2 or left1 > right2 or top1 < bottom2 or bottom1 > top2:
            return False

        return True

    @staticmethod
    def is_tile_selectable(tile):
        return not tile.covered and tile.selectable

    def on_tile_press(self, tile):
        """Check if the tile is in the collection bar - ignore clicks on tiles in the bar"""
        if tile in self.selected_tiles:
            return

        if not self.is_tile_selectable(tile):
            return

        if self.select_sound and not self.app.configs_manager.get("mute"):
            self.select_sound.play()

        if len(self.selected_tiles) < self.max_tiles:
            self.tiles_container.remove_widget(tile)
            self.tiles.remove(tile)

            # Unbind the on_press event before adding to selected_tiles
            tile.unbind(on_press=self.on_tile_press)
            self.selected_tiles.append(tile)

            # Handle stack tiles - make tile below visible
            if hasattr(tile, 'is_in_stack') and tile.is_in_stack and hasattr(tile, 'stack_below'):
                next_tile = tile.stack_below
                if next_tile:
                    # Make the next tile in stack visible and selectable
                    next_tile.opacity = 1
                    next_tile.covered = False
                    next_tile.selectable = True

            # Update game state
            self.reorganize_collection_bar()
            self.recalculate_tile_visibility()
            self.check_matches()

            # Check win condition
            if not self.tiles:
                Clock.schedule_once(lambda dt: self.show_game_end(True), 0.5)

            # Check lose condition
            if len(self.selected_tiles) >= self.max_tiles:
                if not self.has_possible_matches():
                    Clock.schedule_once(lambda dt: self.show_game_end(False), 0.5)

    def reorganize_collection_bar(self):
        self.collection_container.clear_widgets()

        sorted_tiles = sorted(self.selected_tiles, key=lambda t: t.tile_type)

        collection_width = 0.86
        slot_width = collection_width / self.max_tiles

        for i, tile in enumerate(sorted_tiles):
            collection_x = 0.07 + (slot_width * i) + (slot_width / 2)
            tile.pos_hint = {"center_x": collection_x, "center_y": 0.5}
            self.collection_container.add_widget(tile)

        self.selected_tiles = sorted_tiles

    def check_matches(self):
        """Recursively checks and removes groups of 3+ matching tiles from collection bar"""
        tile_groups = {}
        for tile_item in self.selected_tiles:
            if tile_item.tile_type not in tile_groups:
                tile_groups[tile_item.tile_type] = []
            tile_groups[tile_item.tile_type].append(tile_item)

        # Remove first group of 3 matching tiles found
        match_found = False
        for tile_type, tiles in tile_groups.items():
            if len(tiles) >= 3:
                if self.match_sound and not self.app.configs_manager.get("mute"):
                    self.match_sound.play()

                for _ in range(3):
                    matched_tile = tiles.pop()
                    self.collection_container.remove_widget(matched_tile)
                    self.selected_tiles.remove(matched_tile)

                self.reorganize_collection_bar()
                match_found = True
                break

        if match_found:
            Clock.schedule_once(lambda dt: self.check_matches(), 0.3)

    def has_possible_matches(self):
        tile_counts = {}
        for tile in self.selected_tiles:
            if tile.tile_type not in tile_counts:
                tile_counts[tile.tile_type] = 0
            tile_counts[tile.tile_type] += 1

        return any(count >= 3 for count in tile_counts.values())

    def show_game_end(self, is_win):
        if is_win:
            if self.win_sound and not self.app.configs_manager.get("mute"):
                self.win_sound.play()
            bg_image = "assets/image/tiles/finish_win.png"
        else:
            if self.game_over_sound and not self.app.configs_manager.get("mute"):
                self.game_over_sound.play()
            bg_image = "assets/image/tiles/finish_lose.png"

        popup = ModalView(size_hint=(0.8, 0.5), auto_dismiss=False, background_color=[0, 0, 0, 0])
        content = MDFloatLayout()

        bg = Image(
            source=bg_image,
            size_hint=(1, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        content.add_widget(bg)

        message_text = "Yeahhh, bạn đã thắng rồi!" if is_win else "Chúc bạn may mắn lần sau!"
        message = OutlinedLabel(
            text=message_text,
            custom_font_size=16,
            font_name="roboto_medium",
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        content.add_widget(message)

        replay_button = CustomButton(
            app=self.app,
            source="assets/image/quiz/finish/replay.png",
            size_hint=(0.3, 0.15),
            pos_hint={"center_x": 0.35, "center_y": 0.3},
        )
        replay_button.bind(on_press=lambda x: self.restart_game(popup))
        content.add_widget(replay_button)

        main_menu_button = CustomButton(
            app=self.app,
            source="assets/image/quiz/finish/main_menu.png",
            size_hint=(0.3, 0.15),
            pos_hint={"center_x": 0.65, "center_y": 0.3},
        )
        main_menu_button.bind(on_press=lambda x: self.go_to_main_menu(popup))
        content.add_widget(main_menu_button)

        popup.add_widget(content)
        popup.open()

    def restart_game(self, popup):
        popup.dismiss()
        Clock.schedule_once(lambda dt: self.start_new_game(), 0.3)

    def go_to_main_menu(self, popup):
        popup.dismiss()
        Clock.schedule_once(lambda dt: self.app.switch_screen("main_menu"), 0.3)