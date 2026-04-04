ROOT_DIR := $(shell git rev-parse --show-toplevel)

# --- local dev ---
.PHONY: install init run curl check-db clean-db

install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt
	
init:
	pip install -e .
	
run:
	uvicorn app.main:app --reload --reload-dir app --port 8001
	
curl:
	curl -X POST http://localhost:8001/ingest \
		-H "Content-Type: application/json" \
		-d '{"document_name": "test_document.txt", "text": "This is a test document.", "metadata": {"source": "test"}}'

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