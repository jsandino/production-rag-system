# --- local dev ---
.PHONY: install format lint test

install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt
	
format:
	black .
	
lint:
	pylint services
	
test:
	pytest || true

# --- docker orchestration ---
.PHONY: docker-up docker-down docker-reset docker-db docker-ingest docker-query

docker-up:
	docker compose up --build

docker-down:
	docker compose down

docker-reset:
	docker compose down -v && docker compose up --build

docker-db:
	docker exec -it rag-postgres psql -U user -d ragdb

docker-ingest:
	curl -X POST http://localhost:8000/ingest \
		-H "Content-Type: application/json" \
		-d '{"document_name": "smoke_test.txt", "text": "Smoke test validating ingest service on Docker.", "metadata": {"source": "root"}}'

docker-query:
	curl -X POST http://localhost:8001/query \
		-H "Content-Type: application/json" \
		-d '{"query": "What is a vector database?", "top_k": 5, "filters": {}, "debug": false}'

# --- local dashboards ---
.PHONY: prom

prom:
	open http://localhost:9090/targets