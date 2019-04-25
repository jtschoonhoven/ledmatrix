"""Constants for working with colors in the terminal.

https://pypi.org/project/ansicolors/
"""
from typing import NamedTuple, Optional
from colors import color as ansicolor


class ColorOrder(NamedTuple):
    red: int = 0
    green: int = 1
    blue: int = 2
    white: Optional[int] = None


RGB = ColorOrder(red=0, green=1, blue=2)
GRB = ColorOrder(green=0, red=1, blue=2)
RGBW = ColorOrder(red=0, green=1, blue=2, white=3)
GRBW = ColorOrder(green=0, red=1, blue=2, white=3)


class Color(NamedTuple):
    """Container for an RGB color value."""
    red: int = 0
    green: int = 0
    blue: int = 0
    white: Optional[int] = None  # no-op

    def print(self) -> str:
        """Return an ANSI-formatted, colored code block."""
        # TODO: apply ColorOrder
        return ansicolor('██', fg=(self.red, self.green, self.blue))

    def __str__(self) -> str:
        """Format class instance as a code-friendly string."""
        return self.print()

    def __repr__(self) -> str:
        """Format the class instance as a developer-friendly string representation."""
        color_block = ansicolor('██', fg=self)
        return color_block
        # return (
        #     'Color(red={}, green={}, blue={}, white={}) RGB[{}] '
        #     .format(self.red, self.green, self.blue, self.white, color_block)
        # )


RED = Color(255, 0, 0)
GREEN = Color(0, 255, 0)
BLUE = Color(0, 0, 255)
WHITE = Color(255, 255, 255)
BLACK = Color(0, 0, 0)
