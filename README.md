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

## Entitlement API

Grant register for automations (who was given what, by whom, when). Persistence is in-memory.

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/entitlements` | Create an entitlement |
| `GET` | `/entitlements` | List entitlements (`skip`, `limit`, `automation_key`, `ad_group`, `status`) |
| `GET` | `/entitlements/{id}` | Get one entitlement |
| `PATCH` | `/entitlements/{id}` | Update permissions, expiry, or revoke/restore |
| `DELETE` | `/entitlements/{id}` | Delete an entitlement |

## Entitlements microfrontend

Standalone UI for entitlements only (no users module). It can run by itself or be composed into a host page as `<ssp-entitlements>`.

```bash
cd entitlements-mfe
npm install
npm run dev
```

- Standalone: http://localhost:5173
- Host-shell demo: http://localhost:5173/host.html
- More detail: `entitlements-mfe/README.md`

## Tests

Requires MongoDB on `localhost:27017` (start with `./scripts/start-mongodb.sh`):

```bash
source .venv/bin/activate
pytest
```
