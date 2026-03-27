WALL_NORTH = 1
WALL_EAST  = 2
WALL_SOUTH = 4
WALL_WEST  = 8


class Maze:
    def __init__(self, width, height, grid, entry, exit_):
        self.width = width
        self.height = height
        self.grid = grid
        self.entry = entry
        self.exit = exit_


def load_maze(filename):
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
    entry = tuple(map(int, cordinates[0].split(",")))
    exit_ = tuple(map(int, cordinates[1].split(",")))

    return Maze(width, height, grid, entry, exit_)
