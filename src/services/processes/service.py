from ...repositories.processes.repository import (
    fetch_by_group,
    fetch_by_matter,
    fetch_by_organization,
    fetch_by_origin,
    fetch_by_origin_registration_by_year_range,
    fetch_by_origin_registration_last_six_months,
    fetch_by_origin_capture_last_six_months,
    fetch_by_origin_with_instance_date_filter,
    fetch_by_status,
    fetch_process_count,
)
from ...schemas.schemas import OriginDateFilter, YearFilter, YearRangeFilter


def get_process_count():
    result = fetch_process_count()
    return {"total": result[0]["total_processos"]}

def get_origin_stats():
    return fetch_by_origin()

def get_status_stats():
    return fetch_by_status()

def get_matter_stats():
    return fetch_by_matter()

def get_group_stats():
    return fetch_by_group()

def get_organization_stats():
    return fetch_by_organization()

def get_by_origin_with_instance_date_filter(filters: OriginDateFilter):
    return fetch_by_origin_with_instance_date_filter(filters)

def get_by_origin_registration_by_year_range(filters: YearRangeFilter):
    return fetch_by_origin_registration_by_year_range(filters)

def get_by_origin_registration_last_six_months(filters: YearFilter):
    return fetch_by_origin_registration_last_six_months(filters)

def get_by_origin_capture_last_six_months(filters: YearFilter):
    return fetch_by_origin_capture_last_six_months(filters)