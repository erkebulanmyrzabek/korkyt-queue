SHELL := /bin/bash

.PHONY: init up up-backend up-frontend up-core down logs ps api bot worker frontend

init:
	bash scripts/init_venv.sh

up:
	docker compose up --build -d

up-core:
	docker compose up --build -d postgres redis api frontend nginx

up-backend:
	docker compose up --build -d postgres redis api bot worker beat

up-frontend:
	docker compose up --build -d frontend

down:
	docker compose down

logs:
	docker compose logs -f --tail=150

ps:
	docker compose ps

api:
	docker compose logs -f api

bot:
	docker compose logs -f bot

worker:
	docker compose logs -f worker

frontend:
	docker compose logs -f frontend
