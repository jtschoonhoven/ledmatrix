import collections
from enum import Enum
from typing import List

from ledmatrix import board, color, NeoPixel

DEFAULT_GPIO_PIN_NAME = 'D18'
DEFAULT_NUM_ROWS = 7
DEFAULT_NUM_COLS = 42


class MatrixOrigin(Enum):
    northeast: str = 'NE'
    southeast: str = 'SE'
    southwest: str = 'SW'
    northwest: str = 'NW'


class MatrixOrientation(Enum):
    column: str = 'COL'
    row: str = 'ROW'


class LedMatrix(collections.abc.Sequence):

    def __init__(
        self,
        gpio_pin_name: str = DEFAULT_GPIO_PIN_NAME,
        num_rows: int = DEFAULT_NUM_ROWS,
        num_cols: int = DEFAULT_NUM_COLS,
        brightness: float = 1,
        auto_write: bool = False,
        pixel_order: color.ColorOrder = color.RGB,
        origin: MatrixOrigin = MatrixOrigin.northeast,
        orientation: MatrixOrientation = MatrixOrientation.column,
    ) -> None:
        num_pixels = num_rows * num_cols
        gpio_pin = getattr(board, gpio_pin_name)

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

    def _neopixel_set(
        self,
        matrix_row_index: int,
        matrix_col_index: int,
        value: color.Color,
    ) -> None:
        """Update the NeoPixel pixel at the index corresponding to this position in the matrix."""
        matrix_row = self._matrix[matrix_row_index]
        neopixel_index = (matrix_row_index * len(matrix_row)) + matrix_col_index
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
        self._row = [color.BLACK for _ in range(len)]

    def fill(self, value: color.Color) -> None:
        for pixel_index in range(len(self._row)):
            self[pixel_index] = value

    def __len__(self) -> int:
        return len(self._row)

    def __getitem__(self, index: int) -> color.Color:
        return self._row[index]

    def __setitem__(self, index: int, value: color.Color) -> None:
        self._row[index] = value
        self._parent_matrix._neopixel_set(self._parent_matrix_index, index, value)


if __name__ == '__main__':
    a = LedMatrix(auto_write=False)
    a.render()
    print(a)
    a[0][0] = color.RED
    a.render()
    print(a)
    a.fill(color.GREEN)
    a.render()
    print(a)
