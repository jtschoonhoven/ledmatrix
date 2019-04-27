import os
import time
import random
from typing import Any, NamedTuple, Set

from ledmatrix import color, matrix

INITIAL_POPULATION_DENSITY: float = 0.7


class CellCoords(NamedTuple):
    """X and Y index of a "cell" in the game."""
    row_index: int
    col_index: int


class GameOfLife(matrix.LedMatrix):
    """Matrix for playing Conway's Game of Life.

    See: https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life.
    """
    def __init__(self, *args: Any, color: color.Color = color.RED, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._color = color
        self._living_cell_coordinates: Set[CellCoords] = set()

        # initialize to random state
        for row_index in range(self.height):
            for col_index in range(self.width):
                if random.random() > INITIAL_POPULATION_DENSITY:
                    cell = CellCoords(row_index, col_index)
                    self._living_cell_coordinates.add(cell)
                    self[row_index][col_index] = color

    def next(self) -> None:
        """Determine which cells live and die and apply to matrix."""
        next_living_cell_coordinates: Set[CellCoords] = set()

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
                    self[row_index][col_index] = self._color
                else:
                    self[row_index][col_index] = color.BLACK

    def _is_alive(self, cell: CellCoords) -> bool:
        """True if the given cell is alive in the current round."""
        return cell in self._living_cell_coordinates

    def _will_live(self, cell: CellCoords) -> bool:
        """True if the given cell will survive to the next round."""
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

    def _get_neighbor_coordinates(self, cell: CellCoords) -> Set[CellCoords]:
        """Return the coordinates of all 8 neighboring cells for the given cell.

        The board "wraps" so that cells along opposite boundaries are considered neighbors.
        """
        neighbors: Set[CellCoords] = set()

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
    game = GameOfLife(num_rows=7, num_cols=40)
    for round_index in range(90):
        os.system('clear')
        print(game)
        time.sleep(0.1)
        game.next()
