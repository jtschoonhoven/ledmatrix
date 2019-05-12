"""Module for translating text to a pixel matrix in a given font."""
import string
from typing import Dict, List, NamedTuple

from PIL import Image, ImageDraw, ImageFont


DEFAULT_FONT_HEIGHT_PX = 7
DEFAULT_FONT_PATH = 'ledmatrix/fonts/zig.ttf'
PIL_IMAGE_MODE_1BIT = '1'  # https://pillow.readthedocs.io/en/stable/handbook/concepts.html#modes
PIL_IMAGE_MODE_8BIT = 'L'
PIL_COLOR_MODE_8BIT = 255
PIL_COLOR_BLACK = 0
PIL_BITMAP_ORIGIN = (0, 0)


"""Most fonts need extra fine-tuning to render properly on a small display."""
FontOptions = NamedTuple(
    'FontOptions',
    [
        ('font_expand_px', int),  # expand the font by this many vertical pixels
        ('font_shift_down_px', int),  # shift the font down by this many pixels
    ],
)


class Font:
    """Transform text into a matrix-friendly pixel grid in the style of a given font."""

    def __init__(
        self,
        font_path=DEFAULT_FONT_PATH,  # type: str
        font_height_px=DEFAULT_FONT_HEIGHT_PX,  # type: int
        enable_antialiasing=True,  # type: bool
    ):  # type: (...) -> None
        self.font_path = font_path
        self.font_height_px = font_height_px
        self.enable_antialiasing = enable_antialiasing
        self._char_cache = {}  # type: Dict[str, List[List[int]]]
        self._text_cache = {}  # type: Dict[str, List[List[int]]]
        self._font_options = self._get_font_options()

    def text_to_matrix(self, text):  # type: (str) -> List[List[int]]
        """Convert a string to a matrix-friendly 2D array."""
        char_matrices = []  # type:  List[List[List[int]]]

        # return from cache if available
        if self._text_cache.get(text):
            return self._text_cache[text]

        # transform each character in text to a 2-D pixel matrix of binary values
        for char in text:
            # return from cache if available
            if self._char_cache.get(char):
                char_matrices.append(self._char_cache[char])
                continue

            # convert char to matrix
            char_matrix = self._char_to_matrix(
                char,
                font_path=self.font_path,
                font_height_px=self.font_height_px,
                font_expand_px=self._font_options.font_expand_px,
                font_shift_down_px=self._font_options.font_shift_down_px,
                enable_antialiasing=self.enable_antialiasing,
            )

            # add char matrix to cache and append to list of matrices
            char_matrices.append(char_matrix)
            self._char_cache[char] = char_matrix

        # join characters matrices into a single matrix, then add to cache and return
        text_matrix = self._join_matrices(char_matrices)
        self._text_cache[text] = text_matrix
        return text_matrix

    def _join_matrices(self, matrices):  # type: (List[List[List[int]]]) -> List[List[int]]
        """Concatenate multiple matrices (a 3D-matrix) into a single matrix (2D)."""
        joined_matrix = []  # type: List[List[int]]

        # join character matrices into a single matrix
        for row_index in range(self.font_height_px):
            joined_matrix.append([])
            for char_matrix in matrices:
                joined_matrix[row_index] = joined_matrix[row_index] + char_matrix[row_index]

        return joined_matrix

    def _char_to_matrix(
        self,
        char,  # type: str
        font_path=DEFAULT_FONT_PATH,  # type: str
        font_height_px=DEFAULT_FONT_HEIGHT_PX,  # type: int
        font_expand_px=0,  # type: int
        font_shift_down_px=0,  # type: int
        enable_antialiasing=True,  # type: bool
    ):  # type: (...) -> List[List[int]]
        """Convert a single character to a 2-D matrix.

        From: stackoverflow.com/questions/36384353/generate-pixel-matrices-from-characters-in-string
        """
        if enable_antialiasing:
            image_mode = PIL_IMAGE_MODE_8BIT
        else:
            image_mode = PIL_IMAGE_MODE_1BIT

        # parse the font and write the char to a bitmap
        font = ImageFont.truetype(font_path, font_height_px + font_expand_px)
        bitmap_width_px, bitmap_height_px = font.getsize(char)
        bitmap_size = (bitmap_width_px, bitmap_height_px)
        image = Image.new(mode=image_mode, size=bitmap_size, color=PIL_COLOR_MODE_8BIT)
        draw = ImageDraw.Draw(im=image)
        origin = (PIL_BITMAP_ORIGIN[0], PIL_BITMAP_ORIGIN[1] + font_shift_down_px)
        draw.text(origin, char, font=font)

        # populate the matrix
        matrix_rows = []  # type: List[List[int]]
        for row_index in range(font_height_px):
            row = []  # type: List[int]
            for col_index in range(bitmap_width_px):
                try:
                    # pixel value is 0 or 1 for BW, 0-255 for grayscale
                    pixel_value = image.getpixel((col_index, row_index))
                    # invert value for colored text on dark background
                    pixel_value = abs(pixel_value - 255)
                    row.append(pixel_value)
                except IndexError:
                    row.append(PIL_COLOR_BLACK)

            matrix_rows.append(row)
        return matrix_rows

    def _get_font_options(self):  # type: () -> FontOptions
        """Get options for fine-tuning the font scaling.

        NOTE: this optimizes for ASCII letters and digits: there are other characters
        (unusual punctuation or non-LATIN1 characters) that may be truncated.
        """
        font_expand_px = 0
        font_shift_down_px = 0
        test_chars = string.ascii_uppercase + string.digits

        # continue tweaking font size until characters are perfectly scaled
        while True:
            char_matrices = {}  # type: Dict[str, List[List[int]]]

            # generate a matrix for each character
            for char in test_chars:
                char_matrix = self._char_to_matrix(
                    char,
                    font_path=self.font_path,
                    font_height_px=self.font_height_px,
                    font_expand_px=font_expand_px,
                    font_shift_down_px=font_shift_down_px,
                    enable_antialiasing=self.enable_antialiasing,
                )
                char_matrices[char] = char_matrix

            # concatenate all character matrices
            text_matrix = self._join_matrices(list(char_matrices.values()))
            first_row = text_matrix[0]
            last_row = text_matrix[-1]

            # expand font if it does not reach the bottom of the matrix
            if not any(last_row):
                font_expand_px += 1
                continue

            # shift font up if it doesn't reach the top of the matrix
            if not any(first_row):
                font_shift_down_px -= 0.5  # type: ignore
                continue

            # else the font is properly scaled: cache and return the result
            self._char_cache = char_matrices
            return FontOptions(
                font_expand_px=font_expand_px,
                font_shift_down_px=font_shift_down_px,
            )