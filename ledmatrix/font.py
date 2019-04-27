from typing import Dict, List

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

DEFAULT_FONT_HEIGHT_PX: int = 7
DEFAULT_FONT_PATH = 'ledmatrix/fonts/zig.ttf'
PIL_IMAGE_MODE_BW = '1'  # https://pillow.readthedocs.io/en/stable/handbook/concepts.html#modes
PIL_COLOR_WHITE = 1
PIL_BITMAP_ORIGIN = (0, 0)

_char_cache: Dict[str, List[List[bool]]] = {}
_text_cache: Dict[str, List[List[bool]]] = {}


def char_to_matrix(
    char,  # type: str
    font_path=DEFAULT_FONT_PATH,  # type: str
    font_height_px=DEFAULT_FONT_HEIGHT_PX,  # type: int
    font_expand_px=0,  # type: int
    font_shift_down_px=0,  # type: int
):  # type: (...) -> List[List[bool]]
    """Convert a string to a 2-D matrix.

    From: stackoverflow.com/questions/36384353/generate-pixel-matrices-from-characters-in-string
    """
    # return from cache if available
    # NOTE: assumes we're only ever using a single font height
    if char in _char_cache:
        return _char_cache[char]

    # parse the font and write the char to a bitmap
    font = ImageFont.truetype(font_path, font_height_px + font_expand_px)
    bitmap_width_px, bitmap_height_px = font.getsize(char)
    bitmap_size = (bitmap_width_px, bitmap_height_px)
    image = Image.new(mode=PIL_IMAGE_MODE_BW, size=bitmap_size, color=PIL_COLOR_WHITE)
    draw = ImageDraw.Draw(im=image)
    origin = (PIL_BITMAP_ORIGIN[0], PIL_BITMAP_ORIGIN[1] + font_shift_down_px)
    draw.text(origin, char, font=font)

    # populate the matrix
    matrix_rows = []  # type: List[List[bool]]
    for row_index in range(font_height_px):
        row: List[bool] = []
        for col_index in range(bitmap_width_px):
            try:
                if image.getpixel((col_index, row_index)):
                    row.append(False)
                else:
                    row.append(True)
            except IndexError:
                row.append(False)

        matrix_rows.append(row)

    # add to cache and return
    _char_cache[char] = matrix_rows
    return matrix_rows


def text_to_matrix(
    text,  # type: str
    font_path=DEFAULT_FONT_PATH,   # type: str
    font_height_px=DEFAULT_FONT_HEIGHT_PX,   # type: int
    font_expand_px=3,   # type: int
    font_shift_down_px=-1,   # type: int
):  # type: (...) -> List[List[bool]]
    char_matrices: List[List[List[bool]]] = []
    text_matrix: List[List[bool]] = []

    # return from cache if available
    # NOTE: assumes we're only ever using a single font height
    if text in _text_cache:
        return _text_cache[text]

    # transform each character in text to a 2-D pixel matrix of binary values
    for char in text:
        char_matrix = char_to_matrix(
            char,
            font_height_px=font_height_px,
            font_expand_px=font_expand_px,
            font_shift_down_px=font_shift_down_px,
        )
        char_matrices.append(char_matrix)

    # join character matrices into a single matrix
    for row_index in range(font_height_px):
        text_matrix.append([])
        for char_matrix in char_matrices:
            text_matrix[row_index] = text_matrix[row_index] + char_matrix[row_index]

    _text_cache[text] = text_matrix
    return text_matrix
