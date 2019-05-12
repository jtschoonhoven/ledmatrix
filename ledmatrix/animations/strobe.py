"""Rapidly flash all pixels in the matrix between different colors/brightness."""
import random
import time
from typing import Any

from ledmatrix import matrix
from ledmatrix.utilities.colors import Color


class Strobe(matrix.LedMatrix):
    """Rapidly flash all pixels in the matrix between different colors/brightness."""
    def __init__(self, *args, **kwargs):  # type: (*Any, **Any) -> None
        return super().__init__(*args, **kwargs)

    def next_state(self):  # type: () -> None
        """Update the matrix state to be filled with a new random color value."""
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)

        # set white channel if used
        w = None
        if self.pixel_order.white is not None:
            w = random.randint(0, 255)

        # fill matrix with new color
        color = Color(r, g, b, w)
        self.fill(color)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--rows', '-r', type=int, default=7)
    parser.add_argument('--cols', '-c', type=int, default=10)
    parser.add_argument('--delay', '-d', type=float, default=0.001)
    parser.add_argument('--turns', '-t', type=int, default=400)
    parser.add_argument('--orient', '-o', default='ALTERNATING_COLUMN')
    parser.add_argument('--start', '-s', default='NORTHEAST')
    args = parser.parse_args()

    strobe = Strobe(
        auto_write=False,
        num_rows=args.rows,
        num_cols=args.cols,
        origin=getattr(matrix.MATRIX_ORIGIN, args.start),
        orientation=getattr(matrix.MATRIX_ORIENTATION, args.orient),
    )

    try:
        for _ in range(args.turns):
            strobe.next_state()
            strobe.render()
            time.sleep(args.delay)
    finally:
        strobe.deinit()
