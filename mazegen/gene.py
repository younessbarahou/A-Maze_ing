"""
Maze Generator - Recursive Backtracker (DFS) algorithm.

Each cell stores which of its 4 walls are CLOSED as a bitmask:
    bit 0 = North  (0b0001)
    bit 1 = East   (0b0010)
    bit 2 = South  (0b0100)
    bit 3 = West   (0b1000)

So a cell with value 0b1010 has its East and West walls closed.
A cell with value 0xF (1111) is fully isolated (all walls closed).
"""

import random
import collections
from typing import Optional

# ------------------------------------------------------------------
# Direction constants
# ------------------------------------------------------------------

NORTH = 0b0001
EAST = 0b0010
SOUTH = 0b0100
WEST = 0b1000

ALL_DIRECTIONS = [NORTH, EAST, SOUTH, WEST]

# When you open a wall on one side, open the matching wall on the other
OPPOSITE_WALL = {
    NORTH: SOUTH,
    SOUTH: NORTH,
    EAST: WEST,
    WEST: EAST,
}

# How much to move in (col, row) when going in each direction
STEP = {
    NORTH: (0, -1),
    EAST: (1, 0),
    SOUTH: (0, 1),
    WEST: (-1, 0),
}

# Direction to letter for the solution path string
DIR_TO_LETTER = {NORTH: "N", EAST: "E", SOUTH: "S", WEST: "W"}

# ------------------------------------------------------------------
# "42" pixel art  (5 rows x 3 cols,  1 = blocked cell)
# ------------------------------------------------------------------

DIGIT_4 = [
    [1, 0, 1],
    [1, 0, 1],
    [1, 1, 1],
    [0, 0, 1],
    [0, 0, 1],
]

DIGIT_2 = [
    [1, 1, 1],
    [0, 0, 1],
    [1, 1, 1],
    [1, 0, 0],
    [1, 1, 1],
]

GLYPH_WIDTH = 3
GLYPH_HEIGHT = 5
GLYPH_GAP = 1

# Minimum maze size to fit "42" (digits + 1-cell margin on each side)
MIN_COLS_FOR_42 = GLYPH_WIDTH * 2 + GLYPH_GAP + 4   # 11
MIN_ROWS_FOR_42 = GLYPH_HEIGHT + 2                    # 7


# ------------------------------------------------------------------
# MazeGenerator
# ------------------------------------------------------------------

class MazeGenerator:
    """Generates a maze using the Recursive Backtracker (DFS) algorithm.

    Usage::

        gen = MazeGenerator(width=20, height=15, seed=42)
        gen.generate(entry=(0, 0), exit_=(19, 14))

        gen.grid            # grid[row][col] wall bitmask
        gen.solution        # list of "N"/"E"/"S"/"W"
        gen.forty_two_cells # set of (col, row) forming the "42" shape

    Args:
        width:   Number of columns (>= 2).
        height:  Number of rows    (>= 2).
        seed:    Random seed for reproducible mazes.
        perfect: True  -> exactly one path between any two cells.
                 False -> extra openings create multiple paths.
    """

    def __init__(
        self,
        width: int = 20,
        height: int = 15,
        seed: Optional[int] = None,
        perfect: bool = True,
    ) -> None:

        self.width = width
        self.height = height
        self.seed = seed
        self.perfect = perfect

        # Filled in by generate()
        self.grid: list[list[int]] = []
        self.entry: tuple[int, int] = (0, 0)
        self.exit: tuple[int, int] = (width - 1, height - 1)
        self.solution: list[str] = []
        self.forty_two_cells: set[tuple[int, int]] = set()
        self.has_forty_two: bool = False
        self._rng = random.Random(seed)

    def generate(
        self,
        entry: Optional[tuple[int, int]] = None,
        exit_: Optional[tuple[int, int]] = None,
    ) -> None:
        """Build the maze.

        Steps:
            1. Validate entry / exit.
            2. Start with every wall closed.
            3. Stamp the "42" blocked cells.
            4. Carve passages with DFS.
            5. Add extra openings if not perfect.
            6. Seal the outer border.
            7. Open the entry and exit border walls.
            8. Fix any wall mismatches between neighbours.
            9. Find the shortest path with BFS.
        """
        if entry is not None:
            self.entry = entry
        if exit_ is not None:
            self.exit = exit_

        self._check_entry_exit()
        self._rng = random.Random(self.seed)

        # Step 2 - every cell starts fully walled
        self.grid = [
            [0xF for _col in range(self.width)]
            for _row in range(self.height)
        ]

        # Step 3 - stamp "42" before carving so DFS skips those cells
        self.forty_two_cells = set()
        self.has_forty_two = False
        if (
            self.width >= MIN_COLS_FOR_42
            and self.height >= MIN_ROWS_FOR_42
        ):
            self._stamp_forty_two()
            self.has_forty_two = True
        else:
            print(
                f"Warning: maze too small for '42' pattern "
                f"(need at least {MIN_COLS_FOR_42}x{MIN_ROWS_FOR_42})."
            )

        # Steps 4-9
        self._carve_with_dfs()
        if not self.perfect:
            self._punch_extra_openings()
        self._seal_outer_border()
        self._open_entry_and_exit()
        self._fix_wall_mismatches()
        self.solution = self._find_shortest_path()

    def save(self, filepath: str) -> None:
        """Write the maze to a file in the required hex format.

        Format:
            - One hex char per cell, one row per line.
            - Blank line.
            - Entry coordinates (col,row).
            - Exit  coordinates (col,row).
            - Solution path string e.g. "NEESSWW".
        """
        if not self.grid:
            raise RuntimeError("Call generate() before save().")

        with open(filepath, "w") as file:
            for row in self.grid:
                file.write(
                    "".join(format(cell, "X") for cell in row) + "\n"
                )
            file.write("\n")
            entry_col, entry_row = self.entry
            exit_col, exit_row = self.exit
            file.write(f"{entry_col},{entry_row}\n")
            file.write(f"{exit_col},{exit_row}\n")
            file.write("".join(self.solution) + "\n")

    def cell_walls(self, col: int, row: int) -> dict[str, bool]:
        """Return which walls are closed for a given cell.

        Returns:
            {"N": bool, "E": bool, "S": bool, "W": bool}
            True = wall is present (closed).
        """
        if not (0 <= col < self.width and 0 <= row < self.height):
            raise IndexError(f"Cell ({col},{row}) is out of bounds.")
        cell_value = self.grid[row][col]
        return {
            "N": bool(cell_value & NORTH),
            "E": bool(cell_value & EAST),
            "S": bool(cell_value & SOUTH),
            "W": bool(cell_value & WEST),
        }

    def _is_blocked(self, col: int, row: int) -> bool:
        """Return True if this cell is part of the '42' pattern."""
        return (col, row) in self.forty_two_cells

    def _stamp_forty_two(self) -> None:
        """Mark the cells that form the '42' glyph as fully walled.

        The glyph is placed in the lower-center area of the maze.
        """
        total_glyph_width = GLYPH_WIDTH * 2 + GLYPH_GAP

        # Top-left corner of the glyph, centered horizontally
        start_col = (self.width - total_glyph_width) // 2
        start_row = (self.height - GLYPH_HEIGHT) // 2 + self.height // 6

        # Keep it inside the maze (1-cell margin from borders)
        start_col = max(1, min(start_col, self.width - total_glyph_width - 1))
        start_row = max(1, min(start_row, self.height - GLYPH_HEIGHT - 1))

        def stamp_digit(
            digit: list[list[int]], digit_start_col: int
        ) -> None:
            for pixel_row, pixel_cols in enumerate(digit):
                for pixel_col, is_filled in enumerate(pixel_cols):
                    if is_filled:
                        col = digit_start_col + pixel_col
                        row = start_row + pixel_row
                        if 0 <= col < self.width and 0 <= row < self.height:
                            self.forty_two_cells.add((col, row))

        stamp_digit(DIGIT_4, start_col)
        stamp_digit(DIGIT_2, start_col + GLYPH_WIDTH + GLYPH_GAP)

        # Seal all "42" cells immediately
        for (col, row) in self.forty_two_cells:
            self.grid[row][col] = 0xF

    def _carve_with_dfs(self) -> None:
        """Create maze paths using a stack (DFS)."""

        visited = set(self.forty_two_cells)

        start_col, start_row = self.entry
        stack = [(start_col, start_row)]
        visited.add((start_col, start_row))

        while stack:

            col, row = stack[-1]

            neighbours = []

            for direction in ALL_DIRECTIONS:
                dx, dy = STEP[direction]
                new_col = col + dx
                new_row = row + dy

                inside = (
                    0 <= new_col < self.width and
                    0 <= new_row < self.height
                )

                if inside and (new_col, new_row) not in visited:
                    if not self._is_blocked(new_col, new_row):
                        neighbours.append((new_col, new_row, direction))

            if neighbours:
                next_col, next_row, direction = self._rng.choice(neighbours)

                self._open_wall_between(
                    col, row,
                    next_col, next_row,
                    direction
                )

                visited.add((next_col, next_row))
                stack.append((next_col, next_row))

            else:
                stack.pop()

    def _open_wall_between(
        self,
        col_a: int,
        row_a: int,
        col_b: int,
        row_b: int,
        direction_from_a: int,
    ) -> None:
        """Remove the shared wall between two adjacent cells."""
        self.grid[row_a][col_a] &= ~direction_from_a
        self.grid[row_b][col_b] &= ~OPPOSITE_WALL[direction_from_a]

    def _connect_isolated_cell(
        self,
        col: int,
        row: int,
        carved_cells: set[tuple[int, int]],
    ) -> None:
        """Connect a cell that DFS never reached to any carved neighbour."""
        for direction in ALL_DIRECTIONS:
            delta_col, delta_row = STEP[direction]
            neighbour_col = col + delta_col
            neighbour_row = row + delta_row
            neighbour_is_carved = (
                0 <= neighbour_col < self.width
                and 0 <= neighbour_row < self.height
                and (neighbour_col, neighbour_row) in carved_cells
                and not self._is_blocked(neighbour_col, neighbour_row)
            )
            if neighbour_is_carved:
                self._open_wall_between(
                    col, row, neighbour_col, neighbour_row, direction
                )
                carved_cells.add((col, row))
                return

    # ----------------------------------------------------------
    # Private - post-carving fixes
    # ----------------------------------------------------------

    def _punch_extra_openings(self) -> None:
        """Open extra walls to create loops (used when perfect=False)."""
        number_of_extra_openings = max(1, (self.width * self.height) // 7)
        for _ in range(number_of_extra_openings):
            col = self._rng.randint(0, self.width - 2)
            row = self._rng.randint(0, self.height - 2)
            direction = self._rng.choice([EAST, SOUTH])
            delta_col, delta_row = STEP[direction]
            neighbour_col = col + delta_col
            neighbour_row = row + delta_row
            both_free = (
                not self._is_blocked(col, row)
                and not self._is_blocked(neighbour_col, neighbour_row)
            )
            if both_free:
                self._open_wall_between(
                    col, row, neighbour_col, neighbour_row, direction
                )

    def _seal_outer_border(self) -> None:
        """Close all walls that face outside the maze."""
        for col in range(self.width):
            self.grid[0][col] |= NORTH                  # top row
            self.grid[self.height - 1][col] |= SOUTH    # bottom row
        for row in range(self.height):
            self.grid[row][0] |= WEST                   # left col
            self.grid[row][self.width - 1] |= EAST      # right col

    def _open_entry_and_exit(self) -> None:
        """Open the outward-facing wall of the entry and exit cells."""
        entry_col, entry_row = self.entry
        exit_col, exit_row = self.exit
        entry_border_wall = self._outward_border_direction(entry_col, entry_row)
        exit_border_wall = self._outward_border_direction(exit_col, exit_row)
        if entry_border_wall:
            self.grid[entry_row][entry_col] &= ~entry_border_wall
        if exit_border_wall:
            self.grid[exit_row][exit_col] &= ~exit_border_wall

    def _outward_border_direction(self, col: int, row: int) -> int:
        """Return which direction faces outward for a border cell.

        Returns 0 if the cell is not on any border.
        """
        if row == 0:
            return NORTH
        if row == self.height - 1:
            return SOUTH
        if col == 0:
            return WEST
        if col == self.width - 1:
            return EAST
        return 0

    def _fix_wall_mismatches(self) -> None:
        """Make sure neighbouring cells always agree on their shared wall.

        Example: if cell A has its East wall closed, cell B (to its right)
        must also have its West wall closed.
        """
        for row in range(self.height):
            for col in range(self.width):

                # Check East/West pair with the right neighbour
                if col + 1 < self.width:
                    a_has_east = bool(self.grid[row][col] & EAST)
                    b_has_west = bool(self.grid[row][col + 1] & WEST)
                    if a_has_east != b_has_west:
                        self.grid[row][col] |= EAST
                        self.grid[row][col + 1] |= WEST

                # Check South/North pair with the cell below
                if row + 1 < self.height:
                    a_has_south = bool(self.grid[row][col] & SOUTH)
                    b_has_north = bool(self.grid[row + 1][col] & NORTH)
                    if a_has_south != b_has_north:
                        self.grid[row][col] |= SOUTH
                        self.grid[row + 1][col] |= NORTH

    # ----------------------------------------------------------
    # Private - pathfinding
    # ----------------------------------------------------------

    def _find_shortest_path(self) -> list[str]:
        """Find the shortest path from entry to exit using BFS.

        Returns:
            List of direction letters e.g. ["N", "E", "E", "S"].
            Empty list if no path exists.
        """
        start = self.entry
        goal = self.exit

        if start == goal:
            return []

        queue: collections.deque[tuple[int, int]] = collections.deque([start])
        came_from: dict[
            tuple[int, int],
            Optional[tuple[int, int, int]]
        ] = {start: None}

        while queue:
            current_col, current_row = queue.popleft()
            if (current_col, current_row) == goal:
                break
            for direction in ALL_DIRECTIONS:
                # Can only move if the wall is open
                if self.grid[current_row][current_col] & direction:
                    continue
                delta_col, delta_row = STEP[direction]
                next_col = current_col + delta_col
                next_row = current_row + delta_row
                next_cell_valid = (
                    0 <= next_col < self.width
                    and 0 <= next_row < self.height
                    and (next_col, next_row) not in came_from
                )
                if next_cell_valid:
                    came_from[(next_col, next_row)] = (
                        current_col, current_row, direction
                    )
                    queue.append((next_col, next_row))

        # Rebuild path by walking backwards from goal to start
        if goal not in came_from:
            return []

        path: list[str] = []
        current = goal
        while came_from[current] is not None:
            prev_col, prev_row, direction = came_from[current]  # type: ignore
            path.append(DIR_TO_LETTER[direction])
            current = (prev_col, prev_row)
        path.reverse()
        return path
