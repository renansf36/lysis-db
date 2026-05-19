from ...repositories.processes.repository import (
    fetch_by_group,
    fetch_by_matter,
    fetch_by_organization,
    fetch_by_origin,
    fetch_by_origin_capture_last_six_months,
    fetch_by_origin_distribution_last_six_months,
    fetch_by_origin_import_last_six_months,
    fetch_by_origin_registration_by_year_range,
    fetch_by_origin_registration_last_six_months,
    fetch_by_origin_with_date_range,
    fetch_by_origin_with_date_range_detailed,
    fetch_by_origin_with_instance_date_filter,
    fetch_by_status,
    fetch_process_count,
    fetch_process_inclusion_report,
    fetch_process_registration_details_by_year_range,
    fetch_publication_by_matter_last_month,
    fetch_publication_by_matter_last_six_months,
    fetch_publication_by_matter_total,
    fetch_publication_by_matter_year,
)
from ...schemas.schemas import (
    DateRangeFilter,
    OriginDateFilter,
    YearFilter,
)


def get_process_count():
    result = fetch_process_count()
    total = result[0]["total_processos"] if result else 0
    return {"total": total}


def get_origin_stats(filters: DateRangeFilter):
    return fetch_by_origin(filters)


def get_status_stats(filters: DateRangeFilter):
    return fetch_by_status(filters)


def get_matter_stats(filters: DateRangeFilter):
    return fetch_by_matter(filters)


def get_group_stats(filters: DateRangeFilter):
    return fetch_by_group(filters)


def get_organization_stats(filters: DateRangeFilter):
    return fetch_by_organization(filters)


def get_by_origin_with_instance_date_filter(filters: OriginDateFilter):
    return fetch_by_origin_with_instance_date_filter(filters)


def get_by_origin_registration_by_year_range(filters: DateRangeFilter):
    return fetch_by_origin_registration_by_year_range(filters)


def get_process_registration_details_by_year_range(filters: DateRangeFilter):
    return fetch_process_registration_details_by_year_range(filters)


def get_by_origin_registration_last_six_months(filters: DateRangeFilter):
    return fetch_by_origin_registration_last_six_months(filters)


def get_by_origin_capture_last_six_months(filters: DateRangeFilter):
    return fetch_by_origin_capture_last_six_months(filters)


def get_by_origin_distribution_last_six_months(filters: DateRangeFilter):
    return fetch_by_origin_distribution_last_six_months(filters)


def get_by_origin_import_last_six_months(filters: YearFilter):
    return fetch_by_origin_import_last_six_months(filters)


def get_by_origin_with_date_range(filters: DateRangeFilter):
    return fetch_by_origin_with_date_range(filters)


def get_by_origin_with_date_range_detailed(filters: DateRangeFilter):
    return fetch_by_origin_with_date_range_detailed(filters)


def get_process_inclusion_report(
    filters: DateRangeFilter,
    limit: int,
    offset: int,
):
    total, rows = fetch_process_inclusion_report(filters, limit, offset)
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": [dict(row) for row in rows],
    }


def get_publication_by_matter_year(filters: YearFilter):
    return fetch_publication_by_matter_year(filters)


def get_publication_by_matter_total():
    return fetch_publication_by_matter_total()


def get_publication_by_matter_last_six_months(filters: YearFilter):
    return fetch_publication_by_matter_last_six_months(filters)


def get_publication_by_matter_last_month(filters: YearFilter):
    return fetch_publication_by_matter_last_month(filters)
