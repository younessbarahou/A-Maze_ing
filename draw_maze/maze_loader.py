from typing import List, Tuple


WALL_NORTH = 1
WALL_EAST = 2
WALL_SOUTH = 4
WALL_WEST = 8


class Maze:
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
    """
    Load maze from file
    """

    with open(filename, "r") as f:
        lines = [line.strip() for line in f.readlines()]

    # find the empty line ('end')
    empty_index = lines.index("")

    grid_lines = lines[:empty_index]
    cordinates = lines[empty_index + 1:]

    # bulding the grid (maze)
    grid = []
    for line in grid_lines:
        row = []
        for char in line:
            row.append(int(char, 16))  # hex → int
        grid.append(row)

    height = len(grid)
    width = len(grid[0])

    # entry & exit
    ex, ey = map(int, cordinates[0].split(","))
    gx, gy = map(int, cordinates[1].split(","))

    entry: Tuple[int, int] = (ex, ey)
    exit_: Tuple[int, int] = (gx, gy)
    return Maze(width, height, grid, entry, exit_)
    
