"""
maze_loader.py - Person B
Responsible for: Loading a maze file, validating its structure.

The maze file format:
- Each line is a row of hex digits (one per cell).
- Each hex digit encodes walls: bit0=North, bit1=East, bit2=South, bit3=West
- After the grid rows, there is an empty line, then:
    Line 1: entry coordinates  (e.g. "0,0")
    Line 2: exit  coordinates  (e.g. "19,14")
    Line 3: shortest path      (e.g. "SSEENW...")
"""

from typing import Optional


# ─────────────────────────────────────────────
#  Wall bit-mask constants (easy to remember)
# ─────────────────────────────────────────────
WALL_NORTH: int = 0b0001   # bit 0
WALL_EAST:  int = 0b0010   # bit 1
WALL_SOUTH: int = 0b0100   # bit 2
WALL_WEST:  int = 0b1000   # bit 3


class MazeLoadError(Exception):
    """Raised when something is wrong with the maze file."""
    pass


class Maze:
    """
    Holds the maze data after it has been loaded from a file.

    Attributes:
        width  (int)           : number of columns
        height (int)           : number of rows
        grid   (list[list[int]]): grid[row][col] = wall bitmask (0-15)
        entry  (tuple[int,int]): (col, row) of the entrance
        exit   (tuple[int,int]): (col, row) of the exit
        path   (str)           : solution path string from the file
                                 (may be empty if the file has none)
    """

    def __init__(
        self,
        width: int,
        height: int,
        grid: list[list[int]],
        entry: tuple[int, int],
        exit_: tuple[int, int],
        path: str,
    ) -> None:
        """Store all maze fields."""
        self.width:  int             = width
        self.height: int             = height
        self.grid:   list[list[int]] = grid
        self.entry:  tuple[int, int] = entry
        self.exit:   tuple[int, int] = exit_
        self.path:   str             = path

    # ------------------------------------------------------------------
    # Small helper: does cell (col, row) have a wall in direction d?
    # ------------------------------------------------------------------
    def has_wall(self, col: int, row: int, direction: int) -> bool:
        """
        Return True if the cell at (col, row) has a wall on the given side.

        Args:
            col       : x-index (0 = left)
            row       : y-index (0 = top)
            direction : one of WALL_NORTH / WALL_EAST / WALL_SOUTH / WALL_WEST

        Returns:
            True if that wall bit is set, False otherwise.
        """
        return bool(self.grid[row][col] & direction)


# ──────────────────────────────────────────────────────────────────────
#  STEP 1 – Read the raw text from the file
# ──────────────────────────────────────────────────────────────────────

def read_maze_file(filepath: str) -> list[str]:
    """
    Open the maze file and return a list of non-empty lines.

    Args:
        filepath: path to the maze output file (e.g. "maze.txt")

    Returns:
        List of raw text lines (with trailing whitespace stripped).

    Raises:
        MazeLoadError: if the file cannot be opened.
    """
    try:
        with open(filepath, "r") as f:
            # Read every line; strip trailing newline / spaces
            lines: list[str] = [line.rstrip() for line in f.readlines()]
    except OSError as e:
        raise MazeLoadError(f"Cannot open maze file '{filepath}': {e}") from e

    return lines


# ──────────────────────────────────────────────────────────────────────
#  STEP 2 – Parse the lines into a Maze object
# ──────────────────────────────────────────────────────────────────────

def parse_maze(lines: list[str]) -> Maze:
    """
    Convert raw text lines into a Maze object.

    The expected layout (Person A produces this):
        <hex row 0>
        <hex row 1>
        ...
        <hex row H-1>
                          ← one empty line
        <entry x,y>
        <exit  x,y>
        <path string>     ← optional; may be absent

    Args:
        lines: list of raw text lines from read_maze_file()

    Returns:
        A fully populated Maze instance.

    Raises:
        MazeLoadError: if the format is wrong or data is missing.
    """

    # ── 2a. Split into the grid section and the metadata section ──────
    # Find the first empty line that separates the grid from metadata.
    separator_index: Optional[int] = None
    for i, line in enumerate(lines):
        if line.strip() == "":
            separator_index = i
            break

    if separator_index is None:
        raise MazeLoadError(
            "Maze file is missing the blank separator line "
            "between the grid and the metadata."
        )

    grid_lines: list[str] = lines[:separator_index]
    meta_lines: list[str] = [
        l for l in lines[separator_index + 1:] if l.strip() != ""
    ]

    # We need at least 2 meta lines: entry and exit
    if len(meta_lines) < 2:
        raise MazeLoadError(
            "Maze file must have at least entry and exit lines "
            "after the blank separator."
        )

    # ── 2b. Parse the grid ────────────────────────────────────────────
    if len(grid_lines) == 0:
        raise MazeLoadError("Maze file contains no grid rows.")

    height: int = len(grid_lines)
    # All rows must have the same length (= width of maze)
    width: int = len(grid_lines[0])
    if width == 0:
        raise MazeLoadError("Maze grid row has length 0.")

    grid: list[list[int]] = []

    for row_index, row_str in enumerate(grid_lines):
        if len(row_str) != width:
            raise MazeLoadError(
                f"Row {row_index} has {len(row_str)} cells "
                f"but expected {width}."
            )
        row_values: list[int] = []
        for col_index, char in enumerate(row_str):
            # Each character is one hex digit (0-F / 0-f)
            if char not in "0123456789ABCDEFabcdef":
                raise MazeLoadError(
                    f"Invalid character '{char}' at row {row_index}, "
                    f"col {col_index}. Expected a hex digit."
                )
            row_values.append(int(char, 16))   # convert hex → int
        grid.append(row_values)

    # ── 2c. Parse entry / exit ────────────────────────────────────────
    entry: tuple[int, int] = _parse_coordinate(meta_lines[0], "entry")
    exit_: tuple[int, int] = _parse_coordinate(meta_lines[1], "exit")

    # ── 2d. Parse optional path string ───────────────────────────────
    path: str = meta_lines[2].strip() if len(meta_lines) >= 3 else ""

    return Maze(width, height, grid, entry, exit_, path)


def _parse_coordinate(text: str, name: str) -> tuple[int, int]:
    """
    Parse a coordinate string like "0,0" or "19,14".

    Args:
        text: the raw string, e.g. "19,14"
        name: human-readable label for error messages ("entry" / "exit")

    Returns:
        (x, y) as integers.

    Raises:
        MazeLoadError: if the format is wrong.
    """
    parts: list[str] = text.strip().split(",")
    if len(parts) != 2:
        raise MazeLoadError(
            f"Bad {name} coordinate '{text}'. "
            "Expected format: x,y  (e.g. '0,0')"
        )
    try:
        x: int = int(parts[0].strip())
        y: int = int(parts[1].strip())
    except ValueError as e:
        raise MazeLoadError(
            f"Non-integer in {name} coordinate '{text}'."
        ) from e
    return (x, y)


# ──────────────────────────────────────────────────────────────────────
#  STEP 3 – Validate the maze structure
# ──────────────────────────────────────────────────────────────────────

def validate_maze(maze: Maze) -> list[str]:
    """
    Check that the maze data is internally consistent.

    Checks performed:
      1. Entry and exit are inside the grid bounds.
      2. Entry != exit.
      3. Outer-border cells have the correct outer walls set.
      4. Wall coherence: if cell A has a wall toward B, then B must
         have the matching wall toward A.

    Args:
        maze: a Maze object returned by parse_maze()

    Returns:
        A list of error-message strings.
        Empty list means the maze is valid.
    """
    errors: list[str] = []

    ex, ey = maze.entry
    fx, fy = maze.exit

    # ── Check 1: coordinates in bounds ───────────────────────────────
    if not (0 <= ex < maze.width and 0 <= ey < maze.height):
        errors.append(
            f"Entry ({ex},{ey}) is outside the maze "
            f"({maze.width}x{maze.height})."
        )
    if not (0 <= fx < maze.width and 0 <= fy < maze.height):
        errors.append(
            f"Exit ({fx},{fy}) is outside the maze "
            f"({maze.width}x{maze.height})."
        )

    # ── Check 2: entry != exit ────────────────────────────────────────
    if (ex, ey) == (fx, fy):
        errors.append("Entry and exit are the same cell.")

    # ── Check 3 & 4: wall coherence (neighbour symmetry) ─────────────
    #
    # For every cell, look at its East and South neighbours only
    # (checking all 4 directions would double-count).
    # Also verify outer-border walls.

    for row in range(maze.height):
        for col in range(maze.width):
            cell: int = maze.grid[row][col]

            # --- Outer border walls -----------------------------------
            if row == 0 and not (cell & WALL_NORTH):
                # Top row must have a North wall
                # Exception: entry/exit on top edge
                if (col, row) not in (maze.entry, maze.exit):
                    errors.append(
                        f"Cell ({col},{row}) on top border is missing "
                        "its North wall."
                    )
            if row == maze.height - 1 and not (cell & WALL_SOUTH):
                if (col, row) not in (maze.entry, maze.exit):
                    errors.append(
                        f"Cell ({col},{row}) on bottom border is "
                        "missing its South wall."
                    )
            if col == 0 and not (cell & WALL_WEST):
                if (col, row) not in (maze.entry, maze.exit):
                    errors.append(
                        f"Cell ({col},{row}) on left border is "
                        "missing its West wall."
                    )
            if col == maze.width - 1 and not (cell & WALL_EAST):
                if (col, row) not in (maze.entry, maze.exit):
                    errors.append(
                        f"Cell ({col},{row}) on right border is "
                        "missing its East wall."
                    )

            # --- Neighbour symmetry -----------------------------------
            # East neighbour
            if col + 1 < maze.width:
                right_cell: int = maze.grid[row][col + 1]
                # If THIS cell has East wall, neighbour must have West wall
                if bool(cell & WALL_EAST) != bool(right_cell & WALL_WEST):
                    errors.append(
                        f"Wall mismatch: cell ({col},{row}) East "
                        f"vs cell ({col+1},{row}) West."
                    )

            # South neighbour
            if row + 1 < maze.height:
                bottom_cell: int = maze.grid[row + 1][col]
                if bool(cell & WALL_SOUTH) != bool(bottom_cell & WALL_NORTH):
                    errors.append(
                        f"Wall mismatch: cell ({col},{row}) South "
                        f"vs cell ({col},{row+1}) North."
                    )

    return errors


# ──────────────────────────────────────────────────────────────────────
#  Public convenience function: load + validate in one call
# ──────────────────────────────────────────────────────────────────────

def load_maze(filepath: str) -> Maze:
    """
    Load a maze file, parse it, validate it, and return a Maze object.

    This is the main entry point for Person B's loader.

    Args:
        filepath: path to the maze output file.

    Returns:
        A validated Maze object.

    Raises:
        MazeLoadError: if loading, parsing, or validation fails.
    """
    lines: list[str] = read_maze_file(filepath)
    maze: Maze       = parse_maze(lines)
    errors: list[str] = validate_maze(maze)

    if errors:
        error_text: str = "\n  ".join(errors)
        raise MazeLoadError(
            f"Maze validation failed with {len(errors)} error(s):\n"
            f"  {error_text}"
        )

    return maze
