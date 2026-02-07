from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router as search_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    from api.routes import _es
    if _es is not None:
        pass


app = FastAPI(
    title="Clinical Trials Search API",
    description="Natural language search over clinical trials. GET /search/<query>",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search_router)


@app.get("/")
def root():
    return {
        "message": "Clinical Trials Search API",
        "docs": "/docs",
        "search": "GET /search/<natural language query>  (optional ?page=1&size=10)",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


def main() -> None:
    from ingest_json import run_ingest
    run_ingest()

if __name__ == "__main__":
    main()