# Entitlements microfrontend

Standalone UI for the entitlements grant register. It does not include users or other portal modules.

## Run locally

Start the API, then this app:

```bash
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

cd entitlements-mfe
npm install
npm run dev
```

- Standalone MFE: http://localhost:5173
- Host-shell demo (custom element only): http://localhost:5173/host.html

Vite proxies `/entitlements` to the FastAPI process on port 8000.

## Composition

A host application can mount this MFE as a web component without loading the rest of the portal:

```html
<ssp-entitlements api-base="http://localhost:8000"></ssp-entitlements>
<script type="module" src="/src/mfe.tsx"></script>
```

`api-base` is optional when the host and API share an origin, or when a reverse proxy already forwards `/entitlements`.
