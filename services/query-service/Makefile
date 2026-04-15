ROOT_DIR := $(shell git rev-parse --show-toplevel)

# --- local dev ---
.PHONY: install init run curl

install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt

init:
	pip install -e .

run:
	uvicorn app.main:app --reload --reload-dir app --port 8001

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
