"""Render scrolling text."""
import time
from typing import Any, List

from ledmatrix import color, font, matrix
from ledmatrix.color import Color


class Ticker(matrix.LedMatrix):
    """Render scrolling text."""

    def __init__(
        self,
        *args,  # type: Any
        delay_seconds=0.01,  # type: float
        **kwargs  # type: Any
    ):  # type: (...) -> None
        super().__init__(*args, **kwargs)
        self._delay_seconds = delay_seconds
        self.font = font.Font(font_height_px=self.height)

    def write_static(self, text, value=None):  # type: (str, color.Color) -> None
        """Render static text that does not scroll."""
        text_matrix = self.font.text_to_matrix(text)

        # write text matrix to neopixel
        for row_index in range(self.height):
            for col_index in range(self.width):
                if col_index < len(text_matrix[row_index]):
                    pixel_brightness = text_matrix[row_index][col_index]
                    pixel_color = self._eight_bit_value_to_color(pixel_brightness)
                    self[row_index][col_index] = pixel_color
        self.render()

    def write_scroll(self, text, value=None):  # type: (str, color.Color) -> None
        """Render text that scrolls right to left."""
        text_matrix = self.font.text_to_matrix(text)
        text_matrix_length = len(text_matrix[0])

        for index in range(self.width + text_matrix_length):
            next_col = []
            for row_index in range(self.height):
                try:
                    pixel_brightness = text_matrix[row_index][index]
                    pixel_color = self._eight_bit_value_to_color(pixel_brightness)
                except IndexError:
                    pixel_color = color.BLACK
                next_col.append(pixel_color)
            self.shift_left(next_col)
            time.sleep(self._delay_seconds)
            self.render()

    def _eight_bit_value_to_color(self, value):  # type: (int) -> color.Color
        """Convert an 8-bit grayscale value (0-255) to a Color value object in the default color."""
        rgb_channels = []  # type: List[int]
        for rgb_channel in self.default_color:
            if rgb_channel is None:
                rgb_channels.append(None)
            else:
                channel_value = int(rgb_channel * (value / 255))
                rgb_channels.append(channel_value)
        return Color(*rgb_channels)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--text', '-t', type=str, default='Hello, World!')
    parser.add_argument('--rows', '-r', type=int, default=7)
    parser.add_argument('--cols', '-c', type=int, default=4)
    parser.add_argument('--delay', '-d', type=float, default=0.02)
    parser.add_argument('--orient', '-o', type=str, default='ALTERNATING_COLUMN')
    parser.add_argument('--start', '-s', default='NORTHEAST')
    parser.add_argument('--color', '-co', type=str, default='RED')
    args = parser.parse_args()

    ticker = Ticker(
        origin=getattr(matrix.MATRIX_ORIGIN, args.start),
        orientation=getattr(matrix.MATRIX_ORIENTATION, args.orient),
        num_rows=args.rows,
        num_cols=args.cols,
        delay_seconds=args.delay,
        auto_write=False,
        default_color=getattr(color, args.color),
    )
    try:
        ticker.write_scroll(args.text)
    finally:
        ticker.deinit()
