import math
from random import randint, choice
from abc import ABC, abstractmethod

class PatternGenerator(ABC):
    """Abstract base class for generating tile patterns in games"""

    def __init__(self, tiles_container, on_tile_press_callback):
        self.tiles_container = tiles_container
        self.on_tile_press_callback = on_tile_press_callback
        self.tiles = []

    @abstractmethod
    def create_pattern(self, all_tiles):
        pass

    def get_tiles(self):
        return self.tiles

    def add_tile(self, tile):
        self.tiles_container.add_widget(tile)
        self.tiles.append(tile)

    def _create_tile(self, tile_data, tile_position, z_index):
        from game.screen.tiles_game_screen import TileButton

        tile = TileButton(
            tile_id=tile_data['id'],
            tile_type=tile_data['type'],
            position=(tile_position["x"], tile_position["y"]),
            layer=1,
            z_index=z_index
        )
        tile.bind(on_press=lambda btn: self.on_tile_press_callback(btn))

        return tile

    def _create_surrounding_tiles(self, remaining_tiles, radius=0.45, z_index_base=2000):
        center_x, center_y = 0.5, 0.5

        for i, tile_data in enumerate(remaining_tiles):
            angle = 2 * math.pi * i / len(remaining_tiles)

            r = radius + (0.05 if i % 2 == 0 else 0)

            x = center_x + r * math.cos(angle)
            y = center_y + r * math.sin(angle)

            x += randint(-5, 5) / 200
            y += randint(-5, 5) / 200

            z_index = z_index_base + i

            tile = self._create_tile(tile_data, {"x": x, "y": y}, z_index)
            self.add_tile(tile)

    @staticmethod
    def _add_jitter(point, amount=3):
        return {
            "x": point["x"] + randint(-amount, amount) / 100,
            "y": point["y"] + randint(-amount, amount) / 100,
            "z": point["z"]
        }

    def _create_stacked_tiles(self, tiles, position, z_index_base=3000):
        if not tiles:
            return

        if isinstance(position, tuple):
            position = {"x": position[0], "y": position[1]}

        stack_tiles = []

        for i, tile_data in enumerate(tiles):
            z_index = z_index_base + (len(tiles) - i - 1)

            tile = self._create_tile(tile_data, position, z_index)

            tile.is_in_stack = True         # Mark stack tiles
            tile.ignore_coverage = True     # Stack tiles are always bright and selectable

            stack_tiles.append(tile)        # Store the tiles in our local list

        # Link stack tiles together
        for i in range(len(stack_tiles) - 1):
            stack_tiles[i].stack_below = stack_tiles[i + 1]

        # Set visibility and selectability
        for i, tile in enumerate(stack_tiles):
            if i > 0:
                tile.covered = True
                tile.selectable = False
                tile.opacity = 0    # Hide tiles below the top one

            self.add_tile(tile)     # Add tiles to the container


class HeartPatternGenerator(PatternGenerator):
    """Generates tiles arranged in a heart shape pattern"""

    def create_pattern(self, all_tiles):
        heart_coordinates = self._generate_heart_coordinates()

        heart_coordinates.sort(key=lambda coord: coord["z"])

        if len(all_tiles) > 20:
            main_tiles = all_tiles[:len(all_tiles) - 20]
            stack_tiles = all_tiles[len(all_tiles) - 20:]
            left_stack = stack_tiles[:10]
            right_stack = stack_tiles[10:20]
        else:
            main_tiles = all_tiles[:max(len(all_tiles) - 4, len(heart_coordinates))]
            left_stack = all_tiles[len(main_tiles):len(main_tiles) + min(2, len(all_tiles) - len(main_tiles))]
            right_stack = all_tiles[len(main_tiles) + len(left_stack):]

        pattern_tiles_count = min(len(main_tiles), len(heart_coordinates))

        for i in range(pattern_tiles_count):
            if i >= len(main_tiles):
                break

            tile_data = main_tiles[i]
            pos_coord = heart_coordinates[i]

            z_index = int(pos_coord["z"] * 1000) + i

            tile = self._create_tile(tile_data, pos_coord, z_index)
            self.add_tile(tile)

        if len(main_tiles) > pattern_tiles_count:
            remaining_tiles = main_tiles[pattern_tiles_count:]
            self._create_surrounding_tiles(remaining_tiles)

        if left_stack:
            self._create_stacked_tiles(left_stack, (0.1, 0.2), z_index_base=5000)

        if right_stack:
            self._create_stacked_tiles(right_stack, (0.9, 0.2), z_index_base=5000)

        return self.tiles

    @staticmethod
    def _generate_heart_coordinates():
        heart_coordinates = []

        heart_points = [
            (0.35, 0.65), (0.30, 0.70), (0.25, 0.70),
            (0.20, 0.65), (0.20, 0.60), (0.25, 0.55),
            (0.65, 0.65), (0.70, 0.70), (0.75, 0.70),
            (0.80, 0.65), (0.80, 0.60), (0.75, 0.55),
            (0.50, 0.25),
            (0.30, 0.45), (0.40, 0.35),
            (0.70, 0.45), (0.60, 0.35),
            (0.40, 0.55), (0.50, 0.55), (0.60, 0.55),
            (0.35, 0.50), (0.45, 0.50), (0.55, 0.50), (0.65, 0.50),
            (0.40, 0.45), (0.50, 0.45), (0.60, 0.45),
            (0.45, 0.40), (0.55, 0.40),
            (0.50, 0.35),
            (0.30, 0.55), (0.70, 0.55),
            (0.30, 0.50), (0.70, 0.50),
            (0.35, 0.45), (0.65, 0.45),
            (0.40, 0.40), (0.60, 0.40),
            (0.45, 0.35), (0.55, 0.35),
            (0.45, 0.30), (0.55, 0.30),
        ]

        for offset in [0, 0.02, 0.04]:
            for point in heart_points:
                heart_coordinates.append({
                    "x": point[0] + randint(-3, 3) / 100,
                    "y": point[1] + randint(-3, 3) / 100,
                    "z": offset
                })

        return heart_coordinates

class SquarePatternGenerator(PatternGenerator):
    """Generates tiles arranged in a square/rectangular pattern"""

    def create_pattern(self, all_tiles):
        square_coordinates = self._generate_square_coordinates()

        square_coordinates.sort(key=lambda coord: coord["z"])

        if len(all_tiles) > 20:
            main_tiles = all_tiles[:len(all_tiles) - 20]
            stack_tiles = all_tiles[len(all_tiles) - 20:]
            left_stack = stack_tiles[:10]
            right_stack = stack_tiles[10:20]
        else:
            main_tiles = all_tiles[:max(len(all_tiles) - 4, len(square_coordinates))]
            left_stack = all_tiles[len(main_tiles):len(main_tiles) + min(2, len(all_tiles) - len(main_tiles))]
            right_stack = all_tiles[len(main_tiles) + len(left_stack):]

        pattern_tiles_count = min(len(main_tiles), len(square_coordinates))

        for i in range(pattern_tiles_count):
            if i >= len(main_tiles):
                break

            tile_data = main_tiles[i]
            pos_coord = square_coordinates[i]

            z_index = int(pos_coord["z"] * 1000) + i

            tile = self._create_tile(tile_data, pos_coord, z_index)
            self.add_tile(tile)

        if len(main_tiles) > pattern_tiles_count:
            remaining_tiles = main_tiles[pattern_tiles_count:]
            self._create_surrounding_tiles(remaining_tiles, radius=0.48)

        if left_stack:
            self._create_stacked_tiles(left_stack, (0.3, 0.09), z_index_base=5000)

        if right_stack:
            self._create_stacked_tiles(right_stack, (0.7, 0.09), z_index_base=5000)

        return self.tiles

    @staticmethod
    def _generate_square_coordinates():
        square_coordinates = []

        width = 0.25
        height = 0.2
        center_x, center_y = 0.5, 0.5

        square_points = []

        top_y = center_y + height
        for x_pct in range(0, 11):
            x = center_x - width + (width * 2 * x_pct / 10)
            square_points.append((x, top_y))

        bottom_y = center_y - height
        for x_pct in range(0, 11):
            x = center_x - width + (width * 2 * x_pct / 10)
            square_points.append((x, bottom_y))

        left_x = center_x - width
        for y_pct in range(1, 10):
            y = center_y - height + (height * 2 * y_pct / 10)
            square_points.append((left_x, y))

        right_x = center_x + width
        for y_pct in range(1, 10):
            y = center_y - height + (height * 2 * y_pct / 10)
            square_points.append((right_x, y))

        grid_rows = 3
        grid_cols = 5

        for i in range(1, grid_cols):
            for j in range(1, grid_rows):
                x = center_x - width + (width * 2 * i / grid_cols)
                y = center_y - height + (height * 2 * j / grid_rows)
                square_points.append((x, y))

        jitter_levels = [3, 2, 1]
        for offset, jitter in zip([0, 0.02, 0.04], jitter_levels):
            for point in square_points:
                square_coordinates.append({
                    "x": point[0] + randint(-jitter, jitter) / 100,
                    "y": point[1] + randint(-jitter, jitter) / 100,
                    "z": offset
                })

        return square_coordinates

class PatternFactory:
    """Factory class for creating and managing pattern generators"""

    PATTERNS = {
        "heart": HeartPatternGenerator,
        "square": SquarePatternGenerator
    }

    @staticmethod
    def create_pattern_generator(pattern_type, tiles_container, on_tile_press_callback):
        if pattern_type in PatternFactory.PATTERNS:
            return PatternFactory.PATTERNS[pattern_type](tiles_container, on_tile_press_callback)
        else:
            random_pattern = choice(list(PatternFactory.PATTERNS.keys()))
            return PatternFactory.PATTERNS[random_pattern](tiles_container, on_tile_press_callback)

    @staticmethod
    def get_random_pattern():
        return choice(list(PatternFactory.PATTERNS.keys()))

    @staticmethod
    def get_available_patterns():
        return list(PatternFactory.PATTERNS.keys())