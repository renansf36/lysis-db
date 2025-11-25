from fastapi import APIRouter

from ....services.processes.service import (
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
