"""
Terminal ASCII renderer for A-Maze-ing.

Draws the maze using box-drawing characters and ANSI colors.

Layout (each cell = 2 chars wide, 1 line tall):

    +--+--+--+
    |  |     |    <- west wall (|) + 2-char cell interior
    +--+  +--+
    |        |
    +--+--+--+

Path connections: the wall SLOT between two consecutive path cells
is colored the same as path cells, making the route one continuous line.
"""

import os
import sys
from typing import Optional

from gene import MazeGenerator
from gene import NORTH, EAST, SOUTH, WEST, STEP


# ------------------------------------------------------------------
# ANSI color helpers
# ------------------------------------------------------------------

def set_fg(color_code: int) -> str:
    """Return ANSI escape to set foreground color (256-color mode)."""
    return f"\033[38;5;{color_code}m"


def set_bg(color_code: int) -> str:
    """Return ANSI escape to set background color (256-color mode)."""
    return f"\033[48;5;{color_code}m"


RESET_STYLE = "\033[0m"


# ------------------------------------------------------------------
# Color palette definitions
# ------------------------------------------------------------------

# Each palette: (wall_fg, wall_bg, empty_cell_bg)
COLOR_PALETTES: list[tuple[int, int, int]] = [
    (15, 235, 232),    # Default : white walls, dark-grey, black cells
    (220, 52, 232),    # Gold    : gold walls,  dark-red,  black cells
    (46, 22, 232),     # Green   : green walls, dark-green, black cells
    (39, 17, 232),     # Blue    : cyan walls,  navy,       black cells
    (201, 53, 232),    # Magenta : pink walls,  purple,     black cells
]

PALETTE_NAMES = ["Default", "Gold", "Green", "Blue", "Magenta"]

# Special cell colors
PATH_CELL_BG = 226    # bright yellow - solution path
ENTRY_CELL_BG = 28    # green         - entry cell
EXIT_CELL_BG = 160    # red           - exit cell
GLYPH_CELL_BG = 55    # indigo        - "42" cells


# ------------------------------------------------------------------
# Path tracing
# ------------------------------------------------------------------

def trace_solution_path(
    gen: MazeGenerator,
) -> tuple[set[tuple[int, int]], set[tuple[int, int, int, int]]]:
    """Walk the solution and return which cells and edges are on the path.

    Returns:
        path_cells: set of (col, row) on the solution.
        path_edges: set of (col_a, row_a, col_b, row_b) for each step,
                    stored in both directions for easy lookup.
    """
    path_cells: set[tuple[int, int]] = set()
    path_edges: set[tuple[int, int, int, int]] = set()

    if not gen.solution:
        return path_cells, path_edges

    letter_to_direction = {"N": NORTH, "E": EAST, "S": SOUTH, "W": WEST}

    current_col, current_row = gen.entry
    path_cells.add((current_col, current_row))

    for letter in gen.solution:
        direction = letter_to_direction[letter]
        delta_col, delta_row = STEP[direction]
        next_col = current_col + delta_col
        next_row = current_row + delta_row

        path_cells.add((next_col, next_row))
        # Store edge in both directions so we can look it up from either side
        path_edges.add((current_col, current_row, next_col, next_row))
        path_edges.add((next_col, next_row, current_col, current_row))

        current_col, current_row = next_col, next_row

    return path_cells, path_edges


# ------------------------------------------------------------------
# Cell color helpers
# ------------------------------------------------------------------

def get_cell_bg_color(
    col: int,
    row: int,
    gen: MazeGenerator,
    path_cells: set[tuple[int, int]],
    show_path: bool,
    empty_cell_bg: int,
) -> int:
    """Return the background color for a cell's interior."""
    if (col, row) == gen.entry:
        return ENTRY_CELL_BG
    if (col, row) == gen.exit:
        return EXIT_CELL_BG
    if show_path and (col, row) in path_cells:
        return PATH_CELL_BG
    if (col, row) in gen.forty_two_cells:
        return GLYPH_CELL_BG
    return empty_cell_bg


def get_cell_label(col: int, row: int, gen: MazeGenerator) -> str:
    """Return the 2-character text shown inside a cell."""
    if (col, row) == gen.entry:
        return "EN"
    if (col, row) == gen.exit:
        return "EX"
    return "  "


def get_north_gap_bg(
    col: int,
    row: int,
    path_edges: set[tuple[int, int, int, int]],
    show_path: bool,
    empty_cell_bg: int,
) -> int:
    """Background for the gap slot between this cell and the one above.

    Used to draw the path crossing a North/South wall opening.
    """
    if show_path and (col, row, col, row - 1) in path_edges:
        return PATH_CELL_BG
    return empty_cell_bg


def get_west_gap_bg(
    col: int,
    row: int,
    path_edges: set[tuple[int, int, int, int]],
    show_path: bool,
    empty_cell_bg: int,
) -> int:
    """Background for the gap slot between this cell and the one to the left.

    Used to draw the path crossing an East/West wall opening.
    """
    if show_path and (col, row, col - 1, row) in path_edges:
        return PATH_CELL_BG
    return empty_cell_bg


# ------------------------------------------------------------------
# Main renderer
# ------------------------------------------------------------------

def render_maze(
    gen: MazeGenerator,
    show_path: bool = False,
    palette_index: int = 0,
) -> list[str]:
    """Build a list of colored terminal lines representing the maze.

    Each row of cells produces two terminal lines:
        - Top border line : corner (+) + north wall (━━) or open gap
        - Body line       : west wall (|) or gap  + 2-char cell interior

    One final south border line closes the maze at the bottom.

    The path is drawn by coloring the wall slot between consecutive
    path cells, making the route look like one continuous colored line.

    Args:
        gen:           Generated MazeGenerator instance.
        show_path:     Whether to highlight the solution path.
        palette_index: Which color palette to use (0-4).

    Returns:
        List of strings, one per terminal line.
    """
    wall_fg, wall_bg, empty_cell_bg = (
        COLOR_PALETTES[palette_index % len(COLOR_PALETTES)]
    )
    wall_style = f"{set_fg(wall_fg)}{set_bg(wall_bg)}"

    path_cells: set[tuple[int, int]] = set()
    path_edges: set[tuple[int, int, int, int]] = set()
    if show_path:
        path_cells, path_edges = trace_solution_path(gen)

    terminal_lines: list[str] = []

    for row in range(gen.height):

        # Top border line for this row
        top_line = ""
        for col in range(gen.width):
            top_line += f"{wall_style}+{RESET_STYLE}"
            if gen.grid[row][col] & NORTH:
                top_line += f"{wall_style}━━{RESET_STYLE}"
            else:
                gap_bg = get_north_gap_bg(
                    col, row, path_edges, show_path, empty_cell_bg
                )
                top_line += f"{set_bg(gap_bg)}  {RESET_STYLE}"
        top_line += f"{wall_style}+{RESET_STYLE}"
        terminal_lines.append(top_line)

        # Cell body line
        body_line = ""
        for col in range(gen.width):
            # West wall or open gap
            if gen.grid[row][col] & WEST:
                body_line += f"{wall_style}┃{RESET_STYLE}"
            else:
                gap_bg = get_west_gap_bg(
                    col, row, path_edges, show_path, empty_cell_bg
                )
                body_line += f"{set_bg(gap_bg)} {RESET_STYLE}"
            # Cell interior (2 characters)
            cell_bg = get_cell_bg_color(
                col, row, gen, path_cells, show_path, empty_cell_bg
            )
            cell_label = get_cell_label(col, row, gen)
            body_line += f"{set_bg(cell_bg)}{cell_label}{RESET_STYLE}"

        # Rightmost east wall of this row
        if gen.grid[row][gen.width - 1] & EAST:
            body_line += f"{wall_style}┃{RESET_STYLE}"
        else:
            gap_bg = get_west_gap_bg(
                gen.width, row, path_edges, show_path, empty_cell_bg
            )
            body_line += f"{set_bg(gap_bg)} {RESET_STYLE}"
        terminal_lines.append(body_line)

    # Final south border line
    south_border = ""
    for col in range(gen.width):
        south_border += f"{wall_style}+{RESET_STYLE}"
        if gen.grid[gen.height - 1][col] & SOUTH:
            south_border += f"{wall_style}━━{RESET_STYLE}"
        else:
            gap_bg = get_north_gap_bg(
                col, gen.height, path_edges, show_path, empty_cell_bg
            )
            south_border += f"{set_bg(gap_bg)}  {RESET_STYLE}"
    south_border += f"{wall_style}+{RESET_STYLE}"
    terminal_lines.append(south_border)

    return terminal_lines


# ------------------------------------------------------------------
# Print helpers
# ------------------------------------------------------------------

def print_maze(
    gen: MazeGenerator,
    show_path: bool = False,
    palette_index: int = 0,
) -> None:
    """Clear the screen and print the maze with a status bar."""
    os.system("clear")
    for line in render_maze(gen, show_path=show_path, palette_index=palette_index):
        print(line)

    path_status = "ON" if show_path else "OFF"
    palette_name = PALETTE_NAMES[palette_index % len(PALETTE_NAMES)]
    forty_two_status = (
        "42 embedded" if gen.has_forty_two else "no 42 (maze too small)"
    )
    print()
    print(
        f"  Seed: {gen.seed}  |  Path: {path_status}  |  "
        f"Colour: {palette_name}  |  {forty_two_status}"
    )


# ------------------------------------------------------------------
# Interactive menu
# ------------------------------------------------------------------

def interactive_loop(
    gen: MazeGenerator,
    config: dict[str, object],
) -> None:
    """Show the maze and let the user interact via a numbered menu.

    Menu options:
        1 - Re-generate a new maze
        2 - Show / Hide the solution path
        3 - Change wall colour
        4 - Quit

    Args:
        gen:    An already-generated MazeGenerator instance.
        config: Dict with keys width, height, entry, exit,
                output_file, perfect (provided by the config parser).
    """
    show_path = False
    palette_index = 0
    current_seed: Optional[int] = gen.seed

    print_maze(gen, show_path=show_path, palette_index=palette_index)

    while True:
        print()
        print("==== A-Maze-ing ====")
        print("1. Re-generate a new maze")
        print("2. Show/Hide path from entry to exit")
        print("3. Change wall colour")
        print("4. Quit")

        choice = input("Choice (1-4): ").strip()

        if choice == "1":
            if current_seed is not None:
                current_seed += 1
            new_gen = MazeGenerator(
                width=int(str(config["width"])),
                height=int(str(config["height"])),
                seed=current_seed,
                perfect=bool(config["perfect"]),
            )
            try:
                new_gen.generate(
                    entry=config["entry"],   # type: ignore[arg-type]
                    exit_=config["exit"],    # type: ignore[arg-type]
                )
                gen = new_gen
            except (ValueError, RuntimeError) as error:
                print(f"[Error] {error}", file=sys.stderr)
            print_maze(gen, show_path=show_path, palette_index=palette_index)

        elif choice == "2":
            show_path = not show_path
            print_maze(gen, show_path=show_path, palette_index=palette_index)

        elif choice == "3":
            palette_index = (palette_index + 1) % len(COLOR_PALETTES)
            print_maze(gen, show_path=show_path, palette_index=palette_index)

        elif choice == "4":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please enter 1, 2, 3 or 4.")