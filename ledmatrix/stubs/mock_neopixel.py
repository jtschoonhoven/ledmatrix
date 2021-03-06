"""Drop-in replacement for the Adafruit neopixel library: prints matrix to STDOUT."""
import collections
import os
from typing import Union

from ledmatrix.stubs.mock_gpio_pin import MockGpioPin
from ledmatrix.utilities.colors import BLACK, Color, ColorOrder, GRB, GRBW, RGB


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
        self._pixels = [BLACK for pixel in range(pixel_width)]

    def __repr__(self):  # type: () -> str
        buf = ''
        for pixel in self._pixels:
            if len(pixel) == 3:
                buf += Color(*pixel, 0).__repr__()  # type: ignore
            else:
                buf += Color(*pixel).__repr__()
        buf += '\n'
        return buf

    def __len__(self):  # type: () -> int
        return len(self._pixels)

    def __getitem__(self, index):  # type: (Union[int, slice]) -> Color
        """Return the RGB value for a given pixel."""
        return self._pixels[index]  # type: ignore

    def __setitem__(self, index, color):  # type: (int, Color) -> None
        """Set the RGB value for a given pixel."""
        if self.color_order in (GRB, GRBW):
            color = self._rgb_to_grb(color)
        self._pixels[index] = color

    def fill(self, color):  # type: (Color) -> None
        """Set the RGB value for all pixels in this row.

        Prints the entire pixel matrix if auto_write=True.
        """
        if self.color_order in (GRB, GRBW):
            color = self._rgb_to_grb(color)
        for pixel_index, _ in enumerate(self._pixels):
            self._pixels[pixel_index] = color
        if self.auto_write:
            print(self)

    def show(self):  # type: () -> None
        """Print the entire pixel matrix if auto_write=False."""
        if not self.auto_write:
            os.system('clear')  # noqa: S605 S607
            print(self)

    def deinit(self):  # type: () -> None
        """Blank out the NeoPixels and release the pin."""
        for pixel_index in range(len(self)):
            self[pixel_index] = BLACK

    def _rgb_to_grb(self, color):  # type: (Color) -> Color
        """Translate a Color object from RGB to GRB."""
        if len(color) == 3:
            color = Color(color[0], color[1], color[2], None)
        else:
            color = Color(*color)
        return Color(red=color.green, green=color.red, blue=color.blue, white=color.white)
