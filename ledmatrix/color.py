"""Constants for working with colors in the terminal.

https://pypi.org/project/ansicolors/
"""
from typing import NamedTuple, Optional
from colors import color as ansicolor


ColorOrder = NamedTuple(
    'ColorOrder',
    [('red', int), ('green', int), ('blue', int), ('white', Optional[int])],
)


RGB = ColorOrder(red=0, green=1, blue=2, white=None)
GRB = ColorOrder(green=0, red=1, blue=2, white=None)
RGBW = ColorOrder(red=0, green=1, blue=2, white=3)
GRBW = ColorOrder(green=0, red=1, blue=2, white=3)


_ColorTuple = NamedTuple(
    'Color',
    [('red', int), ('green', int), ('blue', int), ('white', Optional[int])],
)


class Color(_ColorTuple):
    """Container for an RGB color value."""

    def print(self):  # type: () -> str
        """Return an ANSI-formatted, colored code block."""
        # TODO: apply ColorOrder
        return ansicolor('██', fg=(self.red, self.green, self.blue))

    def __str__(self):  # type: () -> str
        """Format class instance as a code-friendly string."""
        return self.print()

    def __repr__(self):  # type: () -> str
        """Format the class instance as a developer-friendly string representation."""
        color_block = ansicolor('██', fg=self)
        return color_block


RED = Color(255, 0, 0, 0)
GREEN = Color(0, 255, 0, 0)
BLUE = Color(0, 0, 255, 0)
WHITE = Color(255, 255, 255, 0)
BLACK = Color(0, 0, 0, 0)
