ROOT_DIR := $(shell git rev-parse --show-toplevel)

# --- local dev ---
.PHONY: lint format test test-int run curl

lint:
	pylint --rcfile $(ROOT_DIR)/.pylintrc query tests

format:
	$(MAKE) -C $(ROOT_DIR) format

test:
	pytest --ignore=tests/test_integration.py

test-int:
	pytest -m integration -v

run:
	uvicorn query.main:app --reload --reload-dir query --port 8001

curl:
	curl -X POST http://localhost:8001/query \
		-H "Content-Type: application/json" \
		-d '{"query": "What is a vector database?", "top_k": 5, "filters": {}, "debug": false}'

# --- docker orchestration ---
.PHONY: docker-up docker-down docker-reset docker-db docker-query

docker-up:
	@make -C $(ROOT_DIR) docker-up

docker-down:
	@make -C $(ROOT_DIR) docker-down

docker-reset:
	@make -C $(ROOT_DIR) docker-reset

docker-db:
	@make -C $(ROOT_DIR) docker-db

docker-query:
	@make -C $(ROOT_DIR) docker-query
