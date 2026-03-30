import os
import random
from typing import List, Dict, Tuple, Optional
from parsing import parser
from mazegen.generator import MazeGenerator
from maze_loader import load_maze, Maze
from maze_solver import bfs_solve, path_to_directions
from maze_output import build_grid


# Colors
RESET = "\033[0m"


def fg(r: int, g: int, b: int) -> str:
    """Returns an ANSI escape sequence string to
    set the foreground (text) color.

    Args:
        r (int): Red component (0-255).
        g (int): Green component (0-255).
        b (int): Blue component (0-255).

    Returns:
        str: ANSI escape sequence for the specified foreground color.
    """
    return "\033[38;2;{};{};{}m".format(r, g, b)


def bg(r: int, g: int, b: int) -> str:
    """Returns an ANSI escape sequence string to set the background color.

    Args:
        r (int): Red component (0-255).
        g (int): Green component (0-255).
        b (int): Blue component (0-255).

    Returns:
        str: ANSI escape sequence for the specified background color.
    """
    return "\033[48;2;{};{};{}m".format(r, g, b)


def clear() -> None:
    """Clears the terminal screen using the system's clear command.

    This function works on Unix-like systems where the 'clear'
    command is available.

    Returns:
        None
    """
    os.system("clear")


THEMES: List[Dict[str, Tuple[int, int, int] | str]] = [
    {
        "name": "Blue",
        "wall": (30, 30, 80),
        "empty": (10, 10, 30),
        "path": (100, 200, 255),
        "entry": (80, 255, 120),
        "exit": (255, 100, 100),
    },
    {
        "name": "Red",
        "wall": (80, 20, 0),
        "empty": (20, 5, 0),
        "path": (255, 180, 50),
        "entry": (100, 255, 100),
        "exit": (50, 150, 255),
    },
    {
        "name": "Green",
        "wall": (20, 60, 20),
        "empty": (5, 20, 5),
        "path": (150, 255, 100),
        "entry": (255, 230, 50),
        "exit": (255, 80, 80),
    },
]


def render_maze(
        maze: Maze,
        theme_index: int,
        show_path: bool,
        path: Optional[List[tuple[int, int]]]
) -> str:
    """Renders the maze as a string with colors and optional solution path.

    Args:
        maze (Maze): The maze object to render.
        theme_index (int): Index of the color THEMES.
        show_path (bool): Whether to display the solution path in the maze.
        path (Optional[List[tuple[int, int]]]): coordinates representing
            the solution path. Ignored if `show_path` is False.

    Returns:
        str: A string representation of the maze with ANSI color codes applied.
    """
    theme = THEMES[theme_index]

    if show_path:
        grid = build_grid(maze, path)
    else:
        grid = build_grid(maze, None)

    result = ""

    for row in grid:
        for cell in row:

            if cell == "█":
                result += fg(*theme["wall"]) + bg(*theme["wall"]) + "██"

            elif cell == "E":
                result += fg(*theme["entry"]) + bg(*theme["empty"]) + "EN"

            elif cell == "X":
                result += fg(*theme["exit"]) + bg(*theme["empty"]) + "EX"

            elif cell == "•":
                result += fg(*theme["path"]) + bg(*theme["empty"]) + "··"

            else:
                result += fg(*theme["empty"]) + bg(*theme["empty"]) + "  "

            result += RESET

        result += "\n"

    return result


def print_menu() -> None:
    """Prints the main menu options for the maze program.

    The menu includes options to regenerate the maze, toggle path display,
    change the maze color theme, or quit the program.

    Returns:
        None
    """
    print("-" * 40)
    print("  1. Regenerate maze")
    print("  2. Show / Hide path")
    print("  3. Change maze color")
    print("  4. Quit")


def main() -> None:
    """Main entry point for the maze program.

    Handles:
        - Loading configuration from 'config.txt'.
        - Generating the maze and saving it to a file.
        - Solving the maze using BFS and recording the directions.
        - Displaying the maze in the terminal with optional color themes.
        - Interactive menu for regenerating the maze, toggling the path,
          changing colors, or quitting.

    Returns:
        None
    """
    maze_confg = parser("config.txt")
    maze_obj = MazeGenerator(
        height=maze_confg.Height,
        width=maze_confg.Width,
        entry=maze_confg.Entry,
        exitt=maze_confg.Exit,
        output_file=maze_confg.Output_file,
        perfect=maze_confg.Perfect,
        SEED=maze_confg.SEED
    )
    maze_obj.generate_maze()
    maze_file = "output.txt"
    show_path = False

    # Find saved theme index
    theme_index = 0
    saved_theme = ""

    for i in range(len(THEMES)):
        if THEMES[i]["name"] == saved_theme:
            theme_index = i
            break

    maze = load_maze(maze_file)
    path = bfs_solve(maze) or []

    directions = path_to_directions(path)

    with open(maze_file, 'a') as f:
        f.write('\n' + directions + '\n')
    while True:
        clear()
        print(render_maze(maze, theme_index, show_path, path))

        print_menu()

        choice = input("Choose [1-4]: ")

        # 1. Regenerate
        if choice == "1":
            maze_obj.generate_maze()
            maze = load_maze(maze_file)
            path = bfs_solve(maze) or []
            directions = path_to_directions(path)
            with open(maze_file, 'a') as f:
                f.write('\n' + directions + '\n')
        # 2. show/hide the path
        elif choice == "2":
            show_path = not show_path

        # 3. Change theme
        elif choice == "3":
            new_index = theme_index
            while new_index == theme_index:
                new_index = random.randint(0, len(THEMES) - 1)
            theme_index = new_index

        elif choice == "4":
            clear()
            print("\nGoodbye!\n")
            break


if __name__ == "__main__":
    main()
