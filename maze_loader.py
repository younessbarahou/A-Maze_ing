from typing import List, Tuple


WALL_NORTH = 1
WALL_EAST = 2
WALL_SOUTH = 4
WALL_WEST = 8


class Maze:
    """Represents a 2D maze with entry and exit points.

    Attributes:
        width (int): Width of the maze grid.
        height (int): Height of the maze grid.
        grid (List[List[int]]): 2D list representing the maze layout.
        entry (Tuple[int, int]): Coordinates (x, y) of the maze entry point.
        exit (Tuple[int, int]): Coordinates (x, y) of the maze exit point.
    """
    def __init__(
        self, width: int,
        height: int, grid: List[list[int]], entry: Tuple[int, int],
        exit_: Tuple[int, int]
    ):
        self.width = width
        self.height = height
        self.grid = grid
        self.entry = entry
        self.exit = exit_


def load_maze(filename: str) -> Maze:
    """Loads a maze from a text file and constructs a Maze object.

    The generator writes coordinates as (row, col) i.e. (y, x).
    We convert them to (x, y) = (col, row) for the rest of the system.

    Args:
        filename (str): Path to the maze file to load.

    Returns:
        Maze: A Maze object representing maze with entry and exit points.
    """

    with open(filename, "r") as f:
        lines = [line.strip() for line in f.readlines()]

    # find the empty line
    empty_index = lines.index("")

    grid_lines = lines[:empty_index]
    cordinates = lines[empty_index + 1:]

    # building the grid (maze)
    grid = []
    for line in grid_lines:
        row = []
        for char in line:
            row.append(int(char, 16))  # hex → int
        grid.append(row)

    height = len(grid)
    width = len(grid[0])

    ey, ex = map(int, cordinates[0].split(","))
    gy, gx = map(int, cordinates[1].split(","))

    grid[ey][ex] = 0
    grid[gy][gx] = 0

    entry: Tuple[int, int] = (ex, ey)
    exit_: Tuple[int, int] = (gx, gy)

    return Maze(width, height, grid, entry, exit_)
