import collections
from enum import Enum
from typing import List

from ledmatrix import board, color, NeoPixel

DEFAULT_GPIO_PIN_NAME = 'D18'
DEFAULT_NUM_ROWS = 7
DEFAULT_NUM_COLS = 42


class ArrayOrigin(Enum):
    northeast: str = 'NE'
    southeast: str = 'SE'
    southwest: str = 'SW'
    northwest: str = 'NW'


class ArrayOrientation(Enum):
    column: str = 'COL'
    row: str = 'ROW'


class LedArray(collections.abc.Sequence):

    def __init__(
        self,
        gpio_pin_name: str = DEFAULT_GPIO_PIN_NAME,
        num_rows: int = DEFAULT_NUM_ROWS,
        num_cols: int = DEFAULT_NUM_COLS,
        brightness: float = 1,
        auto_write: bool = False,
        pixel_order: color.ColorOrder = color.RGB,
        origin: ArrayOrigin = ArrayOrigin.northeast,
        orientation: ArrayOrientation = ArrayOrientation.column,
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

        # initialize each row in array
        self._array: List[List[color.Color]] = []
        for row_index in range(num_rows):
            self._array.append(_LedArrayRow(self, row_index, num_cols))

    def render(self) -> None:
        """Render current state of matrix to the neopixel (only useful when auto_write is False)."""
        self._neopixel.show()

    def fill(self, value: color.Color) -> None:
        for row in self._array:
            row.fill(value)

    def _neopixel_set(self, array_row_index: int, array_col_index: int, value: color.Color) -> None:
        """Update the NeoPixel pixel at the index corresponding to this position in the matrix."""
        array_row = self._array[array_row_index]
        neopixel_index = (array_row_index * len(array_row)) + array_col_index
        self._neopixel[neopixel_index] = value

    def __repr__(self) -> str:
        buf = ''
        for row in self._array:
            for pixel in row:
                buf += pixel.print()
            buf += '\n'
        return buf

    def __len__(self) -> int:
        return len(self._neopixel)

    def __getitem__(self, index: int) -> color.Color:
        return self._array[index]

    def __setitem__(self, index: int, color: color.Color) -> None:
        return self._array[index]


class _LedArrayRow(collections.abc.Sequence):

    def __init__(
        self,
        parent_array: LedArray,
        parent_array_index: int,
        len: int,
    ) -> None:
        self._parent_array = parent_array
        self._parent_array_index = parent_array_index
        self._row = [color.BLACK for _ in range(len)]

    def fill(self, value: color.Color) -> None:
        for pixel_index in range(len(self._row)):
            self[pixel_index] = value

    def __len__(self) -> int:
        return len(self._row)

    def __getitem__(self, index: int) -> color.Color:
        return self._row[index]

    def __setitem__(self, index: int, value: color.Color) -> None:
        self._row[index] = value  # update internal matrix
        self._parent_array._neopixel_set(self._parent_array_index, index, value)  # update neopixel


if __name__ == '__main__':
    a = LedArray(auto_write=False)
    a.render()
    print(a)
    a[0][0] = color.RED
    a.render()
    print(a)
    a.fill(color.GREEN)
    a.render()
    print(a)
