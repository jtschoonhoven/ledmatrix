import os
from typing import Any

from ledmatrix import color, font, matrix


class Ticker(matrix.LedMatrix):

    def __init__(
        self,
        *args: Any,
        font_expand_px: int = 0,
        font_shift_down_px: int = 0,
        **kwargs: Any,
    ) -> None:
        self._font_expand_px = font_expand_px
        self._font_shift_down_px = font_shift_down_px
        super().__init__(*args, **kwargs)

    def write_static(self, text: str, value: color.Color = color.RED) -> None:
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

        os.system('clear')
        print(self)  # TODO: change to self.render()

    def write_scroll(self, text: str, value: color.Color = color.RED) -> None:
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
            os.system('clear')
            print(self)


if __name__ == '__main__':
    t = Ticker(num_cols=60, font_expand_px=3, font_shift_down_px=-1)
    while True:
        t.write_scroll('Culdesac Rulez!!!')
