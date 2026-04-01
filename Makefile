.PHONY: install run debug clean lint lint-strict
 
install:
	python3 -m poetry install
 
run:
	python3 -m poetry run python3 a_maze_ing.py
 
debug:
	python3 -m pdb a_maze_ing.py

clean:
	rm -rf __pycache__ .mypy_cache .pytest_cache
	rm -rf mazegen/__pycache__
	rm -f *.pyc *.pyo
 
lint:
	python3 -m flake8 .
	python3 -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
