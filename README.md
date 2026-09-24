# fastapi-tutorials

Production-style FastAPI service for users and automation entitlements, persisted in SQLite. Validation is Pydantic, logging is Loguru, and HTTP is a layered FastAPI app.

## Architecture

| Layer | Responsibility |
| --- | --- |
| `app/api/routes` | HTTP controllers and request/response mapping |
| `app/services` | Business orchestration |
| `app/repositories` | SQLite persistence (SQLAlchemy + aiosqlite) |
| `app/models` | SQLAlchemy table mappings |
| `app/schemas` | Pydantic DTOs for API contracts |
| `app/domain` | Core domain models |
| `app/core` | Configuration, logging, database lifecycle |

## Prerequisites

- Python 3.12+

## Setup

```bash
cp .env.example .env
./scripts/cloud-agent-install.sh
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The SQLite file is created at `data/app.db` on first start.

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

Grant register for automations (who was given what, by whom, when). Rows are stored in SQLite.

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

```bash
source .venv/bin/activate
pytest
```

Tests use an isolated temporary SQLite database; no external services are required.
