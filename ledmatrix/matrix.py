import collections
import os
import time
from enum import Enum
from typing import List

try:
    import board
    from neopixel import NeoPixel
except (NotImplementedError, ModuleNotFoundError):
    from ledmatrix.stubs.mock_board import MockBoard
    from ledmatrix.stubs.mock_neopixel import MockNeoPixel as NeoPixel
    board = MockBoard()

from ledmatrix import color
from ledmatrix.stubs import mock_neopixel

DEFAULT_GPIO_PIN_NAME = 'D18'
DEFAULT_NUM_ROWS = 7
DEFAULT_NUM_COLS = 42


class MATRIX_ORIGIN(Enum):
    NORTHEAST = 'NE'  # type: str
    NORTHWEST = 'NW'  # type: str


class MATRIX_ORIENTATION(Enum):
    COLUMN = 'COL'  # type: str
    ROW = 'ROW'  # type: str
    ALTERNATING_COLUMN = 'ALT_COL'  # type: str
    ALTERNATING_ROW = 'ALT_ROW'  # type: str


class LedMatrix(collections.abc.Sequence):

    def __init__(
        self,
        gpio_pin_name=DEFAULT_GPIO_PIN_NAME,  # type: str
        num_rows=DEFAULT_NUM_ROWS,  # type: int
        num_cols=DEFAULT_NUM_COLS,  # type: int
        brightness=1,  # type: float
        auto_write=False,  # type: bool
        pixel_order=color.GRB,  # type: color.ColorOrder
        origin=MATRIX_ORIGIN.NORTHEAST,  # type: MATRIX_ORIGIN
        orientation=MATRIX_ORIENTATION.ROW,  # type: MATRIX_ORIENTATION
        default_color=color.RED,  # type: color.Color
    ):  # type: (...) -> None
        num_pixels = num_rows * num_cols
        gpio_pin = getattr(board, gpio_pin_name)
        self.width = num_cols
        self.height = num_rows
        self.origin = origin
        self.orientation = orientation
        self.default_color = default_color
        self.done = False

        # coerce pixel_order to plain tuple
        if pixel_order.white is None:
            pixel_order = (pixel_order.red, pixel_order.green, pixel_order.blue)
        else:
            pixel_order = (pixel_order.red, pixel_order.green, pixel_order.blue, pixel_order.white)

        # initialize underlying NeoPixel
        self._neopixel = NeoPixel(
            gpio_pin,
            num_pixels,
            brightness=brightness,
            auto_write=auto_write,
            pixel_order=pixel_order,
        )

        # initialize each row in matrix
        self._matrix = []  # type: List[List[color.Color]]
        for row_index in range(num_rows):
            self._matrix.append(_LedMatrixRow(self, row_index, num_cols))

    def render(self):  # type: () -> None
        """Render current state of matrix to the neopixel (only useful when auto_write is False)."""
        if isinstance(self._neopixel, mock_neopixel.MockNeoPixel):
            os.system('clear')
            print(self)
        else:
            self._neopixel.show()

    def fill(self, value):  # type: (color.Color) -> None
        for row in self._matrix:
            row.fill(value)

    def shift_left(self, values):  # type: (List[color.Color]) -> None
        for row_index in range(self.height):
            row = self._matrix[row_index]
            value = values[row_index]
            row.shift_left(value)

    def deinit(self):  # type: () -> None
        """Turn off and unmount the neopixel."""
        self._neopixel.deinit()

    def _neopixel_set(
        self,
        matrix_row_index,  # type: int
        matrix_col_index,  # type: int
        value,  # type: color.Color
    ):  # type: (...) -> None
        """Update the NeoPixel pixel at the index corresponding to this position in the matrix.

        TODO: make this less of a clusterfuck.
        """
        # the "neopixel row index" is the index of the first pixel for the specified row
        neopixel_row_index = matrix_row_index * self.width
        if self.origin == MATRIX_ORIGIN.NORTHWEST:
            neopixel_col_index = matrix_col_index * self.height
        else:
            neopixel_col_index = ((self.width - 1) - matrix_col_index) * self.height

        # whether this row / column orientation is swapped
        neopixel_col_alt = neopixel_col_index % 2
        neopixel_row_alt = neopixel_row_index % 2

        # strips are laid horizontal across the board
        if self.orientation == MATRIX_ORIENTATION.ROW:
            # the first pixel is in the top-left corner of the board
            if self.origin == MATRIX_ORIGIN.NORTHWEST:
                neopixel_index = neopixel_row_index + matrix_col_index
            # the first pixel is in the top-right corner of the board
            else:
                neopixel_index = neopixel_row_index + (self.width - matrix_col_index) - 1

        # strips are laid vertically across the board
        elif self.orientation == MATRIX_ORIENTATION.COLUMN:
            # the first pixel is in the top-left corner of the board
            if self.origin == MATRIX_ORIGIN.NORTHWEST:
                neopixel_index = neopixel_col_index + matrix_row_index
            # the first pixel is in the top-right corner of the board
            else:
                neopixel_index = neopixel_col_index + (self.height - matrix_row_index) - 1

        # strips are laid horizontally across the board and alternate left-right orientations
        elif self.orientation == MATRIX_ORIENTATION.ALTERNATING_ROW:
            # the first pixel is in the top-left corner of the board
            if self.origin == MATRIX_ORIGIN.NORTHWEST:
                # this strip is oriented left-to-right
                if not neopixel_row_alt:
                    neopixel_index = neopixel_row_index + matrix_col_index
                # this strip's orientation is switched right-to-left
                else:
                    neopixel_index = (neopixel_row_index - (self.width - 1)) + matrix_col_index
            # the first pixel is in the top-right corner of the board
            else:
                # this strip is oriented right-to-left
                if not neopixel_row_alt:
                    neopixel_index = neopixel_row_index + ((self.width - 1) - matrix_col_index)
                # this strip's orientation is switched left-to-right
                else:
                    neopixel_index = neopixel_row_index + matrix_col_index

        # strips are laid vertically across the board and alternate down-up orientations
        else:
            # the first pixel is in the top-left corner of the board
            if self.origin == MATRIX_ORIGIN.NORTHWEST:
                # this strip is oriented top-to-bottom
                if not neopixel_col_alt:
                    neopixel_index = neopixel_col_index + matrix_row_index
                # this strip's orientation is switched bottom-to-top
                else:
                    neopixel_index = neopixel_col_index + ((self.height - 1) - matrix_row_index)
            # the first pixel is in the top-right corner of the board
            else:
                # this strip is oriented top-to-bottom
                if not neopixel_col_alt:
                    neopixel_index = neopixel_col_index + matrix_row_index
                # this strip's orientation is switched bottom-to-top
                else:
                    neopixel_index = neopixel_col_index + ((self.height - 1) - matrix_row_index)

        # set value on pixel
        if value.white is None:
            self._neopixel[neopixel_index] = (value.red, value.green, value.blue)
        else:
            self._neopixel[neopixel_index] = (value.red, value.green, value.blue, value.white)

        # print if using a mock neopixel and auto_write is True
        if isinstance(self._neopixel, mock_neopixel.MockNeoPixel):
            if self._neopixel.auto_write:
                os.system('clear')
                print(self)

    def __repr__(self):  # type: () -> str
        buf = ''
        for row in self._matrix:
            for pixel in row:
                if isinstance(pixel, color.Color):
                    buf += pixel.print()
                else:
                    pixel = color.Color(pixel)
            buf += '\n'
        return buf

    def __len__(self):  # type: () -> int
        return len(self._neopixel)

    def __getitem__(self, index):  # type: (int) -> color.Color
        return self._matrix[index]

    def __setitem__(self, index, color):  # type: (int, color.Color) -> None
        return self._matrix[index]


class _LedMatrixRow(collections.abc.Sequence):
    def __init__(
        self,
        parent_matrix,  # type: LedMatrix
        parent_matrix_index,  # type: int
        len,  # type: int
    ):  # type: (...) -> None
        self._parent_matrix = parent_matrix
        self._parent_matrix_index = parent_matrix_index
        # TODO: use collections.deque for self._row for efficient left-element removal
        self._row = [color.BLACK for _ in range(len)]

    def fill(self, value):  # type: (color.Color) -> None
        for pixel_index in range(len(self._row)):
            self[pixel_index] = value

    def shift_left(self, value):  # type: (color.Color) -> None
        self._row.pop(0)
        self._row.append(value)
        for pixel_index in range(len(self)):
            pixel_value = self[pixel_index]
            self._parent_matrix._neopixel_set(self._parent_matrix_index, pixel_index, pixel_value)

    def __len__(self):  # type: () -> int
        return len(self._row)

    def __getitem__(self, index):  # type: (int) -> color.Color
        return self._row[index]

    def __setitem__(self, index, value):  # type: (int, color.Color) -> None
        self._row[index] = value
        self._parent_matrix._neopixel_set(self._parent_matrix_index, index, value)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--rows', '-r', type=int, default=4)
    parser.add_argument('--cols', '-c', type=int, default=4)
    parser.add_argument('--delay', '-d', type=float, default=0.2)
    parser.add_argument('--orient', '-o', default='ALTERNATING_COLUMN')
    parser.add_argument('--start', '-s', default='NORTHEAST')
    parser.add_argument('--color', '-co', type=str, default='RED')
    args = parser.parse_args()

    matrix = LedMatrix(
        num_rows=args.rows,
        num_cols=args.cols,
        origin=getattr(MATRIX_ORIGIN, args.start),
        orientation=getattr(MATRIX_ORIENTATION, args.orient),
        default_color=getattr(color, args.color),
    )

    for row_index in range(matrix.height):
        for col_index in range(matrix.width):
            matrix[row_index][col_index] = matrix.default_color
            matrix.render()
            time.sleep(args.delay)

    matrix.deinit()
