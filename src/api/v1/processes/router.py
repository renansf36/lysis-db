from fastapi import APIRouter, Query

from ....schemas.schemas import (
    DateRangeFilter,
    OriginDateFilter,
    PaginatedProcessInclusionReport,
    YearFilter,
)
from ....services.processes.service import (
    get_by_origin_capture_last_six_months,
    get_by_origin_distribution_last_six_months,
    get_by_origin_import_last_six_months,
    get_by_origin_registration_by_year_range,
    get_by_origin_registration_last_six_months,
    get_by_origin_with_date_range,
    get_by_origin_with_date_range_detailed,
    get_by_origin_with_instance_date_filter,
    get_group_stats,
    get_matter_stats,
    get_organization_stats,
    get_origin_stats,
    get_process_count,
    get_process_inclusion_report,
    get_process_registration_details_by_year_range,
    get_publication_by_matter_last_month,
    get_publication_by_matter_last_six_months,
    get_publication_by_matter_total,
    get_publication_by_matter_year,
    get_status_stats,
)

router = APIRouter(prefix="/api/v1/processes", tags=["Processes"])


@router.get("/count", summary="Contagem total de processos")
def process_count():
    return get_process_count()


@router.post("/by-origin", summary="Processos por origem")
def processes_by_origin(filters: DateRangeFilter):
    return get_origin_stats(filters)


@router.post("/by-status", summary="Processos por status")
def processes_by_status(filters: DateRangeFilter):
    return get_status_stats(filters)


@router.post("/by-matter", summary="Processos por assunto")
def processes_by_matter(filters: DateRangeFilter):
    return get_matter_stats(filters)


@router.post("/by-group", summary="Processos por grupo")
def processes_by_group(filters: DateRangeFilter):
    return get_group_stats(filters)


@router.post("/by-organization", summary="Processos por organizacao")
def processes_by_organization(filters: DateRangeFilter):
    return get_organization_stats(filters)


@router.post(
    "/by-origin-with-instance-date-filter",
    summary="Processos por data de instancia",
)
def processes_by_origin_with_instance_date_filter(filters: OriginDateFilter):
    return get_by_origin_with_instance_date_filter(filters)


@router.post(
    "/by-origin-registration-year-range",
    summary="Processos de cadastro por intervalo de datas",
)
def processes_by_origin_registration_year_range(filters: DateRangeFilter):
    return get_by_origin_registration_by_year_range(filters)


@router.post(
    "/by-origin-registration-year-range-detailed",
    summary="Processos de cadastro detalhados por intervalo de datas",
)
def processes_by_origin_registration_year_range_detailed(filters: DateRangeFilter):
    return get_process_registration_details_by_year_range(filters)


@router.post(
    "/by-origin-registration-last-six-months",
    summary="Processos de cadastro por mes no intervalo informado",
)
def processes_by_origin_registration_last_six_months(filters: DateRangeFilter):
    return get_by_origin_registration_last_six_months(filters)


@router.post(
    "/by-origin-capture-last-six-months",
    summary="Processos de captura por mes no intervalo informado",
)
def processes_by_origin_capture_last_six_months(filters: DateRangeFilter):
    return get_by_origin_capture_last_six_months(filters)


@router.post(
    "/by-origin-distribution-last-six-months",
    summary="Processos de distribuicao por mes no intervalo informado",
)
def processes_by_origin_distribution_last_six_months(filters: DateRangeFilter):
    return get_by_origin_distribution_last_six_months(filters)


@router.post(
    "/by-origin-import-last-six-months",
    summary="Processos de importacao dos ultimos 6 meses do ano",
)
def processes_by_origin_import_last_six_months(filters: YearFilter):
    return get_by_origin_import_last_six_months(filters)


@router.post(
    "/by-origin-with-date-range",
    summary="Processos por origem dentro de intervalo de datas",
)
def processes_by_origin_with_date_range(filters: DateRangeFilter):
    return get_by_origin_with_date_range(filters)


@router.post(
    "/by-origin-with-date-range-detailed",
    summary="Processos por origem e mes dentro de intervalo de datas",
)
def processes_by_origin_with_date_range_detailed(filters: DateRangeFilter):
    return get_by_origin_with_date_range_detailed(filters)


@router.post(
    "/reports/process-inclusion-period",
    summary="Relatorio detalhado de processos por periodo de inclusao",
    response_model=PaginatedProcessInclusionReport,
)
def process_inclusion_period_report(
    filters: DateRangeFilter,
    limit: int = Query(
        100,
        ge=1,
        le=500,
        description="Quantidade maxima de registros por pagina",
    ),
    offset: int = Query(
        0,
        ge=0,
        description="Quantidade de registros a pular antes da pagina atual",
    ),
) -> PaginatedProcessInclusionReport:
    return get_process_inclusion_report(filters, limit, offset)


@router.post(
    "/publications/by-matter-year",
    summary="Publicacoes por materia em um ano especifico",
)
def publications_by_matter_year(filters: YearFilter):
    return get_publication_by_matter_year(filters)


@router.get(
    "/publications/by-matter-total",
    summary="Total geral de publicacoes por materia",
)
def publications_by_matter_total():
    return get_publication_by_matter_total()


@router.post(
    "/publications/by-matter-last-six-months",
    summary="Publicacoes por mes nos ultimos 6 meses do ano",
)
def publications_by_matter_last_six_months(filters: YearFilter):
    return get_publication_by_matter_last_six_months(filters)


@router.post(
    "/publications/by-matter-last-month",
    summary="Publicacoes por materia no ultimo mes com dados",
)
def publications_by_matter_last_month(filters: YearFilter):
    return get_publication_by_matter_last_month(filters)
