"""Render scrolling text."""
import time
from typing import Any, List, Optional

from ledmatrix import matrix
from ledmatrix.utilities import colors, font
from ledmatrix.utilities.colors import BLACK, Color


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

    def write_static(self, text, value=None):  # type: (str, Optional[Color]) -> None
        """Render static text that does not scroll."""
        text_matrix = self.font.text_to_matrix(text)

        # write text matrix to neopixel
        for row_index in range(self.height):
            for col_index in range(self.width):
                if col_index < len(text_matrix[row_index]):
                    pixel_color = text_matrix[row_index][col_index]
                    self[row_index][col_index] = pixel_color  # type: ignore
        self.render()

    def write_scroll(self, text, color=None):  # type: (str, Optional[Color]) -> None
        """Render text that scrolls right to left."""
        text_matrix = self.font.text_to_matrix(text)
        text_matrix_length = len(text_matrix[0])

        for index in range(self.width + text_matrix_length):
            next_col = []
            for row_index in range(self.height):
                try:
                    pixel_color = text_matrix[row_index][index]
                except IndexError:
                    pixel_color = BLACK
                next_col.append(pixel_color)
            self.shift_left(next_col)
            time.sleep(self._delay_seconds)
            self.render()


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
        default_color=getattr(colors, args.color),
    )
    try:
        ticker.write_scroll(args.text)
    finally:
        ticker.deinit()
