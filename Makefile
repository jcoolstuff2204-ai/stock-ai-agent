.PHONY: install test lint typecheck run signals health

install:
	python -m pip install -e ".[dev]"

test:
	pytest -q

lint:
	ruff check src tests

typecheck:
	mypy src

run:
	streamlit run streamlit_app.py

signals:
	quantrade generate-signals

health:
	quantrade health-check

