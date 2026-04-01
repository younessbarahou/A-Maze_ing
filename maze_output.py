from typing import List, Optional
from maze_loader import Maze, WALL_EAST, WALL_SOUTH


WALL = "█"
EMPTY = " "
PATH = "•"
ENTRY = "E"
EXIT = "X"
CELL_42 = "#"


def build_grid(
    maze: Maze,
    path: Optional[List[tuple[int, int]]]
) -> List[List[str]]:

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
                if not (maze.grid[y][x] & WALL_EAST):
                    grid[ry][rx + 1] = EMPTY

            if y + 1 < maze.height:
                if not (maze.grid[y][x] & WALL_SOUTH):
                    grid[ry + 1][rx] = EMPTY

    # mark 42 cells
    if maze.height >= 12 and maze.width >= 12:
        for y in range(maze.height):
            for x in range(maze.width):
                rx = x * 2 + 1
                ry = y * 2 + 1

                if maze.grid[y][x] == 15:
                    grid[ry][rx] = CELL_42

    # 3. draw path (overwrites # if path goes through)
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

    # 4. entry & exit (always on top)
    ex, ey = maze.entry
    fx, fy = maze.exit
    grid[ey*2+1][ex*2+1] = ENTRY
    grid[fy*2+1][fx*2+1] = EXIT

    return grid


def print_maze(
    maze: Maze,
    path: Optional[List[tuple[int, int]]] = None
) -> None:
    """Print the maze to the console."""

    grid = build_grid(maze, path)

    for row in grid:
        print("".join(row))
