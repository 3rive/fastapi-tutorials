# fastapi-tutorials

Tutorial exercises for [FastAPI](https://fastapi.tiangolo.com/).

## Local development

```bash
./scripts/cloud-agent-install.sh
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Tests

```bash
source .venv/bin/activate
pytest
```
