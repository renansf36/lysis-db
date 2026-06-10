from datetime import date

import pytest

from src.repositories.processes import repository
from src.schemas.schemas import DateRangeFilter, OriginDateFilter


@pytest.mark.parametrize(
    "fetcher",
    [
        repository.fetch_by_origin,
        repository.fetch_by_status,
        repository.fetch_by_matter,
        repository.fetch_by_group,
        repository.fetch_by_organization,
        repository.fetch_by_origin_with_date_range,
        repository.fetch_by_origin_with_date_range_detailed,
    ],
)
def test_process_aggregations_count_distinct_processes(monkeypatch, fetcher):
    captured = {}

    def fake_run_query(sql, params=None):
        captured["sql"] = sql
        captured["params"] = params
        return []

    monkeypatch.setattr(repository, "run_query", fake_run_query)
    filters = DateRangeFilter(
        start_date=date(2025, 1, 1),
        end_date=date(2025, 1, 31),
    )

    fetcher(filters)

    assert "COUNT(DISTINCT T01.ISN_PROCESSO)" in captured["sql"]


def test_instance_date_origin_aggregation_counts_distinct_processes(monkeypatch):
    captured = {}

    def fake_run_query(sql, params=None):
        captured["sql"] = sql
        captured["params"] = params
        return []

    monkeypatch.setattr(repository, "run_query", fake_run_query)
    filters = OriginDateFilter(
        start_date=date(2025, 1, 1),
        end_date=date(2025, 1, 31),
    )

    repository.fetch_by_origin_with_instance_date_filter(filters)

    assert "COUNT(DISTINCT T01.ISN_PROCESSO)" in captured["sql"]


@pytest.mark.parametrize(
    "fetcher",
    [
        repository.fetch_by_origin_registration_by_year_range,
        repository.fetch_process_registration_details_by_year_range,
    ],
)
def test_registration_aggregations_count_process_ids(monkeypatch, fetcher):
    captured = {}

    def fake_run_query(sql, params=None):
        captured["sql"] = sql
        captured["params"] = params
        return []

    monkeypatch.setattr(repository, "run_query", fake_run_query)
    filters = DateRangeFilter(
        start_date=date(2025, 1, 1),
        end_date=date(2025, 12, 31),
    )

    fetcher(filters)

    assert "COUNT(DISTINCT p.ISN_PROCESSO)" in captured["sql"]


def test_process_inclusion_report_has_one_base_row_per_process(monkeypatch):
    captured = []

    def fake_run_query(sql, params=None):
        captured.append(sql)
        return [{"total": 0}]

    monkeypatch.setattr(repository, "run_query", fake_run_query)
    filters = DateRangeFilter(
        start_date=date(2025, 1, 1),
        end_date=date(2025, 1, 31),
    )

    repository.fetch_process_inclusion_report(filters, limit=100, offset=0)

    assert "GROUP BY\n                p.ISN_PROCESSO" in captured[0]
    assert "i.NUM_PROCESSO" not in captured[0]
    assert "EXISTS (" in captured[0]
