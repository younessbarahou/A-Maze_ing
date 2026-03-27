from collections import deque
from maze_loader import WALL_NORTH, WALL_EAST, WALL_SOUTH, WALL_WEST

DIRECTIONS = [
    ("N", 0, -1, WALL_NORTH),
    ("E", 1, 0, WALL_EAST),
    ("S", 0, 1, WALL_SOUTH),
    ("W", -1, 0, WALL_WEST),
]


def bfs_solve(maze):
    start = maze.entry
    goal = maze.exit

    queue = deque([start])
    visited = set([start])
    parent = {start: None}

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


def build_path(parent, goal):
    path = []
    current = goal

    while current is not None:
        path.append(current)
        current = parent[current]

    path.reverse()
    return path


def path_to_directions(path):
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
