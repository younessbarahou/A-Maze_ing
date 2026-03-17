from parsing import parser, Config
from pydantic import ValidationError
from sys import argv


def main() -> None:
    try:
        if len(argv) == 2:
            parsed_data: Config = parser(argv[1])
            print(parsed_data)
            # data_config = MazeGenerator(width=20, height=15, seed=42, perfect=True)
            # gen.generate(entry=(0, 0), exit_=(19, 14))

            # interactive_loop(gen, {
            #     "width": 20,
            #     "height": 15,
            #     "entry": (0, 0),
            #     "exit": (19, 14),
            #     "output_file": "maze.txt",
            #     "perfect": True,
            # })
        else:
            print("Program Should receive One Filename !")
            print("Hint =>")
            print("python3 a_maze_ing.py <filename>")
    except FileNotFoundError:
        print("File Not Found !")
    except ValidationError as e:
        print(e.errors()[0]['msg'])
    except PermissionError:
        print("file lakes permission !")
    except ValueError as e:
        print(f"{e}")


if __name__ == "__main__":
    main()
