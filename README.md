# fastapi-tutorials

FastAPI service for users and automation entitlements, stored in SQLite, plus a standalone entitlements microfrontend.

| Component | Location | What it does |
| --- | --- | --- |
| API | `app/` | Health, user CRUD, and entitlement grant-register CRUD |
| Entitlements UI | `entitlements-mfe/` | React microfrontend for entitlements only |

Validation is Pydantic. Logging is Loguru. Persistence is SQLAlchemy 2 with aiosqlite.

## Architecture

| Layer | Responsibility |
| --- | --- |
| `app/api/routes` | HTTP controllers (`health`, `users`, `entitlements`) |
| `app/services` | Business orchestration and logging |
| `app/repositories` | SQLite reads and writes |
| `app/models` | SQLAlchemy tables `users` and `entitlements` |
| `app/schemas` | Pydantic request and response models |
| `app/domain` | Domain objects used by services |
| `app/core` | Settings, Loguru setup, engine and session lifecycle |
| `entitlements-mfe/` | Vite + React UI, also published as `<ssp-entitlements>` |

## Prerequisites

- Python 3.12+
- Node.js 22+ (entitlements microfrontend only)

## Configuration

Copy the example file and edit it if the defaults are not what you want:

```bash
cp .env.example .env
```

| Variable | Default | Purpose |
| --- | --- | --- |
| `APP_ENV` | `development` | Runtime label used in startup logs |
| `LOG_LEVEL` | `INFO` | Loguru level |
| `DATABASE_URL` | `sqlite+aiosqlite:///./data/app.db` | SQLite database |
| `CORS_ORIGINS` | `["*"]` | Origins allowed to call the API |

The database file is created on first startup. `./scripts/cloud-agent-start.sh` only creates the `data/` directory.

## Setup

```bash
./scripts/cloud-agent-install.sh
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

`cloud-agent-install.sh` creates `.venv`, installs `requirements.txt`, and runs `npm install` in `entitlements-mfe/`.

- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health
- Entitlements UI: see `entitlements-mfe/README.md`

## User API

Stored in the `users` table. Email is unique.

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/users` | Create a user (`email`, `full_name`, optional `phone`) |
| `GET` | `/users` | List users (`skip`, `limit`) |
| `GET` | `/users/{id}` | Get one user |
| `PATCH` | `/users/{id}` | Update email, name, or phone |
| `DELETE` | `/users/{id}` | Delete a user |

## Entitlement API

Grant register: who was given access to which automation, by whom, and when. Stored in the `entitlements` table. `(automation_key, ad_group)` is unique, ignoring case.

Fields: `automation_key`, `ad_group`, `permissions` (`view`, `execute`), `granted_by`, `granted_at`, `expires_at`, `status` (`active`, `revoked`), `revoked_by`, `revoked_at`, `schema_version`.

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/entitlements` | Create a grant |
| `GET` | `/entitlements` | List grants (`skip`, `limit`, `automation_key`, `ad_group`, `status`) |
| `GET` | `/entitlements/{id}` | Get one grant |
| `PATCH` | `/entitlements/{id}` | Change permissions, expiry, or revoke/restore |
| `DELETE` | `/entitlements/{id}` | Delete a grant |

Revoking requires `revoked_by` and sets `revoked_at`. Restoring to `active` clears both revoke fields.

## Tests

```bash
source .venv/bin/activate
pytest
cd entitlements-mfe && npm test
```

API tests use a temporary SQLite file. The microfrontend tests cover the entitlements API client.
