from fastapi import FastAPI

app = FastAPI(title="fastapi-tutorials", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/tutorials")
def list_tutorials() -> dict[str, list[str]]:
    return {"tutorials": ["getting-started"]}
