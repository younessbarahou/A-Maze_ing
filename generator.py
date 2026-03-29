from typing import Optional
from sys import stderr
from random import seed, choice, randint


class Cell:
    def __init__(self) -> None:
        self.north: bool = True
        self.east: bool = True
        self.west: bool = True
        self.south: bool = True
        self.entry: bool = False
        self.exit: bool = False
        self.reserved_42: bool = False
        self.visited: bool = False


class Maze:
    def __init__(self, rows: int, columns: int) -> None:
        self.rows = rows
        self.columns = columns
        self.maze_rep: list[list] = []

    def grid_setup(self) -> list[list]:
        index: int = 0
        while index < self.rows:
            jndex: int = 0
            row: list = []
            while jndex < self.columns:
                temp: Cell = Cell()
                row.append(temp)
                jndex += 1
            self.maze_rep.append(row)
            index += 1
        return self.maze_rep


""" To generate a maze , use the generate_maze() method """


class MazeGenerator:
    def __init__(
        self,
        height: int,
        width: int,
        entry: tuple,
        exitt: tuple,
        output_file: str,
        perfect: bool,
        seed: Optional[int] = None
    ) -> None:
        self.height = height
        self.width = width
        self.entry = entry
        self.exit = exitt
        self.o_file = output_file
        self.perfect = perfect
        self.Seed = seed

    def to_hexa(self, maze_grid: list[list]) -> list[list]:
        hexa_present: str = "0123456789ABCDEF"
        result: str = ""
        for row in maze_grid:
            for cell in row:
                north: int = 1 if cell.north else 0
                east: int = 2 if cell.east is True else 0
                south: int = 4 if cell.south is True else 0
                west: int = 8 if cell.west is True else 0
                result += hexa_present[north + east + south + west]
            result += '\n'
        return result

    def check_borders(self) -> None:
        if (
            self.entry[0] < 0
            or self.entry[1] < 0
            or self.entry[0] >= self.height
            or self.entry[1] >= self.width
        ):
            raise ValueError("entry coordinates out of maze bond!")
        if (
            self.exit[0] < 0
            or self.exit[1] < 0
            or self.exit[0] >= self.height
            or self.exit[1] >= self.width
        ):
            raise ValueError("exit coordinates out of maze bond!")

    def mark_42(self, maze_grid: list[list]) -> list[list] | None:
        if self.height < 12 or self.width < 12:
            print(
                "42 Pattern is omitted!\n maze size is too small.",
                file=stderr
            )
        else:
            maze_grid[2][2].reserved_42 = True
            maze_grid[3][2].reserved_42 = True
            maze_grid[4][2].reserved_42 = True
            maze_grid[4][3].reserved_42 = True
            maze_grid[4][4].reserved_42 = True
            maze_grid[5][4].reserved_42 = True
            maze_grid[6][4].reserved_42 = True
            maze_grid[2][6].reserved_42 = True
            maze_grid[2][7].reserved_42 = True
            maze_grid[2][8].reserved_42 = True
            maze_grid[3][8].reserved_42 = True
            maze_grid[4][8].reserved_42 = True
            maze_grid[4][7].reserved_42 = True
            maze_grid[4][6].reserved_42 = True
            maze_grid[5][6].reserved_42 = True
            maze_grid[6][6].reserved_42 = True
            maze_grid[6][7].reserved_42 = True
            maze_grid[6][8].reserved_42 = True
            return maze_grid

    """ makes the perfect maze imperfect """
    def make_imperfect(
        self, maze_grid: list[list],
        rows: int, columns: int
    ) -> None:
        """ we get the 10% of a grid """
        ten_percent = (rows * columns) // 10
        while ten_percent > 0:
            """ we select random cell """
            rand_row = randint(0, rows - 2)
            rand_col = randint(0, columns - 2)
            east = maze_grid[rand_row][rand_col].east
            south = maze_grid[rand_row][rand_col].south
            if east:
                maze_grid[rand_row][rand_col].east = False
                maze_grid[rand_row][rand_col + 1].west = False
            elif south:
                maze_grid[rand_row][rand_col].south = False
                maze_grid[rand_row + 1][rand_col].north = False
            ten_percent -= 1
    """ Main method for maze generation """
    def generate_maze(self) -> None:
        if self.Seed:
            seed(self.Seed)
        sample_maze: Maze = Maze(self.height, self.width)
        maze_grid: list[dict] = sample_maze.grid_setup()
        """ mark the 42 cells """
        marked: list[list] | None = self.mark_42(maze_grid)
        if marked is not None:
            maze_grid = marked
        """ checking if entry | exit are out of maze borders """
        self.check_borders()
        """ check if entry | exit are in the 42 pattern """
        if maze_grid[self.entry[0]][self.entry[1]].reserved_42 is True:
            raise ValueError("Entry coordinates are in 42 pattern!")
        if maze_grid[self.exit[0]][self.exit[1]].reserved_42 is True:
            raise ValueError("Exit coordinates are in 42 pattern!")
        """ mark the entry cell """
        maze_grid[self.entry[0]][self.entry[1]].entry = True
        """ mark the exit cell """
        maze_grid[self.exit[0]][self.exit[1]].exit = True
        """ starting the implementation of dfs algorithm """
        base_row: int = 0
        base_column: int = 0
        stack_holder: list = [(base_row, base_column)]
        maze_grid[stack_holder[0][0]][stack_holder[0][1]].visited = True
        while stack_holder:
            north: tuple = None
            east: tuple = None
            west: tuple = None
            south: tuple = None
            row = stack_holder[-1][0]
            column = stack_holder[-1][1]
            north_check = (
                row - 1 >= 0 and
                maze_grid[row - 1][column].visited is False and
                maze_grid[row - 1][column].reserved_42 is False
            )
            south_check = (
                row + 1 < self.height and
                maze_grid[row + 1][column].visited is False and
                maze_grid[row + 1][column].reserved_42 is False
            )
            east_check = (
                column + 1 < self.width and
                maze_grid[row][column + 1].visited is False and
                maze_grid[row][column + 1].reserved_42 is False
            )
            west_check = (
                column - 1 >= 0 and
                maze_grid[row][column - 1].visited is False and
                maze_grid[row][column - 1].reserved_42 is False
            )
            if north_check or south_check or west_check or east_check:
                if north_check:
                    north = (row - 1, column)
                if south_check:
                    south = (row + 1, column)
                if west_check:
                    west = (row, column - 1)
                if east_check:
                    east = (row, column + 1)
                possible_dir: list = [north, south, east, west]
                """ filter the non-None directions """
                possible_dir = [p for p in possible_dir if p is not None]
                decision = choice(possible_dir)
                """ Walls destructing """
                if decision == north:
                    maze_grid[row][column].north = False
                    maze_grid[decision[0]][decision[1]].south = False
                    maze_grid[decision[0]][decision[1]].visited = True
                elif decision == south:
                    maze_grid[row][column].south = False
                    maze_grid[decision[0]][decision[1]].north = False
                    maze_grid[decision[0]][decision[1]].visited = True
                elif decision == east:
                    maze_grid[row][column].east = False
                    maze_grid[decision[0]][decision[1]].west = False
                    maze_grid[decision[0]][decision[1]].visited = True
                elif decision == west:
                    maze_grid[row][column].west = False
                    maze_grid[decision[0]][decision[1]].east = False
                    maze_grid[decision[0]][decision[1]].visited = True
                stack_holder.append(decision)
            else:
                stack_holder.pop()
        if self.perfect is False:
            self.make_imperfect(maze_grid, self.height, self.width)
        with open(self.o_file, 'w') as file:
            file.write(self.to_hexa(maze_grid))
            file.write('\n')
            file.write(f"{self.entry[0]},{self.entry[1]}\n")
            file.write(f"{self.exit[0]},{self.exit[1]}\n")
