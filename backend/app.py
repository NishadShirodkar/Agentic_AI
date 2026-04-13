from fastapi import FastAPI

from api.routes import router as research_router

app = FastAPI(title="Research Agent V2", version="2.0.0")
app.include_router(research_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=5001, reload=True)
