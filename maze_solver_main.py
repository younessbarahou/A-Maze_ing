"""
maze_solver_main.py - Person B  (interactive terminal version)

Works on Windows, Linux, and Mac — no external libraries needed.

Usage:
    python3 maze_solver_main.py <config_file>

Example:
    python3 maze_solver_main.py config.txt

How the screen refresh works:
    Instead of trying to "clear" the terminal (which doesn't work
    reliably), we track exactly how many lines we printed last time,
    then move the cursor back up that many lines and overwrite them.
    This is the same technique used by tools like pip progress bars.
"""

import sys
import os
import subprocess

from maze_loader import load_maze, MazeLoadError, Maze
from maze_solver  import bfs_solve, path_to_directions
from maze_output  import build_render_grid

PERSON_A_SCRIPT: str = "a_maze_ing.py"

# ── Color themes ──────────────────────────────────────────────────────
THEMES: dict[str, dict[str, str]] = {
    "green": {
        "name":  "Green (classic)",
        "wall":  "\033[32m",
        "path":  "\033[92m",
        "entry": "\033[96m",
        "exit":  "\033[91m",
        "open":  "\033[90m",
        "reset": "\033[0m",
    },
    "blue": {
        "name":  "Blue (ocean)",
        "wall":  "\033[34m",
        "path":  "\033[96m",
        "entry": "\033[93m",
        "exit":  "\033[91m",
        "open":  "\033[90m",
        "reset": "\033[0m",
    },
    "fire": {
        "name":  "Fire (red/yellow)",
        "wall":  "\033[31m",
        "path":  "\033[93m",
        "entry": "\033[96m",
        "exit":  "\033[92m",
        "open":  "\033[90m",
        "reset": "\033[0m",
    },
    "mono": {
        "name":  "Monochrome",
        "wall":  "",
        "path":  "",
        "entry": "",
        "exit":  "",
        "open":  "",
        "reset": "",
    },
}
THEME_KEYS: list[str] = list(THEMES.keys())


# ── Screen writer ─────────────────────────────────────────────────────

class Screen:
    """
    Builds the entire frame as a list of lines, then either:
      - On first draw: prints all lines normally.
      - On redraw:     moves cursor up (by the previous line count)
                       then overwrites every line in place.

    This means old content is OVERWRITTEN, not appended below.
    Works on Windows cmd, PowerShell, Linux, and Mac terminals.
    """

    def __init__(self) -> None:
        self._last_line_count: int = 0

    def draw(self, lines: list[str]) -> None:
        """
        Overwrite the previous frame with new lines.

        Args:
            lines: list of strings to display (no \\n needed).
        """
        out = ""

        if self._last_line_count > 0:
            # Move cursor up to the start of the previous frame
            out += f"\033[{self._last_line_count}A"

        for line in lines:
            # \033[2K  = erase the entire current line
            # \r       = go to start of line
            # then print new content, then newline
            out += f"\033[2K\r{line}\n"

        # If new frame is shorter than old, erase leftover lines
        for _ in range(self._last_line_count - len(lines)):
            out += "\033[2K\r\n"

        sys.stdout.write(out)
        sys.stdout.flush()
        self._last_line_count = len(lines)


# ── Build one complete frame as a list of strings ─────────────────────

def build_frame(
    maze: Maze,
    solution_cells: list[tuple[int, int]] | None,
    show_path: bool,
    theme: dict[str, str],
    message: str,
    is_error: bool,
) -> list[str]:
    """
    Assemble the entire screen content into a list of lines.

    Args:
        maze          : the Maze object
        solution_cells: BFS path cells (or None)
        show_path     : whether to draw the path dots
        theme         : active color theme
        message       : status/error message to show (or "")
        is_error      : True = show ⚠, False = show ✓

    Returns:
        List of strings, one per terminal line.
    """
    WALL_CHAR  = "█"
    PATH_CHAR  = "·"
    ENTRY_CHAR = "E"
    EXIT_CHAR  = "X"

    lines: list[str] = []

    # ── Title ─────────────────────────────────────────────────────────
    lines.append("\033[1m  ╔══════════════════════════╗\033[0m")
    lines.append("\033[1m  ║       MAZE  SOLVER       ║\033[0m")
    lines.append("\033[1m  ╚══════════════════════════╝\033[0m")
    lines.append("")

    # ── Status message ────────────────────────────────────────────────
    if message:
        icon = "⚠  " if is_error else "✓  "
        lines.append(f"  {icon}{message}")
        lines.append("")

    # ── Maze render ───────────────────────────────────────────────────
    cells = solution_cells if show_path else None
    render: list[list[str]] = build_render_grid(maze, cells)

    lines.append("")
    for row_chars in render:
        line = ""
        for ch in row_chars:
            if   ch == WALL_CHAR:  line += theme["wall"]  + ch + theme["reset"]
            elif ch == PATH_CHAR:  line += theme["path"]  + ch + theme["reset"]
            elif ch == ENTRY_CHAR: line += theme["entry"] + ch + theme["reset"]
            elif ch == EXIT_CHAR:  line += theme["exit"]  + ch + theme["reset"]
            else:                  line += theme["open"]  + ch + theme["reset"]
        lines.append(line)
    lines.append("")

    # ── No solution warning ───────────────────────────────────────────
    if solution_cells is None:
        lines.append("  ⚠  This maze has no solution!")
        lines.append("")

    # ── Menu ──────────────────────────────────────────────────────────
    sep = "─" * 42
    path_label = (
        f"ON  ({len(path_to_directions_len(solution_cells))} steps)"
        if show_path and solution_cells else "OFF"
    )
    lines.append(sep)
    lines.append(f"  Maze size     : {maze.width}x{maze.height}")
    lines.append(f"  Solution path : {path_label}")
    lines.append(f"  Color theme   : {theme['name']}")
    lines.append(sep)
    lines.append(f"  [1]  Re-generate maze  (runs {PERSON_A_SCRIPT})")
    lines.append("  [2]  Show / Hide solution path")
    lines.append("  [3]  Change color theme")
    lines.append("  [4]  Quit")
    lines.append(sep)

    return lines


def path_to_directions_len(
    solution_cells: list[tuple[int, int]] | None,
) -> str:
    """Return direction string length as string, or 0."""
    if solution_cells is None:
        return "0"
    return str(len(solution_cells) - 1)


# ── Helpers ───────────────────────────────────────────────────────────

def get_output_file_from_config(config_path: str) -> str:
    """Read OUTPUT_FILE from config.txt, default to maze.txt."""
    try:
        with open(config_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.upper().startswith("OUTPUT_FILE"):
                    parts = line.split("=", 1)
                    if len(parts) == 2:
                        return parts[1].strip()
    except OSError:
        pass
    return "maze.txt"


def load_and_solve(
    maze_file: str,
) -> tuple[Maze, list[tuple[int, int]] | None, str]:
    """Load maze file, solve with BFS, return (maze, path_cells, directions)."""
    maze      = load_maze(maze_file)
    cell_path = bfs_solve(maze)
    if cell_path is None:
        return maze, None, ""
    return maze, cell_path, path_to_directions(cell_path)


def regenerate_maze(config_path: str) -> str:
    """Run Person A's script. Returns '' on success or error message."""
    if not os.path.isfile(PERSON_A_SCRIPT):
        return (
            f"'{PERSON_A_SCRIPT}' not found. "
            "Place Person A's file in the same folder."
        )
    try:
        result = subprocess.run(
            ["python3", PERSON_A_SCRIPT, config_path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            err = (result.stderr or result.stdout).strip()
            return f"Generator failed: {err[:120]}"
    except subprocess.TimeoutExpired:
        return "Generator timed out (30s)."
    except Exception as e:
        return f"Could not run generator: {e}"
    return ""


# ── Main interactive loop ─────────────────────────────────────────────

def run(config_path: str) -> None:
    """Interactive loop: build frame → overwrite screen → read key."""

    maze_file: str = get_output_file_from_config(config_path)
    screen         = Screen()

    show_path:        bool = True
    theme_index:      int  = 0
    maze:             Maze = None
    solution_cells         = None
    direction_string: str  = ""
    message:          str  = ""
    is_error:         bool = False

    # ── First load ────────────────────────────────────────────────────
    err = regenerate_maze(config_path)
    if err:
        message  = f"Generator not available. Loading existing file."
        is_error = False
    else:
        message  = "Maze generated successfully."
        is_error = False

    try:
        maze, solution_cells, direction_string = load_and_solve(maze_file)
    except MazeLoadError as e:
        print(f"\n❌  Could not load maze: {e}")
        print(f"    Make sure '{PERSON_A_SCRIPT}' exists or '{maze_file}' is present.\n")
        sys.exit(1)

    # ── Enable ANSI on Windows ────────────────────────────────────────
    if os.name == "nt":
        os.system("")   # this one-liner enables ANSI escape codes in Windows cmd

    # ── Event loop ────────────────────────────────────────────────────
    while True:

        theme  = THEMES[THEME_KEYS[theme_index]]
        frame  = build_frame(
            maze, solution_cells, show_path,
            theme, message, is_error,
        )
        message  = ""
        is_error = False

        # Draw/overwrite the frame — no history, no scrolling
        screen.draw(frame)

        # Read choice (on the same last line, after menu)
        choice = input("  Choice: ").strip().upper()
        # The input() call adds 1 line — account for it next redraw
        screen._last_line_count += 1

        if choice == "4":
            screen.draw(["", "  Goodbye!", ""])
            break

        elif choice == "1":
            err = regenerate_maze(config_path)
            if err:
                message  = err
                is_error = True
            else:
                try:
                    maze, solution_cells, direction_string = load_and_solve(maze_file)
                    show_path = True
                    message   = "New maze generated successfully."
                    is_error  = False
                except MazeLoadError as e:
                    message  = f"Reload failed: {e}"
                    is_error = True

        elif choice == "2":
            if solution_cells is None:
                message  = "No solution — cannot show path."
                is_error = True
            else:
                show_path = not show_path

        elif choice == "3":
            theme_index = (theme_index + 1) % len(THEME_KEYS)

        else:
            message  = f"Unknown option '{choice}'. Use 1 / 2 / 3 / 4."
            is_error = True


# ── Entry point ───────────────────────────────────────────────────────

def main() -> None:
    if len(sys.argv) < 2:
        print("\nUsage:   python3 maze_solver_main.py <config_file>")
        print("Example: python3 maze_solver_main.py config.txt\n")
        sys.exit(1)
    run(sys.argv[1])


if __name__ == "__main__":
    main()