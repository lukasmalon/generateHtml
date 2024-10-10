build:
	python -m pip install --upgrade build
	python -m build

test:
	python -m pytest tests/*
	make clean

clean:
	find . -type d \( -name "dist" -o -name "__pycache__" -o -name ".ruff_cache" -o -name ".pytest_cache" \) -exec rm -r {} +
