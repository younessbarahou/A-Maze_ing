WALL = "█"
EMPTY = " "
PATH = "•"
ENTRY = "E"
EXIT = "X"


def build_grid(maze, path=None):
    w = maze.width * 2 + 1
    h = maze.height * 2 + 1

    grid = [[WALL for _ in range(w)] for _ in range(h)]

    # open cells
    for y in range(maze.height):
        for x in range(maze.width):

            rx = x * 2 + 1
            ry = y * 2 + 1

            grid[ry][rx] = EMPTY

            # east
            if x + 1 < maze.width:
                if not (maze.grid[y][x] & 2):
                    grid[ry][rx + 1] = EMPTY

            # south
            if y + 1 < maze.height:
                if not (maze.grid[y][x] & 4):
                    grid[ry + 1][rx] = EMPTY

    # draw path
    if path:
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

    # entry & exit
    ex, ey = maze.entry
    fx, fy = maze.exit

    grid[ey*2+1][ex*2+1] = ENTRY
    grid[fy*2+1][fx*2+1] = EXIT

    return grid


def print_maze(maze, path=None):
    grid = build_grid(maze, path)

    for row in grid:
        print("".join(row))
