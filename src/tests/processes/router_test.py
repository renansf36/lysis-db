from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.v1.processes.router import router

app = FastAPI()
app.include_router(router)

client = TestClient(app)

def test_process_count():
  response = client.get("/api/v1/processes/count")
  assert response.status_code == 200

def test_processes_by_origin():
  response = client.get("/api/v1/processes/by-origin")
  assert response.status_code == 200

def test_processes_by_status():
  response = client.get("/api/v1/processes/by-status")
  assert response.status_code == 200

def test_processes_by_matter():
  response = client.get("/api/v1/processes/by-matter")
  assert response.status_code == 200

def test_processes_by_group():
  response = client.get("/api/v1/processes/by-group")
  assert response.status_code == 200

def test_processes_by_organization():
  response = client.get("/api/v1/processes/by-organization")
  assert response.status_code == 200

def test_processes_by_origin_with_instance_date_filter():
  payload = {
    "start_date": "1991-01-01",
    "end_date": "2025-11-28"
  }
  response = client.post(
    "/api/v1/processes/by-origin-with-instance-date-filter",
    json=payload
  )
  
  assert response.status_code == 200

def test_processes_by_origin_registration_year_range():
  """
  Testa o endpoint POST /by-origin-registration-year-range
  com intervalo de anos 2000-2025
  """
  payload = {
    "start_year": 2000,
    "end_year": 2025
  }
  response = client.post(
    "/api/v1/processes/by-origin-registration-year-range",
    json=payload
  )
  
  assert response.status_code == 200
  data = response.json()
  
  assert isinstance(data, list)

  for record in data:
    assert "Ano" in record
    assert "TotalCadastro" in record
    assert isinstance(record["Ano"], int)
    assert isinstance(record["TotalCadastro"], int)

def test_processes_by_origin_registration_last_six_months():
  """
  Testa o endpoint POST /by-origin-registration-last-six-months
  para o ano de 2025, retornando os últimos 6 meses (julho a dezembro)
  """
  payload = {
    "year": 2025
  }
  response = client.post(
    "/api/v1/processes/by-origin-registration-last-six-months",
    json=payload
  )
  
  assert response.status_code == 200
  data = response.json()
  
  # Verifica se é uma lista
  assert isinstance(data, list)
  
def test_processes_by_origin_registration_last_six_months_custom_year():
  """
  Testa o endpoint com um ano diferente (2024)
  """
  payload = {
    "year": 2024
  }
  response = client.post(
    "/api/v1/processes/by-origin-registration-last-six-months",
    json=payload
  )
  
  assert response.status_code == 200
  data = response.json()
  
  # Verifica estrutura básica
  assert len(data) == 6
  assert all("Mes" in record for record in data)
  assert all("NomeMes" in record for record in data)
  assert all("TotalCadastro" in record for record in data)

def test_processes_by_origin_capture_last_six_months():
  """
  Testa o endpoint POST /by-origin-capture-last-six-months
  para o ano de 2025, retornando os últimos 6 meses (julho a dezembro)
  """
  payload = {
    "year": 2025
  }
  response = client.post(
    "/api/v1/processes/by-origin-capture-last-six-months",
    json=payload
  )
  
  assert response.status_code == 200
  data = response.json()
  
  # Verifica se é uma lista
  assert isinstance(data, list)
      
def test_processes_by_origin_capture_last_six_months_custom_year():
  """
  Testa o endpoint com um ano diferente (2024)
  """
  payload = {
    "year": 2024
  }
  response = client.post(
    "/api/v1/processes/by-origin-capture-last-six-months",
    json=payload
  )
  
  assert response.status_code == 200

def test_processes_by_origin_distribution_last_six_months():
  """
  Testa o endpoint POST /by-origin-distribution-last-six-months
  para o ano de 2025, retornando os últimos 6 meses (julho a dezembro)
  """
  payload = {
    "year": 2025
  }
  response = client.post(
    "/api/v1/processes/by-origin-distribution-last-six-months",
    json=payload
  )
  
  assert response.status_code == 200
  data = response.json()
  
  # Verifica se é uma lista
  assert isinstance(data, list)
  
def test_processes_by_origin_distribution_last_six_months_custom_year():
  """
  Testa o endpoint com um ano diferente (2024)
  """
  payload = {
    "year": 2024
  }
  response = client.post(
    "/api/v1/processes/by-origin-distribution-last-six-months",
    json=payload
  )
  
  assert response.status_code == 200

def test_processes_by_origin_import_last_six_months():
  """
  Testa o endpoint POST /by-origin-import-last-six-months
  para o ano de 2025, retornando os últimos 6 meses (julho a dezembro)
  """
  payload = {
    "year": 2025
  }
  response = client.post(
    "/api/v1/processes/by-origin-import-last-six-months",
    json=payload
  )
  
  assert response.status_code == 200
  data = response.json()
  
  # Verifica se é uma lista
  assert isinstance(data, list)
  
def test_processes_by_origin_import_last_six_months_custom_year():
  """
  Testa o endpoint com um ano diferente (2024)
  """
  payload = {
    "year": 2024
  }
  response = client.post(
    "/api/v1/processes/by-origin-import-last-six-months",
    json=payload
  )
  
  assert response.status_code == 200
