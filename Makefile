.PHONY: install run debug clean lint lint-strict
 
install:
	python -m poetry install
 
run:
	python -m poetry run python3 a_maze_ing.py
 
debug:
	python -m pdb a_maze_ing.py
 
clean:
	rm -rf __pycache__ .mypy_cache .pytest_cache
	rm -rf mazegen/__pycache__
	rm -f *.pyc *.pyo
 
lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
