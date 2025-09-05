# Makefile for running the project with Docker Compose and Alembic
# Usage examples:
#   make build        # Build Docker images
#   make up           # Start containers in background
#   make migrate      # Run Alembic migrations inside the app container
#   make test         # Run tests inside the app container
#   make start        # Start containers in foreground (logs attached)
#   make down         # Stop and remove containers

# You can override COMPOSE to use docker-compose instead of docker compose
COMPOSE ?= docker compose
COMPOSE_FILE := deployments/docker-compose.yml
SERVICE ?= app

.PHONY: build up down start logs migrate test shell ps restart stop

build:
	$(COMPOSE) -f $(COMPOSE_FILE) build

up:
	$(COMPOSE) -f $(COMPOSE_FILE) up -d

start:
	$(COMPOSE) -f $(COMPOSE_FILE) up

down:
	$(COMPOSE) -f $(COMPOSE_FILE) down

logs:
	$(COMPOSE) -f $(COMPOSE_FILE) logs -f $(SERVICE)

ps:
	$(COMPOSE) -f $(COMPOSE_FILE) ps

restart: down up

stop:
	$(COMPOSE) -f $(COMPOSE_FILE) stop

# Run Alembic migrations
# Example: docker-compose run --rm app alembic upgrade head
migrate:
	$(COMPOSE) -f $(COMPOSE_FILE) run --rm $(SERVICE) python -m alembic upgrade head

# Run API tests inside the Docker container
# Example: docker-compose run --rm app pytest tests/
# Installs test requirements inside the container before running tests
# Override TEST_PATH to run a subset, e.g., make test TEST_PATH=tests/test_detector_unit.py
TEST_PATH ?= tests/

test:
	$(COMPOSE) -f $(COMPOSE_FILE) run --rm $(SERVICE) sh -c "pip install -q -r test-requirements.txt || true; pytest -q $(TEST_PATH)"

# Open a shell inside the app container
shell:
	$(COMPOSE) -f $(COMPOSE_FILE) run --rm $(SERVICE) sh