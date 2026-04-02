from maze_loader import WALL_EAST, WALL_SOUTH
from typing import List, Optional
from maze_loader import Maze


WALL = "█"
EMPTY = " "
PATH = "•"
ENTRY = "E"
EXIT = "X"
CELL_42 = "#"

_42_CELLS = {
    (2, 2), (3, 2), (4, 2), (4, 3), (4, 4), (5, 4), (6, 4),
    (2, 6), (2, 7), (2, 8), (3, 8), (4, 8), (4, 7), (4, 6),
    (5, 6), (6, 6), (6, 7), (6, 8)
}


def build_grid(
    maze: Maze,
    path: Optional[List[tuple[int, int]]]
) -> List[List[str]]:
    """Builds a 2D string representation of the maze including walls,
    empty cells, and optional path.

    Args:
        maze (Maze): The maze object containing the grid, entry, and exit.
        path (Optional[List[tuple[int, int]]]): List of (x, y)
        coordinates representing the solution path.

    Returns:
        List[List[str]]: A 2D list of strings representing the maze.
    """
    w = maze.width * 2 + 1
    h = maze.height * 2 + 1

    grid = [[WALL for _ in range(w)] for _ in range(h)]

    # 1. open cells
    for y in range(maze.height):
        for x in range(maze.width):

            rx = x * 2 + 1
            ry = y * 2 + 1

            grid[ry][rx] = EMPTY

            if x + 1 < maze.width:
                if (not (maze.grid[y][x] & WALL_EAST)
                    and maze.grid[y][x + 1] != 15):
                    grid[ry][rx + 1] = EMPTY

            if y + 1 < maze.height:
                if (not (maze.grid[y][x] & WALL_SOUTH)
                        and maze.grid[y + 1][x] != 15):
                    grid[ry + 1][rx] = EMPTY

    # 2. mark 42 cells
    if maze.height >= 12 and maze.width >= 12:
        ex, ey = maze.entry
        fx, fy = maze.exit
        for (cy, cx) in _42_CELLS:
            if (cx, cy) == (ex, ey) or (cx, cy) == (fx, fy):
                continue
            if cy < maze.height and cx < maze.width:
                grid[cy * 2 + 1][cx * 2 + 1] = CELL_42

    # 3. draw path
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

    # 4. entry & exit
    ex, ey = maze.entry
    fx, fy = maze.exit

    grid[ey * 2 + 1][ex * 2 + 1] = ENTRY
    grid[fy * 2 + 1][fx * 2 + 1] = EXIT

    return grid


def print_maze(
    maze: Maze,
    path: Optional[List[tuple[int, int]]] = None
) -> None:
    """Prints the maze to the console as a grid of characters.

    Args:
        maze (Maze): The maze object containing the grid, entry, and exit.
        path (Optional[List[tuple[int, int]]]): List of (x, y)
        coordinates representing the solution path.
    """
    grid = build_grid(maze, path)

    for row in grid:
        print("".join(row))
