from fastapi import APIRouter

from ....schemas.schemas import OriginDateFilter, YearFilter, YearRangeFilter
from ....services.processes.service import (
    get_by_origin_capture_last_six_months,
    get_by_origin_distribution_last_six_months,
    get_by_origin_import_last_six_months,
    get_by_origin_registration_by_year_range,
    get_by_origin_registration_last_six_months,
    get_by_origin_with_instance_date_filter,
    get_group_stats,
    get_matter_stats,
    get_organization_stats,
    get_origin_stats,
    get_process_count,
    get_status_stats,
)

router = APIRouter(prefix="/api/v1/processes", tags=["Processes"])

@router.get("/count", summary="Contagem total de processos")
def process_count():
    """
    Retorna o total de processos registrados no sistema.
    """
    return get_process_count()

@router.get("/by-origin", summary="Processos por origem")
def processes_by_origin():
    """
    Retorna estatísticas dos processos agrupados por origem.
    """
    return get_origin_stats()

@router.get("/by-status", summary="Processos por status")
def processes_by_status():
    """
    Retorna estatísticas dos processos agrupados por status.
    """
    return get_status_stats()

@router.get("/by-matter", summary="Processos por assunto")
def processes_by_matter():
    """
    Retorna estatísticas dos processos agrupados por assunto/matéria.
    """
    return get_matter_stats()

@router.get("/by-group", summary="Processos por grupo")
def processes_by_group():
    """
    Retorna estatísticas dos processos agrupados por grupo.
    """
    return get_group_stats()

@router.get("/by-organization", summary="Processos por organização")
def processes_by_organization():
    """
    Retorna estatísticas dos processos agrupados por organização.
    """
    return get_organization_stats()

@router.post(
    "/by-origin-with-instance-date-filter", 
    summary="Processos por periodo"
)
def processes_by_origin_with_instance_date_filter(filters: OriginDateFilter):
    return get_by_origin_with_instance_date_filter(filters)

@router.post(
    "/by-origin-registration-year-range", 
    summary="Processos de cadastro por intervalo de anos"
)
def processes_by_origin_registration_year_range(filters: YearRangeFilter):
    """
    Retorna o total de processos de origem 'Cadastro' agrupados por ano,
    dentro do intervalo especificado (start_year a end_year).
    """
    return get_by_origin_registration_by_year_range(filters)

@router.post(
    "/by-origin-registration-last-six-months",
    summary="Processos de cadastro dos últimos 6 meses do ano"
)
def processes_by_origin_registration_last_six_months(filters: YearFilter):
    """
    Retorna o total de processos de origem 'Cadastro' agrupados por mês,
    para os últimos 6 meses do ano especificado (julho a dezembro).
    """
    return get_by_origin_registration_last_six_months(filters)

@router.post(
    "/by-origin-capture-last-six-months",
    summary="Processos de captura dos últimos 6 meses do ano"
)
def processes_by_origin_capture_last_six_months(filters: YearFilter):
    """
    Retorna o total de processos de origem 'Captura' agrupados por mês,
    para os últimos 6 meses do ano especificado (julho a dezembro).
    """
    return get_by_origin_capture_last_six_months(filters)

@router.post(
    "/by-origin-distribution-last-six-months",
    summary="Processos de distribuição dos últimos 6 meses do ano"
)
def processes_by_origin_distribution_last_six_months(filters: YearFilter):
    """
    Retorna o total de processos de origem 'Distribuição' agrupados por mês,
    para os últimos 6 meses do ano especificado (julho a dezembro).
    """
    return get_by_origin_distribution_last_six_months(filters)

@router.post(
    "/by-origin-import-last-six-months",
    summary="Processos de importação dos últimos 6 meses do ano"
)
def processes_by_origin_import_last_six_months(filters: YearFilter):
    """
    Retorna o total de processos de origem 'Importação' agrupados por mês,
    para os últimos 6 meses do ano especificado (julho a dezembro).
    """
    return get_by_origin_import_last_six_months(filters)