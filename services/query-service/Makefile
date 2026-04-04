ROOT_DIR := $(shell git rev-parse --show-toplevel)

# --- local dev ---
.PHONY: install init run

install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt

init:
	pip install -e .
	
run:
	uvicorn app.main:app --reload --reload-dir app