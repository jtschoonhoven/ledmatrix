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

    def __bool__(self):  # type: () -> bool
        """Return False only for black."""
        return any(self)

    def __str__(self):  # type: () -> str
        """Format class instance as a code-friendly string."""
        return self.__repr__()

    def __repr__(self):  # type: () -> str
        """Format the class instance as a developer-friendly string representation."""
        # TODO: apply color order
        return ansicolor('██', fg=(self.red, self.green, self.blue))  # type: ignore


BLACK = Color(0, 0, 0, None)
RED = Color(255, 0, 0, None)
GREEN = Color(0, 255, 0, None)
BLUE = Color(0, 0, 255, None)
YELLOW = Color(255, 255, 0, None)
TEAL = Color(0, 255, 255, None)
PINK = Color(255, 0, 255, None)
WHITE = Color(255, 255, 255, None)
