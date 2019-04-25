import collections
import os
import sys
from typing import List

from ledmatrix import color
from ledmatrix.color import Color, ColorOrder, GRB, GRBW, RGB, RGBW  # noqa: F401
from ledmatrix.stubs.mock_gpio_pin import MockGpioPin


class MockNeoPixel(collections.abc.Sequence):
    """A drop-in replacement for neopixel.NeoPixel with the same API.

    Prints matrix to stdout instead of controlling LEDs on a physical board.
    """

    # all MockNeoPixels share the current state of the matrix via this class attribute
    # NOTE: this makes it impossible to have multiple matrices in the same process with MockNeoPixel
    _pixel_matrix: List[List[Color]] = []

    def __init__(
        self,
        gpio_pin: MockGpioPin,
        pixel_width: int,
        brightness: int = 1,  # no-op
        auto_write: bool = True,
        pixel_order: ColorOrder = RGB,
    ) -> None:
        # set attributes
        self.gpio_pin = gpio_pin
        self.pixel_width = pixel_width
        self.brightness = brightness
        self.auto_write = auto_write
        self.color_order = pixel_order

        # update pixel matrix
        self._row_index = len(self._pixel_matrix)
        self._pixel_row = [color.Color() for pixel in range(pixel_width)]
        self._pixel_matrix.append(self._pixel_row)

    def __len__(self) -> int:
        return self.pixel_width

    def __getitem__(self, index: int) -> Color:
        """Return the RGB value for a given pixel."""
        return self._pixel_row[index]

    def __setitem__(self, index: int, color: Color) -> None:
        """Set the RGB value for a given pixel.

        Prints the entire pixel matrix if auto_write=True.
        """
        if self.color_order in (GRB, GRBW):
            color = self._rgb_to_grb(color)
        self._pixel_row[index] = color
        if self.auto_write:
            self._print_pixel_matrix()

    def fill(self, color: color.Color) -> None:
        """Set the RGB value for all pixels in this row.

        Prints the entire pixel matrix if auto_write=True.
        """
        if self.color_order in (GRB, GRBW):
            color = self._rgb_to_grb(color)
        for pixel_index in range(self.pixel_width):
            self._pixel_matrix[self._row_index][pixel_index] = color
        if self.auto_write:
            self._print_pixel_matrix()

    def show(self) -> None:
        """Prints the entire pixel matrix if auto_write=False."""
        if not self.auto_write:
            self._print_pixel_matrix()

    def deinit(self) -> None:
        """Blank out the NeoPixels and release the pin."""
        color = Color(0, 0, 0, 0)
        for pixel_index in range(self.pixel_width):
            self._pixel_matrix[self._row_index][pixel_index] = color
        self._print_pixel_matrix()

    def _print_pixel_matrix(self) -> str:
        """Print the pixel matrix to stdout."""
        buf: str = ''
        for pixel_row in self._pixel_matrix:
            buf += '\n'
            for pixel in pixel_row:
                buf += pixel.print()
        buf += '\n'
        os.system('clear')  # use os.system('cls') for windows
        sys.stdout.write(buf)

    def _rgb_to_grb(self, color: Color) -> Color:
        """Translate a Color object from RGB to GRB."""
        return Color(red=color.green, green=color.red, blue=color.blue, white=color.white)
