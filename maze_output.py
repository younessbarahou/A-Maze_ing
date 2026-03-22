"""
maze_output.py - Person B
Responsible for: Rendering the maze in the terminal with the solution
                 path drawn on it, and writing the solved output file.

ASCII art scheme
----------------
We draw each maze cell as a 3×3 block of characters:

    +--+
    |  |
    +--+

Walls are shown as  '█' (full block) and open passages as space ' '.
The solution path is shown as  '·' (middle dot).
Entry is marked  'E', exit  'X'.

Because cells share walls with their neighbours, the rendered grid is:
    render_width  = width  * 2 + 1   columns
    render_height = height * 2 + 1   rows
"""

from maze_loader import (
    Maze,
    WALL_NORTH,
    WALL_EAST,
    WALL_SOUTH,
    WALL_WEST,
)

# Characters used in the ASCII output
WALL_CHAR:  str = "█"
OPEN_CHAR:  str = " "
PATH_CHAR:  str = "·"
ENTRY_CHAR: str = "E"
EXIT_CHAR:  str = "X"
CORNER_CHAR: str = "█"


# ──────────────────────────────────────────────────────────────────────
#  Build a 2-D character grid (list of list of str)
# ──────────────────────────────────────────────────────────────────────

def build_render_grid(
    maze: Maze,
    solution_cells: list[tuple[int, int]] | None = None,
) -> list[list[str]]:
    """
    Create a 2-D character array representing the maze visually.

    Each maze cell (col, row) maps to render position (col*2+1, row*2+1).
    Walls between cells sit on even render coordinates.
    Corners sit on even/even render positions.

    Args:
        maze           : the Maze object.
        solution_cells : optional list of (col,row) tuples on the path.

    Returns:
        A list of lists of single characters.
    """
    rw: int = maze.width  * 2 + 1   # render width
    rh: int = maze.height * 2 + 1   # render height

    # Start with everything as wall
    grid: list[list[str]] = [
        [WALL_CHAR] * rw for _ in range(rh)
    ]

    # ── 1. Open up cell centers and passages ─────────────────────────
    for row in range(maze.height):
        for col in range(maze.width):
            rc: int = col * 2 + 1   # render column of cell center
            rr: int = row * 2 + 1   # render row    of cell center

            # Cell center is always open (it is a room, not a wall)
            grid[rr][rc] = OPEN_CHAR

            # Open East passage (between this cell and the right one)
            if col + 1 < maze.width:
                if not (maze.grid[row][col] & WALL_EAST):
                    grid[rr][rc + 1] = OPEN_CHAR   # open the shared wall

            # Open South passage (between this cell and the one below)
            if row + 1 < maze.height:
                if not (maze.grid[row][col] & WALL_SOUTH):
                    grid[rr + 1][rc] = OPEN_CHAR

    # ── 2. Draw the solution path ─────────────────────────────────────
    if solution_cells:
        path_set: set[tuple[int, int]] = set(solution_cells)

        for i, (col, row) in enumerate(solution_cells):
            rc = col * 2 + 1
            rr = row * 2 + 1

            # Mark cell center
            grid[rr][rc] = PATH_CHAR

            # Mark the passage between this cell and the next
            if i + 1 < len(solution_cells):
                ncol, nrow = solution_cells[i + 1]
                nrc = ncol * 2 + 1
                nrr = nrow * 2 + 1
                # The passage is at the midpoint of the render positions
                grid[(rr + nrr) // 2][(rc + nrc) // 2] = PATH_CHAR

    # ── 3. Mark entry and exit ────────────────────────────────────────
    ex, ey = maze.entry
    fx, fy = maze.exit
    grid[ey * 2 + 1][ex * 2 + 1] = ENTRY_CHAR
    grid[fy * 2 + 1][fx * 2 + 1] = EXIT_CHAR

    return grid


# ──────────────────────────────────────────────────────────────────────
#  Print the render grid to the terminal
# ──────────────────────────────────────────────────────────────────────

def print_maze(
    maze: Maze,
    solution_cells: list[tuple[int, int]] | None = None,
) -> None:
    """
    Print the maze (and optional solution path) to stdout.

    Args:
        maze           : the Maze object.
        solution_cells : list of (col,row) on the shortest path, or None.
    """
    render: list[list[str]] = build_render_grid(maze, solution_cells)

    # Print a top border label
    title: str = " A-Maze-ing Solver "
    print(f"\n{'─' * 4}{title}{'─' * 4}\n")

    for row_chars in render:
        print("".join(row_chars))

    print()   # blank line at the bottom

    # Legend
    print(f"  {ENTRY_CHAR} = Entry    {EXIT_CHAR} = Exit    "
          f"{PATH_CHAR} = Shortest path    {WALL_CHAR} = Wall")
    print()


# ──────────────────────────────────────────────────────────────────────
#  Write the solved output file
#  (same format as Person A's output, but with the BFS path filled in)
# ──────────────────────────────────────────────────────────────────────

def write_solved_maze(
    maze: Maze,
    direction_string: str,
    output_path: str,
) -> None:
    """
    Write the maze to a file in the standard hex output format.

    Format (from the subject):
        <hex row 0>\\n
        ...
        <hex row H-1>\\n
        \\n
        <entry_x>,<entry_y>\\n
        <exit_x>,<exit_y>\\n
        <direction_string>\\n

    Args:
        maze             : the Maze object.
        direction_string : e.g. "SSEENW…" from solve_maze().
        output_path      : where to write the file.

    Raises:
        OSError: if the file cannot be written.
    """
    try:
        with open(output_path, "w") as f:
            # ── Grid rows ─────────────────────────────────────────────
            for row in maze.grid:
                # Each cell value 0-15 → one uppercase hex character
                hex_row: str = "".join(format(cell, "X") for cell in row)
                f.write(hex_row + "\n")

            # ── Empty separator line ──────────────────────────────────
            f.write("\n")

            # ── Metadata ──────────────────────────────────────────────
            ex, ey = maze.entry
            fx, fy = maze.exit
            f.write(f"{ex},{ey}\n")
            f.write(f"{fx},{fy}\n")
            f.write(direction_string + "\n")

    except OSError as e:
        raise OSError(
            f"Could not write solved maze to '{output_path}': {e}"
        ) from e

    print(f"✓ Solved maze written to: {output_path}")
