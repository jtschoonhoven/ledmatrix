import collections
import os
from enum import Enum
from typing import List

from ledmatrix import board, color, NeoPixel

DEFAULT_GPIO_PIN_NAME = 'D18'
DEFAULT_NUM_ROWS = 7
DEFAULT_NUM_COLS = 42


class MATRIX_ORIGIN(Enum):
    NORTHEAST: str = 'NE'
    NORTHWEST: str = 'NW'


class MATRIX_ORIENTATION(Enum):
    COLUMN: str = 'COL'
    ROW: str = 'ROW'


class LedMatrix(collections.abc.Sequence):

    def __init__(
        self,
        gpio_pin_name: str = DEFAULT_GPIO_PIN_NAME,
        num_rows: int = DEFAULT_NUM_ROWS,
        num_cols: int = DEFAULT_NUM_COLS,
        brightness: float = 1,
        auto_write: bool = False,
        pixel_order: color.ColorOrder = color.RGB,
        origin: MATRIX_ORIGIN = MATRIX_ORIGIN.NORTHEAST,
        orientation: MATRIX_ORIENTATION = MATRIX_ORIENTATION.ROW,
    ) -> None:
        num_pixels = num_rows * num_cols
        gpio_pin = getattr(board, gpio_pin_name)
        self.width = num_cols
        self.height = num_rows
        self.origin = origin
        self.orientation = orientation

        # initialize underlying NeoPixel
        self._neopixel = NeoPixel(
            gpio_pin,
            num_pixels,
            brightness=brightness,
            auto_write=auto_write,
            pixel_order=pixel_order,
        )

        # initialize each row in matrix
        self._matrix: List[List[color.Color]] = []
        for row_index in range(num_rows):
            self._matrix.append(_LedMatrixRow(self, row_index, num_cols))

    def render(self) -> None:
        """Render current state of matrix to the neopixel (only useful when auto_write is False)."""
        self._neopixel.show()

    def fill(self, value: color.Color) -> None:
        for row in self._matrix:
            row.fill(value)

    def shift_left(self, values: List[color.Color]) -> None:
        for row_index in range(self.height):
            row = self._matrix[row_index]
            value = values[row_index]
            row.shift_left(value)

    def _neopixel_set(
        self,
        matrix_row_index: int,
        matrix_col_index: int,
        value: color.Color,
    ) -> None:
        """Update the NeoPixel pixel at the index corresponding to this position in the matrix."""
        neopixel_row_index = matrix_row_index * self.width
        neopixel_col_index = matrix_col_index * self.height

        if self.orientation == MATRIX_ORIENTATION.ROW:
            if self.origin == MATRIX_ORIGIN.NORTHWEST:
                neopixel_index = neopixel_row_index + matrix_col_index
            else:  # self.origin == MATRIX_ORIGIN.NORTHEAST
                neopixel_index = neopixel_row_index + (self.width - matrix_col_index - 1)

        else:  # self.orientation == MATRIX_ORIENTATION.COLUMN
            if self.origin == MATRIX_ORIGIN.NORTHWEST:
                neopixel_index = neopixel_col_index + matrix_row_index
            else:  # self.origin == MATRIX_ORIGIN.NORTHEAST
                neopixel_index = neopixel_col_index + (self.height - matrix_row_index - 1)

        self._neopixel[neopixel_index] = value

    def __repr__(self) -> str:
        buf = ''
        for row in self._matrix:
            for pixel in row:
                buf += pixel.print()
            buf += '\n'
        return buf

    def __len__(self) -> int:
        return len(self._neopixel)

    def __getitem__(self, index: int) -> color.Color:
        return self._matrix[index]

    def __setitem__(self, index: int, color: color.Color) -> None:
        return self._matrix[index]


class _LedMatrixRow(collections.abc.Sequence):
    def __init__(
        self,
        parent_matrix: LedMatrix,
        parent_matrix_index: int,
        len: int,
    ) -> None:
        self._parent_matrix = parent_matrix
        self._parent_matrix_index = parent_matrix_index
        # TODO: use collections.deque for self._row for efficient left-element removal
        self._row = [color.BLACK for _ in range(len)]

    def fill(self, value: color.Color) -> None:
        for pixel_index in range(len(self._row)):
            self[pixel_index] = value

    def shift_left(self, value: color.Color) -> None:
        self._row.pop(0)
        self._row.append(value)
        for pixel_index in range(len(self)):
            pixel_value = self[pixel_index]
            self._parent_matrix._neopixel_set(self._parent_matrix_index, pixel_index, pixel_value)

    def __len__(self) -> int:
        return len(self._row)

    def __getitem__(self, index: int) -> color.Color:
        return self._row[index]

    def __setitem__(self, index: int, value: color.Color) -> None:
        self._row[index] = value
        self._parent_matrix._neopixel_set(self._parent_matrix_index, index, value)


if __name__ == '__main__':
    a = LedMatrix(auto_write=False, num_cols=40)
    for _ in range(20):
        a.fill(color.RED)
        os.system('clear')
        # print(a)
        a.render()
        a.fill(color.GREEN)
        os.system('clear')
        # print(a)
        a.render()
        a.fill(color.BLUE)
        os.system('clear')
        # print(a)
        a.render()
