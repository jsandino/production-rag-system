install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt
	
format:
	black *.py
	
lint:
	pylint --disable=R,C hello.py
	
test:
	python -m pytest

set-ingest:
	pip install -e services/ingestion-service
	
run-ingest:
	cd services/ingestion-service && uvicorn app.main:app --reload --port 8001