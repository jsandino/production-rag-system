ROOT_DIR := $(shell git rev-parse --show-toplevel)

# --- local dev ---
.PHONY: lint format test test-int run curl check-db clean-db

lint:
	pylint --rcfile $(ROOT_DIR)/.pylintrc ingestion tests

format:
	$(MAKE) -C $(ROOT_DIR) format

test:
	pytest --ignore=tests/test_integration.py

test-int:
	pytest -m integration -v

run:
	uvicorn ingestion.main:app --reload --reload-dir ingestion --port 8000

curl:
	curl -X POST http://localhost:8000/ingest \
		-H "Content-Type: application/json" \
		-d '{"document_name": "vector_dbs.txt", \
		"text": "A vector database indexes and stores vector embeddings for fast retrieval and similarity search, with capabilities like CRUD operations, metadata filtering, horizontal scaling, and serverless.", \
		"metadata": {"source": "test"}}'

check-db:
	pg_isready

clean-db:
	psql -d rag -c "TRUNCATE documents CASCADE"

# --- docker orchestration ---
.PHONY: docker-up docker-down docker-reset docker-db docker-ingest

docker-up:
	@make -C $(ROOT_DIR) docker-up

docker-down:
	@make -C $(ROOT_DIR) docker-down

docker-reset:
	@make -C $(ROOT_DIR) docker-reset

docker-db:
	@make -C $(ROOT_DIR) docker-db

docker-ingest:
	@make -C $(ROOT_DIR) docker-ingest
