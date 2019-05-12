"""Render a Conway's Game of Life."""
import random
import time
from typing import Any, NamedTuple, Set

from ledmatrix import matrix
from ledmatrix.utilities import colors
from ledmatrix.utilities.colors import BLACK

INITIAL_POPULATION_DENSITY = 0.7  # type: float

CellCoords = NamedTuple('CellCoords', [('row_index', int), ('col_index', int)])


class GameOfLife(matrix.LedMatrix):
    """Matrix for playing Conway's Game of Life.

    See: https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life.
    """
    def __init__(
        self,
        *args,  # type: Any
        **kwargs  # type: Any
    ):  # type: (...) -> None
        super().__init__(*args, **kwargs)
        self._living_cell_coordinates = set()  # type: Set[CellCoords]

        # initialize to random state
        for row_index in range(self.height):
            for col_index in range(self.width):
                if random.random() > INITIAL_POPULATION_DENSITY:  # noqa: S311
                    cell = CellCoords(row_index, col_index)
                    self._living_cell_coordinates.add(cell)
                    self[row_index][col_index] = self.default_color

    def next_state(self):  # type: () -> None
        """Determine which cells live and die and apply to matrix."""
        next_living_cell_coordinates = set()  # type: Set[CellCoords]

        # get batch of cells that will survive / regenerate in the next round
        for cell in self._living_cell_coordinates:
            if self._will_live(cell):
                next_living_cell_coordinates.add(cell)
            for neighbor_cell in self._get_neighbor_coordinates(cell):
                if self._will_live(neighbor_cell):
                    next_living_cell_coordinates.add(neighbor_cell)

        # update living cell coordinates on class
        self._living_cell_coordinates = next_living_cell_coordinates

        # apply changes to the matrix
        for row_index in range(self.height):
            for col_index in range(self.width):
                cell = CellCoords(row_index, col_index)
                if self._is_alive(cell):
                    self[row_index][col_index] = self.default_color
                else:
                    self[row_index][col_index] = BLACK

    def _is_alive(self, cell):  # type: (CellCoords) -> bool
        """Return True if the given cell is alive in the current round."""
        return cell in self._living_cell_coordinates

    def _will_live(self, cell):  # type: (CellCoords) -> bool
        """Return True if the given cell will survive to the next round."""
        neighbors = self._get_neighbor_coordinates(cell)
        num_living_neighbors = sum(self._is_alive(neighbor) for neighbor in neighbors)

        # any cell with three live neighbors will live or revive by "reproduction"
        if num_living_neighbors == 3:
            return True
        # any dead cell not revived by the step above will remain dead
        if not self._is_alive(cell):
            return False
        # any live cell with more than three live neighbors dies by "overpopulation"
        if num_living_neighbors > 3:
            return False
        # any live cell with fewer than two live neighbors dies by "underpopulation"
        if num_living_neighbors < 2:
            return False
        # any remaining cells are alive and will survive to the next round
        return True

    def _get_neighbor_coordinates(self, cell):  # type: (CellCoords) -> Set[CellCoords]
        """Return the coordinates of all 8 neighboring cells for the given cell.

        The board "wraps" so that cells along opposite boundaries are considered neighbors.
        """
        neighbors = set()  # type: Set[CellCoords]

        for row_offset in (-1, 0, 1):
            for col_offset in (-1, 0, 1):
                # skip the origin cell
                if not row_offset and not col_offset:
                    continue

                row_index = cell.row_index + row_offset
                col_index = cell.col_index + col_offset

                # wrap neighbors around board
                if row_index < 0:
                    row_index = row_index + self.height
                if row_index >= self.height:
                    row_index >= row_index - self.height
                if col_index < 0:
                    col_index = col_index + self.width
                if col_index >= self.width:
                    col_index = col_index - self.width

                # add the neighbor cell to the set of neighbors
                neighbor = CellCoords(row_index, col_index)
                neighbors.add(neighbor)

        return neighbors


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--rows', '-r', type=int, default=4)
    parser.add_argument('--cols', '-c', type=int, default=4)
    parser.add_argument('--turns', '-t', type=int, default=20)
    parser.add_argument('--delay', '-d', type=float, default=0.2)
    parser.add_argument('--orient', '-o', default='ALTERNATING_COLUMN')
    parser.add_argument('--start', '-s', default='NORTHEAST')
    parser.add_argument('--color', '-co', type=str, default='RED')
    args = parser.parse_args()

    game = GameOfLife(
        auto_write=False,
        num_rows=args.rows,
        num_cols=args.cols,
        origin=getattr(matrix.MATRIX_ORIGIN, args.start),
        orientation=getattr(matrix.MATRIX_ORIENTATION, args.orient),
        default_color=getattr(colors, args.color),
    )
    try:
        for _ in range(args.turns):
            time.sleep(args.delay)
            game.render()
            game.next_state()
    finally:
        game.deinit()
