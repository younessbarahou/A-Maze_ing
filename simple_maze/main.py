from gene import MazeGenerator
from script import interactive_loop

gen = MazeGenerator(width=20, height=15, seed=42, perfect=True)
gen.generate(entry=(0, 0), exit_=(19, 14))

interactive_loop(gen, {
    "width": 20,
    "height": 15,
    "entry": (0, 0),
    "exit": (19, 14),
    "output_file": "maze.txt",
    "perfect": True,
})
