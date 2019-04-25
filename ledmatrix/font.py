from typing import Dict, List

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

DEFAULT_FONT_HEIGHT_PX: int = 7
PIL_IMAGE_MODE_BW = '1'  # https://pillow.readthedocs.io/en/stable/handbook/concepts.html#modes
PIL_COLOR_BLACK = 0
PIL_BITMAP_ORIGIN = (0, 0)

_char_cache: Dict[str, List[List[bool]]] = {}


def char_to_matrix(
    char: str,
    font_path: str = 'ledmatrix/fonts/silkscreen.ttf',
    font_height_px: int = DEFAULT_FONT_HEIGHT_PX,
) -> List[List[bool]]:
    """Convert a string to a 2-D matrix.
    From: stackoverflow.com/questions/36384353/generate-pixel-matrices-from-characters-in-string
    """
    # return from cache if available
    # NOTE: assumes we're only ever using a single font height
    if char in _char_cache:
        return _char_cache[char]

    # parse the font and write the char to a bitmap
    font = ImageFont.truetype(font_path, font_height_px)
    bitmap_width_px, bitmap_height_px = font.getsize(char)
    bitmap_size = (bitmap_width_px, bitmap_height_px)
    image = Image.new(mode=PIL_IMAGE_MODE_BW, size=bitmap_size, color=PIL_COLOR_BLACK)
    draw = ImageDraw.Draw(im=image)
    draw.text(PIL_BITMAP_ORIGIN, char, font=font)

    # populate the matrix
    matrix_rows: List[List[bool]] = []
    for row_index in range(bitmap_height_px):
        row: List[bool] = []
        for col_index in range(bitmap_width_px):
            if image.getpixel((col_index, row_index)):
                row.append(True)
            else:
                row.append(False)
        matrix_rows.append(row)

    # add to cache and return
    _char_cache[char] = matrix_rows
    return matrix_rows
