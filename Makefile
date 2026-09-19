.PHONY: install test app api docker research

install:
	python -m pip install -r requirements-dev.txt

test:
	PYTHONPATH=src python -m pytest -q

app:
	PYTHONPATH=src streamlit run app.py

api:
	PYTHONPATH=src uvicorn api.main:app --reload

docker:
	docker compose up --build

research:
	PYTHONPATH=src python scripts/build_research_cohort.py --out data/research
