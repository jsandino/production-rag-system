# --- local dev ---
.PHONY: install format lint test test-all test-int eval

install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt
	
format:
	ruff format .

lint:
	ruff check .
	pylint shared/shared
	$(MAKE) -C services/ingestion-service lint
	$(MAKE) -C services/query-service lint
	
test:
	pytest || true

test-all:
	pytest shared/
	$(MAKE) -C services/ingestion-service test
	$(MAKE) -C services/query-service test

test-int:
	$(MAKE) -C services/ingestion-service test-int
	$(MAKE) -C services/query-service test-int

eval:
	docker compose -f docker-compose.eval.yml up --build -d --wait && \
	    INGESTION_URL=http://localhost:8002 QUERY_URL=http://localhost:8003 \
	    python eval/run_eval.py; \
	    EXIT_CODE=$$?; \
	    docker compose -f docker-compose.eval.yml down; \
	    exit $$EXIT_CODE

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
.PHONY: prom grafana

prom:
	open http://localhost:9090/targets

grafana:
	open http://localhost:3000