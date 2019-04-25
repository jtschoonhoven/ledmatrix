from typing import List

try:
    import board
    from neopixel import NeoPixel
except (NotImplementedError, ModuleNotFoundError):
    from ledmatrix.stubs.mock_board import MockBoard
    from ledmatrix.stubs.mock_neopixel import MockNeoPixel as NeoPixel
    board = MockBoard()

from ledmatrix import color
from ledmatrix import font

DEFAULT_DISPLAY_HEIGHT_PX = 7
DEFAULT_DISPLAY_WIDTH_PX = 42
DEFAULT_GPIO_PIN_INDICES = (18, 23, 24, 25, 8, 7, 12)


def run(
    gpio_pins=DEFAULT_GPIO_PIN_INDICES,
    pixel_width=DEFAULT_DISPLAY_WIDTH_PX,
    pixel_height=DEFAULT_DISPLAY_HEIGHT_PX,
) -> None:
    if pixel_height != len(gpio_pins):
        raise Exception('A GPIO pin must be specified for each row of the display matrix.')

    pixel_rows: List[NeoPixel] = []

    # populate matrix
    for gpio_pin_index in gpio_pins:
        gpio_pin = getattr(board, 'D{}'.format(gpio_pin_index))
        pixel_row = NeoPixel(gpio_pin, pixel_width, auto_write=False)
        pixel_rows.append(pixel_row)

    # fill with color
    for pixel_row in pixel_rows:
        pixel_row.fill(color.GREEN)
        pixel_row.show()

    # add some red
    for idx in range(len(pixel_rows)):
        pixel_rows[idx][idx] = color.RED
        pixel_rows[idx].show()

    # scroll text
    text = 'hi!!'
    for char in text:
        char_matrix = font.char_to_matrix(char)
        char_cols = len(char_matrix[0])
        for char_col_idx in range(char_cols):
            for pixel_row_idx, pixel_row in enumerate(pixel_rows):
                pixel_is_on = char_matrix[pixel_row_idx][char_col_idx]
                pixel_row[char_col_idx] = color.RED if pixel_is_on else color.BLACK
                pixel_row.show()

    # deactivate
    for pixel_row in pixel_rows:
        pixel_row.deinit()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Initialize an LED matrix.')
    parser.add_argument(
        '-x',
        '--pixel-width',
        type=int,
        default=DEFAULT_DISPLAY_WIDTH_PX,
        help='Width of display matrix in pixels.'
    )
    parser.add_argument(
        '-y',
        '--pixel-height',
        type=int,
        default=DEFAULT_DISPLAY_HEIGHT_PX,
        help='Height of display matrix in pixels.'
    )
    parser.add_argument(
        '-p',
        '--gpio-pins',
        type=int,
        nargs='*',
        default=DEFAULT_GPIO_PIN_INDICES,
        help='Ordered indices of GPIO pins for each row of matrix.'
    )
    args = parser.parse_args()
    run(gpio_pins=args.gpio_pins, pixel_width=args.pixel_width, pixel_height=args.pixel_height)
