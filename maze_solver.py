"""
maze_solver.py - Person B
Responsible for: Finding the shortest path from entry to exit using BFS,
                 then reconstructing and returning it as a direction string.

BFS (Breadth-First Search) guarantees the SHORTEST path in an unweighted
graph like a maze.  Here each cell is a node, and two cells are connected
if there is NO wall between them.
"""

from collections import deque      # deque is used as an efficient queue
from typing import Optional

# Import the Maze class and wall constants from our loader
from maze_loader import (
    Maze,
    WALL_NORTH,
    WALL_EAST,
    WALL_SOUTH,
    WALL_WEST,
)


# ──────────────────────────────────────────────────────────────────────
#  Direction tables
#
#  Each direction has:
#    - a letter  : used in the output path string
#    - a delta   : (dcol, drow) to reach the neighbour
#    - wall_here : the wall bit on the CURRENT cell to check
#    - wall_there: the wall bit on the NEIGHBOUR cell (for symmetry)
# ──────────────────────────────────────────────────────────────────────

# (letter, dcol, drow, wall_bit_on_current_cell)
DIRECTIONS: list[tuple[str, int, int, int]] = [
    ("N",  0, -1, WALL_NORTH),   # North → row decreases
    ("E",  1,  0, WALL_EAST),    # East  → col increases
    ("S",  0,  1, WALL_SOUTH),   # South → row increases
    ("W", -1,  0, WALL_WEST),    # West  → col decreases
]


# ──────────────────────────────────────────────────────────────────────
#  BFS core
# ──────────────────────────────────────────────────────────────────────

def bfs_solve(maze: Maze) -> Optional[list[tuple[int, int]]]:
    """
    Find the shortest path from maze.entry to maze.exit using BFS.

    How BFS works (step by step):
      1. Start at the entry cell. Mark it as visited.
      2. Put the entry cell in a queue.
      3. Take the first cell from the queue.
      4. For each of its 4 neighbours:
           - If there is NO wall between them, and the neighbour was
             not visited yet:
               * Mark the neighbour as visited.
               * Remember which cell we came FROM (this is the "parent" map).
               * Add the neighbour to the queue.
      5. Stop as soon as we reach the exit cell.
      6. If the queue empties without reaching the exit → no path exists.

    Because BFS explores cells layer by layer (distance 1, then 2, …),
    the first time we reach the exit it is guaranteed to be via the
    shortest possible path.

    Args:
        maze: a validated Maze object.

    Returns:
        A list of (col, row) tuples from entry to exit (inclusive),
        or None if no path exists.
    """

    start: tuple[int, int] = maze.entry
    goal:  tuple[int, int] = maze.exit

    # visited[row][col] = True once a cell has been seen
    visited: list[list[bool]] = [
        [False] * maze.width for _ in range(maze.height)
    ]

    # parent[(col, row)] = the cell we came from to reach (col, row)
    # We use this later to trace back the path from goal → start.
    parent: dict[tuple[int, int], Optional[tuple[int, int]]] = {}

    # Mark the start as visited; it has no parent
    sx, sy = start
    visited[sy][sx] = True
    parent[start] = None   # None means "this is the beginning"

    # The BFS queue holds (col, row) tuples.
    # deque allows O(1) popleft() unlike a plain list.
    queue: deque[tuple[int, int]] = deque()
    queue.append(start)

    # ── BFS loop ──────────────────────────────────────────────────────
    while queue:
        # Take the next cell to explore
        current: tuple[int, int] = queue.popleft()
        cx, cy = current

        # Did we reach the goal?
        if current == goal:
            return _reconstruct_path(parent, start, goal)

        # Try all 4 directions
        for (letter, dcol, drow, wall_bit) in DIRECTIONS:
            # Skip if there is a wall in this direction
            if maze.grid[cy][cx] & wall_bit:
                continue   # wall present → can't go that way

            # Compute the neighbour's coordinates
            nx: int = cx + dcol
            ny: int = cy + drow

            # Skip if out of bounds
            if not (0 <= nx < maze.width and 0 <= ny < maze.height):
                continue

            # Skip if already visited
            if visited[ny][nx]:
                continue

            # ✅ Reachable, unvisited neighbour → add to queue
            visited[ny][nx] = True
            neighbour: tuple[int, int] = (nx, ny)
            parent[neighbour] = current
            queue.append(neighbour)

    # Queue exhausted without reaching goal → no path
    return None


# ──────────────────────────────────────────────────────────────────────
#  Path reconstruction
# ──────────────────────────────────────────────────────────────────────

def _reconstruct_path(
    parent: dict[tuple[int, int], Optional[tuple[int, int]]],
    start:  tuple[int, int],
    goal:   tuple[int, int],
) -> list[tuple[int, int]]:
    """
    Walk backwards through the parent map to rebuild the path.

    BFS stores, for every visited cell, which cell we came FROM.
    To get the path we start at the goal and follow parent pointers
    until we reach the start, then reverse the list.

    Args:
        parent: maps each visited cell to the cell before it on the path.
        start:  entry cell (col, row).
        goal:   exit cell  (col, row).

    Returns:
        List of (col, row) from start to goal.
    """
    path: list[tuple[int, int]] = []
    current: Optional[tuple[int, int]] = goal

    # Follow parent pointers: goal → ... → start
    while current is not None:
        path.append(current)
        current = parent[current]

    # The list is currently goal→start; reverse it to get start→goal
    path.reverse()
    return path


# ──────────────────────────────────────────────────────────────────────
#  Convert cell-list path → direction string
# ──────────────────────────────────────────────────────────────────────

def path_to_directions(cell_path: list[tuple[int, int]]) -> str:
    """
    Turn a list of (col, row) cells into a direction string like "SSEEN…".

    For each consecutive pair of cells we figure out which direction
    was taken and append the matching letter.

    Args:
        cell_path: ordered list of (col, row) from entry to exit.

    Returns:
        A string of N/E/S/W characters.

    Example:
        [(0,0), (0,1), (1,1)] → "SE"
        (went South then East)
    """
    direction_string: str = ""

    for i in range(len(cell_path) - 1):
        curr_col, curr_row = cell_path[i]
        next_col, next_row = cell_path[i + 1]

        dcol: int = next_col - curr_col
        drow: int = next_row - curr_row

        # Match the delta to a direction letter
        letter: str = ""
        for (ltr, ddcol, ddrow, _wall) in DIRECTIONS:
            if dcol == ddcol and drow == ddrow:
                letter = ltr
                break

        if letter == "":
            # This should never happen if the path is valid
            raise ValueError(
                f"Cannot determine direction from "
                f"({curr_col},{curr_row}) to ({next_col},{next_row})"
            )

        direction_string += letter

    return direction_string


# ──────────────────────────────────────────────────────────────────────
#  Public convenience function
# ──────────────────────────────────────────────────────────────────────

def solve_maze(maze: Maze) -> Optional[str]:
    """
    Solve the maze and return the direction string of the shortest path.

    This is the main entry point for Person B's solver.

    Args:
        maze: a validated Maze object (from maze_loader.load_maze()).

    Returns:
        A string of N/E/S/W letters describing the shortest path,
        or None if the maze has no solution.
    """
    cell_path: Optional[list[tuple[int, int]]] = bfs_solve(maze)

    if cell_path is None:
        return None   # unsolvable maze

    return path_to_directions(cell_path)
