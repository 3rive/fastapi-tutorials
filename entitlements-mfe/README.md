# Entitlements microfrontend

Vite + React 18 + TypeScript UI for the entitlements grant register. Package name: `@ssp/entitlements-mfe`.

This app is entitlements only. It does not render users, health, or other API modules. All data comes from the FastAPI `/entitlements` routes, which store rows in SQLite.

## Components

| Path | Role |
| --- | --- |
| `index.html` + `src/main.tsx` | Standalone page |
| `host.html` + `src/mfe.tsx` | Host demo that mounts `<ssp-entitlements>` in shadow DOM |
| `src/App.tsx` | Create, list, filter, update, revoke, restore, delete |
| `src/api.ts` | HTTP client for `/entitlements` |
| `src/types.ts` | Entitlement types shared with the API |
| `src/styles.css` | Isolated styles (inlined into the custom element) |
| `src/api.test.ts` | Vitest coverage for the client |

## Run with the API

From the repository root, start SQLite-backed FastAPI on port 8000:

```bash
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Then:

```bash
cd entitlements-mfe
npm install
npm run dev
```

| URL | What you get |
| --- | --- |
| http://localhost:5173 | Standalone entitlements UI |
| http://localhost:5173/host.html | Host shell around `<ssp-entitlements>` |

`vite.config.ts` proxies `/entitlements` and `/health` to `http://127.0.0.1:8000`. Leave `api-base` empty when using that proxy.

## API wiring

| Source | When to use it |
| --- | --- |
| empty (default) | Same origin or Vite proxy |
| `VITE_API_BASE` | Standalone/build should call a fixed API origin |
| `api-base` on `<ssp-entitlements>` | Host page and API are on different origins |

The API CORS setting is `CORS_ORIGINS` in the root `.env` (default `["*"]`).

## Host composition

```html
<ssp-entitlements api-base="http://localhost:8000"></ssp-entitlements>
<script type="module" src="/src/mfe.tsx"></script>
```

`host.html` omits `api-base` so the element uses the Vite proxy in development.

## Scripts

| Command | Result |
| --- | --- |
| `npm run dev` | Dev server on `0.0.0.0:5173` |
| `npm test` | Vitest (`jsdom`) |
| `npm run build` | Production bundles for `index.html` and `host.html` |
| `npm run preview` | Serve the production build on port 5173 |
