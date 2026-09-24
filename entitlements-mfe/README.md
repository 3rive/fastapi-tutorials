# Entitlements microfrontend

React + Vite UI for the entitlements grant register. It calls only `/entitlements`. Users and other portal modules are not part of this app.

Package name: `@ssp/entitlements-mfe`.

## What it includes

| Surface | Entry | Behavior |
| --- | --- | --- |
| Standalone page | `index.html` / `src/main.tsx` | Full entitlements screen |
| Host custom element | `host.html` / `src/mfe.tsx` | Same screen inside `<ssp-entitlements>` (shadow DOM) |
| API client | `src/api.ts` | List, create, update, and delete against the FastAPI service |

The screen can create a grant, filter the list, change permissions and expiry, revoke, restore, and delete.

## Run locally

Start the API from the repository root first. It listens on port 8000 and stores grants in SQLite.

```bash
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Then start this app:

```bash
cd entitlements-mfe
npm install
npm run dev
```

- Standalone UI: http://localhost:5173
- Host-shell demo: http://localhost:5173/host.html

The Vite dev server proxies `/entitlements` and `/health` to `http://127.0.0.1:8000`. With that proxy, leave `api-base` unset.

## Configuration

| Source | Used when |
| --- | --- |
| `api-base` attribute on `<ssp-entitlements>` | A host page embeds the custom element and the API is on another origin |
| `VITE_API_BASE` | Standalone or embedded build should call a fixed API origin |
| empty (default) | Requests stay same-origin, including the Vite proxy |

The API allows browser calls from other origins through `CORS_ORIGINS` in the root `.env` (default `["*"]`).

## Composition

```html
<ssp-entitlements api-base="http://localhost:8000"></ssp-entitlements>
<script type="module" src="/src/mfe.tsx"></script>
```

`host.html` is a minimal shell that mounts the element with no `api-base`, so it uses the dev proxy.

## Scripts

| Command | Result |
| --- | --- |
| `npm run dev` | Dev server on port 5173 |
| `npm test` | Vitest tests for the API client |
| `npm run build` | Production build of `index.html` and `host.html` |
| `npm run preview` | Serves the production build on port 5173 |
