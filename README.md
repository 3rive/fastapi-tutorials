# fastapi-tutorials

Production-style FastAPI service for storing user details in MongoDB, using Pydantic validation, Loguru logging, and a layered architecture.

## Architecture

| Layer | Responsibility |
| --- | --- |
| `app/api/routes` | HTTP controllers and request/response mapping |
| `app/services` | Business orchestration |
| `app/repositories` | MongoDB persistence (Motor) |
| `app/schemas` | Pydantic DTOs for API contracts |
| `app/domain` | Core domain models |
| `app/core` | Configuration, logging, database lifecycle |

## Prerequisites

- Python 3.12+
- Docker (for local MongoDB via Compose)

## Setup

```bash
cp .env.example .env
./scripts/cloud-agent-install.sh
./scripts/start-mongodb.sh
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## User API

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/users` | Create a user |
| `GET` | `/users` | List users (`skip`, `limit`) |
| `GET` | `/users/{id}` | Get one user |
| `PATCH` | `/users/{id}` | Update a user |
| `DELETE` | `/users/{id}` | Delete a user |

## Tests

Requires MongoDB on `localhost:27017` (start with `./scripts/start-mongodb.sh`):

```bash
source .venv/bin/activate
pytest
```
