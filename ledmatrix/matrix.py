"""Contains LedMatrix base class for working with a single LED strip as a matrix."""
import collections
import os
import time
from enum import Enum
from logging import getLogger
from typing import List, Union

log = getLogger(__name__)

try:
    import board
    from neopixel import NeoPixel
# the NeoPixel library can *only* be installed on a Raspberry Pi:
# fall back to a "mock neopixel" that prints the matrix to STDOUT to allow remote development
except (NotImplementedError, ImportError):
    log.warning('neopixel library not found: matrix will be printed to STDOUT')
    from ledmatrix.stubs.mock_board import MockBoard
    from ledmatrix.stubs.mock_neopixel import MockNeoPixel as NeoPixel
    board = MockBoard()

from ledmatrix.stubs import mock_neopixel  # noqa: E402
from ledmatrix.utilities import colors  # noqa: E402
from ledmatrix.utilities.colors import BLACK, Color, ColorOrder, GRB, RED  # noqa: E402

DEFAULT_GPIO_PIN_NAME = 'D18'
DEFAULT_NUM_ROWS = 7
DEFAULT_NUM_COLS = 42


class MATRIX_ORIGIN(Enum):
    """Configures whether the NeoPixel originates in the top-left or right corner of the matrix."""
    NORTHEAST = 'NE'  # type: str
    NORTHWEST = 'NW'  # type: str


class MATRIX_ORIENTATION(Enum):
    """Configures the path that the NeoPixel travels to form the matrix.

    COLUMN:             pixels travel *down* each column, then continue at the top of the next.
    ROW:                pixels travel *across* each row, then continue at the beginning of the next.
    ALTERNATING COLUMN: pixels travel *down* the first column, then back *up* the next.
    ALTERNATING ROW:    pixels travel *across* the first row, then back across the next row down.
    """
    COLUMN = 'COL'  # type: str
    ROW = 'ROW'  # type: str
    ALTERNATING_COLUMN = 'ALT_COL'  # type: str
    ALTERNATING_ROW = 'ALT_ROW'  # type: str


class LedMatrix(collections.abc.Sequence):
    """Abstraction over the NeoPixel class for working with a NeoPixel strip as a matrix."""

    def __init__(
        self,
        gpio_pin_name=DEFAULT_GPIO_PIN_NAME,  # type: str
        num_rows=DEFAULT_NUM_ROWS,  # type: int
        num_cols=DEFAULT_NUM_COLS,  # type: int
        brightness=1,  # type: float
        auto_write=False,  # type: bool
        pixel_order=GRB,  # type: ColorOrder
        origin=MATRIX_ORIGIN.NORTHEAST,  # type: MATRIX_ORIGIN
        orientation=MATRIX_ORIENTATION.ROW,  # type: MATRIX_ORIENTATION
        default_color=RED,  # type: Color
    ):  # type: (...) -> None
        num_pixels = num_rows * num_cols
        gpio_pin = getattr(board, gpio_pin_name)
        self.width = num_cols
        self.height = num_rows
        self.origin = origin
        self.orientation = orientation
        self.default_color = default_color
        self.pixel_order = pixel_order

        # coerce pixel_order to plain tuple
        if pixel_order.white is None:
            pixel_order = ColorOrder(pixel_order.red, pixel_order.green, pixel_order.blue, None)
        else:
            pixel_order = ColorOrder(pixel_order.red, pixel_order.green, pixel_order.blue, pixel_order.white)

        # initialize underlying NeoPixel
        self._neopixel = NeoPixel(
            gpio_pin,
            num_pixels,
            brightness=brightness,
            auto_write=auto_write,
            pixel_order=pixel_order,
        )

        # initialize each row in matrix
        self._matrix = []  # type: List[_LedMatrixRow]
        for row_index in range(num_rows):
            self._matrix.append(_LedMatrixRow(self, row_index, num_cols))

    def render(self):  # type: () -> None
        """Render current state of matrix to the neopixel (only useful when auto_write is False)."""
        # print to STDOUT if using a mock
        if isinstance(self._neopixel, mock_neopixel.MockNeoPixel):
            os.system('clear')  # noqa: S605 S607
            print(self)
        # otherwise call the "show" method on the underlying neopixel
        else:
            self._neopixel.show()

    def fill(self, value):  # type: (Color) -> None
        """Fill the entire matrix with the given color value."""
        for row in self._matrix:
            row.fill(value)

    def shift_left(self, values):  # type: (List[Color]) -> None
        """Shift all current pixel values left one unit."""
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
        value,  # type: Color
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
                os.system('clear')  # noqa: S605 S607
                print(self)

    def __repr__(self):  # type: () -> str
        buf = ''
        for row in self._matrix:
            for color in row:
                if not isinstance(color, Color):
                    if len(color) == 4:
                        color = Color(*color)
                    else:
                        color = Color(color[0], color[1], color[2], None)
                buf += color.__repr__()
            buf += '\n'
        return buf

    def __len__(self):  # type: () -> int
        return len(self._neopixel)

    def __getitem__(self, index):  # type: (Union[int, slice]) -> Color
        return self._matrix[index]  # type: ignore

    def __setitem__(self, index, color):  # type: (int, Color) -> None
        return self._matrix[index]  # type: ignore


class _LedMatrixRow(collections.abc.Sequence):
    def __init__(
        self,
        parent_matrix,  # type: LedMatrix
        parent_matrix_index,  # type: int
        length,  # type: int
    ):  # type: (...) -> None
        self._parent_matrix = parent_matrix
        self._parent_matrix_index = parent_matrix_index
        # TODO: use collections.deque for self._row for efficient left-element removal
        self._row = [BLACK for _ in range(length)]

    def fill(self, value):  # type: (Color) -> None
        for pixel_index in range(len(self._row)):
            self[pixel_index] = value

    def shift_left(self, value):  # type: (Color) -> None
        self._row.pop(0)
        self._row.append(value)
        for pixel_index in range(len(self)):
            pixel_value = self[pixel_index]
            self._parent_matrix._neopixel_set(self._parent_matrix_index, pixel_index, pixel_value)

    def __len__(self):  # type: () -> int
        return len(self._row)

    def __getitem__(self, index):  # type: (Union[int, slice]) -> Color
        return self._row[index]  # type: ignore

    def __setitem__(self, index, value):  # type: (int, Color) -> None
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
        default_color=getattr(colors, args.color),
    )

    for row_index in range(matrix.height):
        for col_index in range(matrix.width):
            matrix[row_index][col_index] = matrix.default_color  # type: ignore
            matrix.render()
            time.sleep(args.delay)

    matrix.deinit()
