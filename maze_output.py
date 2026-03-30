from maze_loader import WALL_EAST, WALL_SOUTH
from typing import List, Optional
from maze_loader import Maze


WALL = "█"
EMPTY = " "
PATH = "•"
ENTRY = "E"
EXIT = "X"


def build_grid(
    maze: Maze,
    path: Optional[List[tuple[int, int]]]
) -> List[List[str]]:
    """Builds a 2D string representation of the maze including walls,
    empty cells, and optional path.

    The resulting grid doubles the maze dimensions to account for
    walls between cells.
    Optionally marks a path through the maze if provided.

    Args:
        maze (Maze): The maze object containing the grid, entry, and exit.
        path (Optional[List[tuple[int, int]]]): List of (x, y)
        coordinates representing the solution path.
            If None, no path is drawn.

    Returns:
        List[List[str]]: A 2D list of strings representing
        the maze with walls, empty cells, entry, exit,
            and path markers.
    """
    w = maze.width * 2 + 1
    h = maze.height * 2 + 1

    grid = [[WALL for _ in range(w)] for _ in range(h)]

    # open cells
    for y in range(maze.height):
        for x in range(maze.width):

            rx = x * 2 + 1
            ry = y * 2 + 1

            grid[ry][rx] = EMPTY

            # east
            if x + 1 < maze.width:
                if not (maze.grid[y][x] & WALL_EAST):
                    grid[ry][rx + 1] = EMPTY

            # south
            if y + 1 < maze.height:
                if not (maze.grid[y][x] & WALL_SOUTH):
                    grid[ry + 1][rx] = EMPTY

    # draw path
    if path is not None:
        for i in range(len(path)):
            x, y = path[i]
            rx = x * 2 + 1
            ry = y * 2 + 1

            grid[ry][rx] = PATH

            if i > 0:
                px, py = path[i - 1]
                prx = px * 2 + 1
                pry = py * 2 + 1

                grid[(ry + pry)//2][(rx + prx)//2] = PATH

    # entry & exit
    ex, ey = maze.entry
    fx, fy = maze.exit

    grid[ey*2+1][ex*2+1] = ENTRY
    grid[fy*2+1][fx*2+1] = EXIT

    return grid


def print_maze(
    maze: Maze,
    path: Optional[List[tuple[int, int]]]
) -> None:
    """Prints the maze to the console as a grid of characters.

    Uses `build_grid` to generate the 2D grid including walls,
    empty cells, entry, exit,
    and an optional path, then prints it row by row.

    Args:
        maze (Maze): The maze object containing the grid, entry, and exit.
        path (Optional[List[tuple[int, int]]]): List of (x, y)
        coordinates representing the solution path.
            If None, no path is printed.

    Returns:
        None
    """
    grid = build_grid(maze, path)

    for row in grid:
        print("".join(row))
