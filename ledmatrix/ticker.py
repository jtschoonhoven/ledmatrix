import os
import time
from typing import Any

from ledmatrix import color, font, matrix


class Ticker(matrix.LedMatrix):

    def __init__(
        self,
        *args,  # type: Any
        font_expand_px=0,  # type: int
        font_shift_down_px=0,  # type: int
        delay_seconds=0.01,  # type: float
        **kwargs,  # type: Any
    ):  # type: (...) -> None
        self._font_expand_px = font_expand_px
        self._font_shift_down_px = font_shift_down_px
        self._delay_seconds = delay_seconds
        super().__init__(*args, **kwargs)

    def write_static(self, text, value=color.RED):  # type: (str, color.Color) -> None
        text_matrix = font.text_to_matrix(
            text,
            font_height_px=self.height,
            font_expand_px=self._font_expand_px,
            font_shift_down_px=self._font_shift_down_px,
        )

        # write text matrix to neopixel
        for row_index in range(self.height):
            for col_index in range(self.width):
                if col_index < len(text_matrix[row_index]):
                    pixel_on = text_matrix[row_index][col_index]
                    if pixel_on:
                        self[row_index][col_index] = value
                    else:
                        self[row_index][col_index] = color.BLACK

        os.system('clear')  # TODO: rm
        print(self)  # TODO: change to self.render()

    def write_scroll(self, text, value=color.RED):  # type: (str, color.Color) -> None
        text_matrix = font.text_to_matrix(
            text,
            font_height_px=self.height,
            font_expand_px=self._font_expand_px,
            font_shift_down_px=self._font_shift_down_px,
        )
        text_matrix_length = len(text_matrix[0])

        for index in range(self.width + text_matrix_length):
            next_col = []
            for row_index in range(self.height):
                try:
                    pixel_on = text_matrix[row_index][index]
                except IndexError:
                    pixel_on = False
                if pixel_on:
                    next_col.append(value)
                else:
                    next_col.append(color.BLACK)
            self.shift_left(next_col)
            time.sleep(self._delay_seconds)
            os.system('clear')  # TODO: rm
            print(self)  # TODO: change to self.render()


if __name__ == '__main__':
    t = Ticker(
        origin=matrix.MATRIX_ORIGIN.NORTHEAST,
        orientation=matrix.MATRIX_ORIENTATION.COLUMN,
        num_rows=7,
        num_cols=40,
        font_expand_px=3,
        font_shift_down_px=-1,
        delay_seconds=0.02,
        auto_write=False,
    )
    for _ in range(2):
        t.write_scroll('Culdesac Rulez!!!')
