from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.v1.status.router import router

app = FastAPI()
app.include_router(router)

client = TestClient(app)

def test_status_page():
  response = client.get("/api/v1/status")
  assert response.status_code == 200
