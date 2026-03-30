*This project has been created as part of the 42 curriculum by <ybarahou>, <mjoukhal>.*


## Description

**A-Maze-ing** is a Python maze generator and solver. Given a configuration file, the program:

1. Generates a random maze using a **Depth-First Search (DFS) recursive backtracker** algorithm.
2. Writes the maze to an output file using a compact hexadecimal wall encoding.
3. Solves the maze using **Breadth-First Search (BFS)** to find the shortest path from entry to exit.
4. Displays the maze visually in the terminal.

The maze may be configured as **perfect** (exactly one path between any two cells) or imperfect (multiple paths allowed). The visual representation always includes a hidden **"42"** pattern drawn by fully closed cells.


## Instructions

### Requirements

- Python **3.10** or later
- `pip` (or `uv`, `pipx`) for dependency management
- `flake8` and `mypy` for linting

### Installation

# Install dependencies
make install
```

### Running the Program

# Run with a configuration file
python3 main.py config.txt

# Or via Makefile
make run
```


## Configuration File

The configuration file is a plain text file with one `KEY=VALUE` pair per line.  
Lines beginning with `#` are treated as comments and ignored.

### Mandatory Keys


| `WIDTH` | Number of cells horizontally | `WIDTH=20` |
| `HEIGHT` | Number of cells vertically | `HEIGHT=15` |
| `ENTRY` | Entry cell coordinates `(x,y)` | `ENTRY=0,0` |
| `EXIT` | Exit cell coordinates `(x,y)` | `EXIT=19,14` |
| `OUTPUT_FILE` | Path of the output maze file | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | Whether to generate a perfect maze | `PERFECT=True` |

### Optional Keys


| `SEED` | Random seed for reproducibility | `SEED=42` 

### Example `config.txt`

```
# A-Maze-ing configuration
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
```

All error cases are handled gracefully: invalid keys, out-of-bounds coordinates, missing mandatory fields, bad types, etc. The program never crashes unexpectedly and always prints a clear error message.

---

## Output File Format

Each cell is encoded as **one hexadecimal digit** where each bit represents a wall:

| Bit | Direction | Value |
|-----|-----------|-------|
| 0 (LSB) | North | 1 |
| 1 | East | 2 |
| 2 | South | 4 |
| 3 (MSB) | West | 8 |

- A **set bit (1)** means the wall is **closed**.
- A **clear bit (0)** means the wall is **open**.

**Example:** `3` = binary `0011` → North and East walls closed, South and West open.  
**Example:** `A` = binary `1010` → East and West walls closed, North and South open.

Cells are written **row by row**, one row per line. After an empty line, three additional lines are appended:

```
<entry_x>,<entry_y>
<exit_x>,<exit_y>
<path: sequence of N/E/S/W directions>
```

### Sample Output

```
ff9f3f9fbf...
0,0
19,14
EESSSSEENNE...
```


## Maze Generation Algorithm

### Algorithm: DFS Recursive Backtracker

We chose the **Depth-First Search (DFS) recursive backtracker** as our generation algorithm.

#### How It Works

1. Initialize the 0,0 in a stack
2. Choose A random valid direction
3. Sets the Current cell's Wall + its parallel as opened
4. Move to the next chosen Cell (push it to the stack)
5. if there are no next valid directions , pop the last item from the stack
6. Keep doing [2->5] until no item left on the stack

#### Why DFS?

- **Guaranteed perfect maze:** DFS visits every cell exactly once, so the result always has exactly one path between any two cells when `PERFECT=True`.
- **Long, winding corridors:** DFS tends to create aesthetically pleasing mazes with long passages and few dead ends.
- **Simple implementation:** The algorithm maps cleanly to a stack-based or recursive approach, making it easy to maintain and reason about.
- **Reproducible via seed:** Using Python's `random.seed()` makes mazes fully reproducible from a given seed.

#### Solving: BFS Shortest Path

The solver uses **Breadth-First Search (BFS)** to guarantee the shortest path from ENTRY to EXIT:

1. Start from ENTRY; add it to a queue.
2. For each cell dequeued, check its open neighbors (no wall between them).
3. Enqueue unvisited neighbors and record their parent.
4. When EXIT is reached, reconstruct the path by following parent pointers back to ENTRY.
5. Convert the path to a sequence of `N`, `E`, `S`, `W` directions.

BFS is optimal for unweighted graphs — it always finds the shortest path, which is what the output file and visual display require.

---

## Reusable Module

The maze generation logic is packaged as a standalone installable Python module:


```python
import MazeGenerator

# Basic usage
gen = MazeGenerator(height=15, width=20, entry=(0, 0), exit=(1, 1), output_file='output.txt', perfect=True, seed=42)

# This will create an output file with the maze generated represented as hexadecimal
gen.generate_maze()


# Access the solution path
path = gen.solution      # List of (x, y) tuples
directions = gen.path_directions()  # List of 'N', 'E', 'S', 'W'




**User interactions (keyboard):**

| Key | Action |
|-----|--------|
| `1` | Re-generate a new maze |
| `2` | Show / Hide the shortest path |
| `3` | Cycle wall colours |
| `4` | Quit |



### roles of each team member

- <ybarahou>: + DFS algorithm implementation for the maze generation
              + Parsing of the config file
              + Format the maze output as hexadecimal representation
- <mjoukhal>: + BFS algorithm implementation for the maze solution path
              + Maze Visualisation + Menu
              + MakeFile
### What Worked Well

- Splitting generation and solving between team members allowed parallel development with a clean interface boundary (the shared grid format).
- The DFS algorithm was straightforward to implement and debug.

### What Could Be Improved

- Integration testing between Person A's generator and Person B's solver could have started earlier.

### Tools Used

- **Git** for version control and collaboration
- **VS Code** with Pylance for type checking
- **mypy** and **flake8** for static analysis and linting

---

## Resources

### Maze Generation & Algorithms

- [Maze Generation Algorithm — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Depth-First Search — Wikipedia](https://en.wikipedia.org/wiki/Depth-first_search)
- [Breadth-First Search — Wikipedia](https://en.wikipedia.org/wiki/Breadth-first_search)
- [Jamis Buck — "Maze Generation: Recursive Backtracking"](https://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracking)
- [Think Labyrinth — Walter D. Pullen](https://www.astrolog.org/labyrnth/algrithm.htm) — comprehensive reference on maze algorithms

### Python & Packaging
- [Python `pydantic` module documentation](https://docs.pydantic.dev/latest/)
- [Python `typing` module documentation](https://docs.python.org/3/library/typing.html)
- [PEP 257 — Docstring Conventions](https://peps.python.org/pep-0257/)
- [Python Packaging User Guide](https://packaging.python.org/en/latest/)
- [mypy documentation](https://mypy.readthedocs.io/)
- [flake8 documentation](https://flake8.pycqa.org/)

### AI Usage

AI tools (Claude, ChatGPT) were used for understanding how we can implement the algorithms to generate and solve the maze.