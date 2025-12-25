.PHONY: help build up down restart logs pull-model clean

help:
	@echo "SimpleRAG Docker Commands"
	@echo "=========================="
	@echo "make build       - Build Docker images"
	@echo "make up          - Start all services"
	@echo "make down        - Stop all services"
	@echo "make restart     - Restart all services"
	@echo "make logs        - View logs (all services)"
	@echo "make logs-app    - View application logs"
	@echo "make logs-ollama - View Ollama logs"
	@echo "make pull-model  - Pull Ollama model"
	@echo "make shell       - Open shell in app container"
	@echo "make clean       - Remove all containers and volumes"
	@echo "make ps          - Show running containers"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Waiting for services to start..."
	@sleep 5
	@echo "Pulling Ollama model..."
	@docker-compose exec -T ollama ollama pull llama2 || true
	@echo ""
	@echo "✅ SimpleRAG is ready at http://localhost:8000"

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

logs-app:
	docker-compose logs -f app

logs-ollama:
	docker-compose logs -f ollama

pull-model:
	docker-compose exec ollama ollama pull llama2

shell:
	docker-compose exec app /bin/bash

clean:
	docker-compose down -v
	rm -rf chroma_db/* uploads/* documents_to_scan/*

ps:
	docker-compose ps
