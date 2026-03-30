.PHONY: install run debug clean lint lint-strict
 
install:
	pip install -r requirements.txt
 
run:
	python3 main.py
 
debug:
	python -m pdb main.py
 
clean:
	rm -rf __pycache__ .mypy_cache .pytest_cache
	rm -rf mazegen/__pycache__
	rm -f *.pyc *.pyo
 
lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
