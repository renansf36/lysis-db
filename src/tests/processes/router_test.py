from datetime import date

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.v1.processes import router as processes_router_module

app = FastAPI()
app.include_router(processes_router_module.router)

client = TestClient(app)


@pytest.mark.parametrize(
    ("path", "target", "payload"),
    [
        ("/api/v1/processes/count", "get_process_count", {"total": 10}),
        (
            "/api/v1/processes/publications/by-matter-total",
            "get_publication_by_matter_total",
            [{"subject": "Fiscal", "total": 6}],
        ),
    ],
)
def test_get_endpoints(monkeypatch, path, target, payload):
    monkeypatch.setattr(processes_router_module, target, lambda *args: payload)

    response = client.get(path)

    assert response.status_code == 200
    assert response.json() == payload


@pytest.mark.parametrize(
    ("path", "target", "body", "payload"),
    [
        (
            "/api/v1/processes/by-origin",
            "get_origin_stats",
            {"start_date": "2025-01-10", "end_date": "2025-01-31"},
            [{"origin": "Cadastro", "total": 5}],
        ),
        (
            "/api/v1/processes/by-status",
            "get_status_stats",
            {"start_date": "2025-01-10", "end_date": "2025-01-31"},
            [{"status": "Ativo", "total": 3}],
        ),
        (
            "/api/v1/processes/by-matter",
            "get_matter_stats",
            {"start_date": "2025-01-10", "end_date": "2025-01-31"},
            [{"subject": "Civel", "total": 2}],
        ),
        (
            "/api/v1/processes/by-group",
            "get_group_stats",
            {"start_date": "2025-01-10", "end_date": "2025-01-31"},
            [{"process_group": "Equipe A", "total": 4}],
        ),
        (
            "/api/v1/processes/by-organization",
            "get_organization_stats",
            {"start_date": "2025-01-10", "end_date": "2025-01-31"},
            [{"agency": "Orgao X", "total": 1}],
        ),
        (
            "/api/v1/processes/by-origin-with-instance-date-filter",
            "get_by_origin_with_instance_date_filter",
            {"start_date": "2025-01-01", "end_date": "2025-01-31"},
            [{"Origem": "Cadastro", "Quantidade": 8}],
        ),
        (
            "/api/v1/processes/by-origin-registration-year-range",
            "get_by_origin_registration_by_year_range",
            {"start_date": "2020-01-01", "end_date": "2024-12-31"},
            [{"Ano": 2024, "TotalCadastro": 12}],
        ),
        (
            "/api/v1/processes/by-origin-registration-year-range-detailed",
            "get_process_registration_details_by_year_range",
            {"start_date": "2020-01-01", "end_date": "2024-12-31"},
            [{"Ano": 2024, "TotalCadastro": 12, "OrigemProcesso": "Cadastro"}],
        ),
        (
            "/api/v1/processes/by-origin-registration-last-six-months",
            "get_by_origin_registration_last_six_months",
            {"start_date": "2025-07-01", "end_date": "2025-12-31"},
            [{"Mes": 7, "NomeMes": "July", "TotalCadastro": 1}],
        ),
        (
            "/api/v1/processes/by-origin-capture-last-six-months",
            "get_by_origin_capture_last_six_months",
            {"start_date": "2025-07-01", "end_date": "2025-12-31"},
            [{"Mes": 7, "NomeMes": "July", "TotalCaptura": 1}],
        ),
        (
            "/api/v1/processes/by-origin-distribution-last-six-months",
            "get_by_origin_distribution_last_six_months",
            {"start_date": "2025-07-01", "end_date": "2025-12-31"},
            [{"Mes": 7, "NomeMes": "July", "TotalDistribuicao": 1}],
        ),
        (
            "/api/v1/processes/by-origin-import-last-six-months",
            "get_by_origin_import_last_six_months",
            {"year": 2025},
            [{"Mes": 7, "NomeMes": "July", "TotalImportacao": 1}],
        ),
        (
            "/api/v1/processes/by-origin-with-date-range",
            "get_by_origin_with_date_range",
            {"start_date": "2025-07-01", "end_date": "2025-12-31"},
            [{"Origem": "Cadastro", "Quantidade": 9}],
        ),
        (
            "/api/v1/processes/by-origin-with-date-range-detailed",
            "get_by_origin_with_date_range_detailed",
            {"start_date": "2025-07-01", "end_date": "2025-12-31"},
            [{"Origem": "Cadastro", "Ano": 2025, "Mes": 7, "Quantidade": 9}],
        ),
        (
            "/api/v1/processes/reports/process-inclusion-period",
            "get_process_inclusion_report",
            {"start_date": "2025-07-01", "end_date": "2025-12-31"},
            {
                "total": 1,
                "limit": 100,
                "offset": 0,
                "items": [{"N Processo": "1234567-89.2025.8.00.0001"}],
            },
        ),
        (
            "/api/v1/processes/publications/by-matter-year",
            "get_publication_by_matter_year",
            {"year": 2025},
            [{"subject": "Fiscal", "total": 9}],
        ),
        (
            "/api/v1/processes/publications/by-matter-last-six-months",
            "get_publication_by_matter_last_six_months",
            {"year": 2025},
            [{"Mes": 7, "NomeMes": "July", "TotalPublicacoes": 9}],
        ),
        (
            "/api/v1/processes/publications/by-matter-last-month",
            "get_publication_by_matter_last_month",
            {"year": 2025},
            [{"subject": "Fiscal", "total": 4}],
        ),
    ],
)
def test_post_endpoints(monkeypatch, path, target, body, payload):
    monkeypatch.setattr(processes_router_module, target, lambda *args: payload)

    response = client.post(path, json=body)

    assert response.status_code == 200
    assert response.json() == payload


def test_processes_by_origin_parses_date_range_payload(monkeypatch):
    captured = {}

    def fake_handler(filters):
        captured["filters"] = filters
        return [{"origin": "Cadastro", "total": 5}]

    monkeypatch.setattr(
        processes_router_module,
        "get_origin_stats",
        fake_handler,
    )

    response = client.post(
        "/api/v1/processes/by-origin",
        json={"start_date": "2025-01-10", "end_date": "2025-01-31"},
    )

    assert response.status_code == 200
    assert captured["filters"].start_date == date(2025, 1, 10)
    assert captured["filters"].end_date == date(2025, 1, 31)


def test_process_inclusion_report_parses_pagination_query_params(monkeypatch):
    captured = {}

    def fake_handler(filters, limit, offset):
        captured["filters"] = filters
        captured["limit"] = limit
        captured["offset"] = offset
        return {
            "total": 1,
            "limit": limit,
            "offset": offset,
            "items": [{"N Processo": "123"}],
        }

    monkeypatch.setattr(
        processes_router_module,
        "get_process_inclusion_report",
        fake_handler,
    )

    response = client.post(
        "/api/v1/processes/reports/process-inclusion-period",
        params={"limit": 50, "offset": 100},
        json={"start_date": "2025-07-01", "end_date": "2025-12-31"},
    )

    assert response.status_code == 200
    assert captured["filters"].start_date == date(2025, 7, 1)
    assert captured["filters"].end_date == date(2025, 12, 31)
    assert captured["limit"] == 50
    assert captured["offset"] == 100


def test_process_inclusion_report_rejects_invalid_pagination():
    response = client.post(
        "/api/v1/processes/reports/process-inclusion-period",
        params={"limit": 0, "offset": -1},
        json={"start_date": "2025-07-01", "end_date": "2025-12-31"},
    )

    assert response.status_code == 422


def test_date_range_payload_is_validated():
    response = client.post(
        "/api/v1/processes/by-origin",
        json={"start_date": "2025-12-31", "end_date": "2025-01-01"},
    )

    assert response.status_code == 422


def test_registration_year_range_date_payload_is_validated():
    response = client.post(
        "/api/v1/processes/by-origin-registration-year-range",
        json={"start_date": "2025-12-31", "end_date": "2025-01-01"},
    )

    assert response.status_code == 422
