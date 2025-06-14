from kivy.core.window import Window


class CalculateWindow:
    """Window size calculator based on aspect ratios with support for portrait/landscape presets."""

    # Standard aspect ratio presets
    ASPECT_RATIOS = {"portrait": (9, 16), "landscape": (16, 9)}

    def __init__(
        self,
        window_width: int,
        aspect_ratio: str | float | tuple[float, float] = Window.width / Window.height,
    ):
        # Validate and set aspect ratio
        if isinstance(aspect_ratio, str) and aspect_ratio in self.ASPECT_RATIOS:
            self.aspect_ratio = self.ASPECT_RATIOS[aspect_ratio]
        elif isinstance(aspect_ratio, tuple) and len(aspect_ratio) == 2:
            if all(isinstance(x, (float, int)) and x > 0 for x in aspect_ratio):
                self.aspect_ratio = aspect_ratio
            else:
                raise ValueError(
                    "Both elements of the aspect ratio tuple must be positive numbers."
                )
        elif isinstance(aspect_ratio, (float, int)) and aspect_ratio > 0:
            self.aspect_ratio = aspect_ratio
        else:
            raise ValueError(
                f"Invalid aspect ratio. Choose from: {', '.join(self.ASPECT_RATIOS.keys())} "
                f"or provide a tuple of positive numbers."
            )

        # Store calculated dimensions
        self._window_width = window_width
        self._window_height = self._calculate_height()

    def _calculate_height(self) -> int:
        """Calculate window height based on width and aspect ratio"""
        if isinstance(self.aspect_ratio, (float, int)):
            return int(self._window_width / self.aspect_ratio)

        width_ratio, height_ratio = self.aspect_ratio
        return int(self._window_width * height_ratio / width_ratio)

    def get_size(self):
        return self._window_width, self._window_height

    def get_width(self):
        return self._window_width

    def get_height(self):
        return self._window_height