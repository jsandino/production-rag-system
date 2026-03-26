install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt
	
init:
	pip install -e .
	
run:
	uvicorn app.main:app --reload --port 8001
	
curl:
	curl -X POST http://localhost:8001/ingest \
		-H "Content-Type: application/json" \
		-d '{"document_id": "doc1", "text": "This is a test document.", "metadata": {"source": "test"}}'