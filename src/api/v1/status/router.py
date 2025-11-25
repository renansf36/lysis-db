from fastapi import APIRouter
from ....services.status.service import get_db_status

router = APIRouter(prefix="/api/v1", tags=["Status"])

@router.get("/status")
def database_status():
    """
    Retorna informações de diagnóstico do SQL Server:
    - Versão
    - Máximo de conexões
    - Conexões ativas
    - Tempo de atividade
    """
    return get_db_status()
