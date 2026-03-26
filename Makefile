install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt
	
format:
	black .
	
lint:
	pylint --disable=R,C hello.py
	
test:
	python -m pytest

set-ingest:
	pip install -e services/ingestion-service
	
run-ingest:
	cd services/ingestion-service && uvicorn app.main:app --reload --port 8001
	
curl-ingest:
	curl -X POST http://localhost:8001/ingest \
		-H "Content-Type: application/json" \
		-d '{"document_id": "doc1", "text": "This is a test document.", "metadata": {"source": "test"}}'