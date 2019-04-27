import collections
import os

from ledmatrix import color
from ledmatrix.color import Color, ColorOrder, GRB, GRBW, RGB, RGBW  # noqa: F401
from ledmatrix.stubs.mock_gpio_pin import MockGpioPin


class MockNeoPixel(collections.abc.Sequence):
    """A drop-in replacement for neopixel.NeoPixel with the same API.

    Prints matrix to stdout instead of controlling LEDs on a physical board.
    """

    def __init__(
        self,
        gpio_pin,
        pixel_width,
        brightness=1,  # no-op
        auto_write=True,
        pixel_order=RGB,
    ):  # type: (MockGpioPin, int, int, bool, ColorOrder) -> None
        # set attributes
        self.brightness = brightness
        self.auto_write = auto_write
        self.color_order = pixel_order

        # initialize pixels
        self._pixels = [color.BLACK for pixel in range(pixel_width)]

    def __repr__(self):  # type: () -> str
        buf = ''
        for pixel in self._pixels:
            if len(pixel) == 3:
                buf += color.Color(*pixel, 0).print()
            else:
                buf += color.Color(*pixel).print()
        buf += '\n'
        return buf

    def __len__(self):  # type: () -> int
        return len(self._pixels)

    def __getitem__(self, index):  # type: (int) -> Color
        """Return the RGB value for a given pixel."""
        return self._pixels[index]

    def __setitem__(self, index, color):  # type: (int, Color) -> None
        """Set the RGB value for a given pixel.

        Prints the entire pixel matrix if auto_write=True.
        """
        if self.color_order in (GRB, GRBW):
            color = self._rgb_to_grb(color)
        self._pixels[index] = color
        if self.auto_write:
            print(self)

    def fill(self, value):  # type: (Color) -> None
        """Set the RGB value for all pixels in this row.

        Prints the entire pixel matrix if auto_write=True.
        """
        if self.color_order in (GRB, GRBW):
            value = self._rgb_to_grb(color)
        for pixel_index, pixel in self._pixels:
            self._pixels[pixel_index] = value
        if self.auto_write:
            print(self)

    def show(self):  # type: () -> None
        """Prints the entire pixel matrix if auto_write=False."""
        if not self.auto_write:
            os.system('clear')
            print(self)

    def deinit(self):  # type: () -> None
        """Blank out the NeoPixels and release the pin."""
        color = Color(0, 0, 0, 0)
        for pixel_index in range(self.pixel_width):
            self._pixel_matrix[self._row_index][pixel_index] = color
        self._print_pixel_matrix()

    def _rgb_to_grb(self, color: Color):  # type: (Color) -> Color
        """Translate a Color object from RGB to GRB."""
        return Color(red=color.green, green=color.red, blue=color.blue, white=color.white)
