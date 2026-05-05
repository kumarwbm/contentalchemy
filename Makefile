.PHONY: install run test clean

install:
	python3 -m venv venv
	. venv/bin/activate && pip install -r requirements.txt

run:
	. venv/bin/activate && PYTHONPATH=. streamlit run src/web_app/app.py

test:
	. venv/bin/activate && PYTHONPATH=. pytest tests/ -v

clean:
	rm -rf venv __pycache__ .pytest_cache
