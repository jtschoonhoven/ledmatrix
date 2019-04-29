import time

from ledmatrix import color, matrix


class ColorCycle(matrix.LedMatrix):

    def __init__(self, *args, gradient_multiplier=1, **kwargs):  # type: (*Any, **Any) -> None
        super().__init__(*args, **kwargs)

        # fill with slight gradient
        self.fill(self.default_color)
        for row_index in range(self.height):
            for col_index in range(self.width):
                pixel = self[row_index][col_index]
                for y_offset in range(row_index * gradient_multiplier):
                    pixel = self._next_pixel_value(pixel)
                for x_offset in range(col_index * gradient_multiplier):
                    pixel = self._next_pixel_value(pixel)
                self[row_index][col_index] = pixel

    def next(self):  # type: () -> None
        for row_index in range(self.height):
            for col_index in range(self.width):
                pixel = self[row_index][col_index]
                next_pixel = self._next_pixel_value(pixel)
                self[row_index][col_index] = next_pixel

    @staticmethod
    def _next_pixel_value(pixel):  # type: (color.Color) -> color.Color
        red_value = pixel[0]
        green_value = pixel[1]
        blue_value = pixel[2]

        if red_value == 255:
            green_value = green_value + 1 if green_value <= 255 else 255
            blue_value = blue_value - 1 if blue_value > 0 else 0
        if green_value == 255:
            blue_value = blue_value + 1 if blue_value <= 255 else 255
            red_value = red_value - 1 if red_value > 0 else 0
        if blue_value == 255:
            red_value = red_value + 1 if red_value <= 255 else 255
            green_value = green_value - 1 if green_value > 0 else 0

        next_pixel = color.Color(red_value, green_value, blue_value, None)
        return next_pixel


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--rows', '-r', type=int, default=4)
    parser.add_argument('--cols', '-c', type=int, default=4)
    parser.add_argument('--delay', '-d', type=float, default=0)
    parser.add_argument('--orient', '-o', default='ALTERNATING_COLUMN')
    parser.add_argument('--start', '-s', default='NORTHEAST')
    parser.add_argument('--color', '-co', type=str, default='RED')
    parser.add_argument('--turns', '-t', type=int, default=1024)
    parser.add_argument('--gradient', '-g', type=int, default=1)
    args = parser.parse_args()

    cycler = ColorCycle(
        auto_write=False,
        num_rows=args.rows,
        num_cols=args.cols,
        origin=getattr(matrix.MATRIX_ORIGIN, args.start),
        orientation=getattr(matrix.MATRIX_ORIENTATION, args.orient),
        default_color=getattr(color, args.color),
        gradient_multiplier=args.gradient,
    )

    for cycle_index in range(args.turns):
        cycler.next()
        cycler.render()
        time.sleep(args.delay)

    cycler.deinit()
