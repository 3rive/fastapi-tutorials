# fastapi-tutorials

Two deployable components live in this repository:

| Component | Path | Stack | Role |
| --- | --- | --- | --- |
| HTTP API | `app/` | FastAPI 0.3.0, Pydantic, Loguru, SQLAlchemy 2, aiosqlite | Health, users, entitlements |
| Entitlements microfrontend | `entitlements-mfe/` | Vite, React 18, TypeScript | Grant-register UI only |

Both users and entitlements persist in SQLite.

## Repository layout

```text
app/                    FastAPI application
  api/routes/           health.py, users.py, entitlements.py
  api/dependencies.py   session and service wiring
  services/             UserService, EntitlementService
  repositories/         SqliteUserRepository, SqliteEntitlementRepository
  models/               SQLAlchemy tables users, entitlements
  schemas/              request and response DTOs
  domain/               User, Entitlement, Permission, EntitlementStatus
  core/                 config, logging, SQLite engine
  exceptions.py         AppError, NotFoundError, ConflictError, BadRequestError
  main.py               app factory, CORS, lifespan
entitlements-mfe/       standalone UI and <ssp-entitlements> custom element
tests/                  pytest: health, CORS, users, entitlements
scripts/                cloud-agent-install.sh, cloud-agent-start.sh
data/                   SQLite file app.db (created at runtime)
.env.example            APP_ENV, LOG_LEVEL, DATABASE_URL, CORS_ORIGINS
```

## Prerequisites

- Python 3.12+
- Node.js 22+ if you run the microfrontend

## Configuration

```bash
cp .env.example .env
```

| Variable | Default | Purpose |
| --- | --- | --- |
| `APP_ENV` | `development` | Label in the startup log |
| `LOG_LEVEL` | `INFO` | Loguru level |
| `DATABASE_URL` | `sqlite+aiosqlite:///./data/app.db` | SQLite database |
| `CORS_ORIGINS` | `["*"]` | Browser origins allowed to call the API |

`./scripts/cloud-agent-start.sh` creates `data/`. The first API start creates `data/app.db` and the `users` and `entitlements` tables.

## Run the API

```bash
./scripts/cloud-agent-install.sh
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Install also runs `npm install` in `entitlements-mfe/`.

- Docs: http://localhost:8000/docs
- Health: `GET /health` → `{"status":"ok"}`

## Run the entitlements UI

With the API already on port 8000:

```bash
cd entitlements-mfe
npm run dev
```

Vite listens on http://localhost:5173 and proxies `/entitlements` and `/health` to the API. Details are in `entitlements-mfe/README.md`.

## Health

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/health` | Liveness probe |

## User API

Table `users`. Unique `email`. Duplicate email returns `409`.

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/users` | Create (`email`, `full_name`, optional `phone`) |
| `GET` | `/users` | List (`skip` ≥ 0, `limit` 1–100, default 20) |
| `GET` | `/users/{id}` | Get one |
| `PATCH` | `/users/{id}` | Update email, name, or phone |
| `DELETE` | `/users/{id}` | Delete (`204`) |

## Entitlement API

Table `entitlements`. Unique `(automation_key, ad_group)` ignoring case (`409` on conflict). Grant register only: who received which automation, from whom, and when.

| Field | Values |
| --- | --- |
| `permissions` | list of `view` and/or `execute` |
| `status` | `active` or `revoked` |
| `schema_version` | integer ≥ 1, default `1` |

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/entitlements` | Create a grant |
| `GET` | `/entitlements` | List (`skip`, `limit`, `automation_key`, `ad_group`, `status`) |
| `GET` | `/entitlements/{id}` | Get one |
| `PATCH` | `/entitlements/{id}` | Update permissions, expiry, or revoke/restore |
| `DELETE` | `/entitlements/{id}` | Delete (`204`) |

Revoke payloads must include `revoked_by` (sets `revoked_at`). Restoring `status` to `active` clears `revoked_by` and `revoked_at`.

## Tests

```bash
source .venv/bin/activate
pytest
cd entitlements-mfe && npm test
```

`tests/` covers health, CORS, user CRUD, and entitlement CRUD against a temporary SQLite file. `entitlements-mfe` Vitest covers the HTTP client.
