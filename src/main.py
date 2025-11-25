from fastapi import FastAPI

from .api.v1.processes.router import router as processo_router
from .api.v1.status.router import router as status_router

app = FastAPI(title="Lysis DB API", version="1.0.0", docs_url="/docs", redoc_url="/redoc")

app.include_router(processo_router)
app.include_router(status_router)

@app.get("/")
def root():
    return {"message": "Lysis API DB working!"}
