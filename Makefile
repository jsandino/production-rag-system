install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt
	
format:
	black .
	
lint:
	pylint services
	
test:
	pytest || true

docker-up:
	docker compose up --build

docker-down:
	docker compose down

docker-db:
	docker exec -it rag-postgres psql -U user -d ragdb

docker-ingest:
		curl -X POST http://localhost:8000/ingest \
		-H "Content-Type: application/json" \
		-d '{"document_id": "doc1", "text": "Smoke test validating ingest service on Docker.", "metadata": {"source": "root"}}'