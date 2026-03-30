from collections import deque
from typing import List, Optional
from maze_loader import WALL_NORTH, WALL_EAST, WALL_SOUTH, WALL_WEST
from maze_loader import Maze


DIRECTIONS = [
    ("N", 0, -1, WALL_NORTH),
    ("E", 1, 0, WALL_EAST),
    ("S", 0, 1, WALL_SOUTH),
    ("W", -1, 0, WALL_WEST),
]


def bfs_solve(maze: Maze) -> Optional[List[tuple[int, int]]]:
    """Solves the maze using Breadth-First Search (BFS)
    and returns the solution path.

    Args:
        maze (Maze): The maze object containing grid, entry, and exit.

    Returns:
        Optional[List[tuple[int, int]]]: List of coordinates (x, y)
        from entry to exit if a solution exists; otherwise, None.
    """
    start = maze.entry
    goal = maze.exit

    queue = deque([start])
    visited = {start}

    parent: dict[tuple[int, int], Optional[tuple[int, int]]] = {start: None}

    while queue:
        x, y = queue.popleft()

        if (x, y) == goal:
            return build_path(parent, goal)

        for _, dx, dy, wall in DIRECTIONS:

            if maze.grid[y][x] & wall:
                continue

            nx = x + dx
            ny = y + dy

            if nx < 0 or ny < 0 or nx >= maze.width or ny >= maze.height:
                continue

            if (nx, ny) in visited:
                continue

            visited.add((nx, ny))
            parent[(nx, ny)] = (x, y)
            queue.append((nx, ny))

    return None


def build_path(
    parent: dict[tuple[int, int], Optional[tuple[int, int]]],
    goal: tuple[int, int],
) -> List[tuple[int, int]]:
    """Reconstructs the path from the BFS parent dictionary.

    Args:
        parent (Dict[tuple[int, int], Optional[tuple[int, int]]])
            cell to its parent cell in the BFS tree.
        goal (tuple[int, int]): Coordinates (x, y) of the goal cell.

    Returns:
        List[tuple[int, int]]: Ordered list of coordinates from start to goal.
    """
    path: List[tuple[int, int]] = []
    current: Optional[tuple[int, int]] = goal

    while current is not None:
        path.append(current)
        current = parent[current]

    path.reverse()
    return path


def path_to_directions(path: List[tuple[int, int]]) -> str:
    """Converts a list of path coordinates into directional letters.

    Each step in the path is converted to a corresponding direction symbol
    according to the DIRECTIONS mapping (e.g., 'N', 'S', 'E', 'W').

    Args:
        path (List[tuple[int, int]]): Ordered list of coordinates
        representing a path.

    Returns:
        str: String of directional letters representing
        the moves from start to goal.
    """
    result = ""

    for i in range(len(path) - 1):
        x1, y1 = path[i]
        x2, y2 = path[i + 1]

        dx = x2 - x1
        dy = y2 - y1

        for letter, dxx, dyy, _ in DIRECTIONS:
            if dx == dxx and dy == dyy:
                result += letter

    return result
