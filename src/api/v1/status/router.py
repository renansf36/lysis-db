from fastapi import APIRouter
from fastapi.responses import JSONResponse

from ....services.status.service import get_db_status

router = APIRouter(prefix="/api/v1", tags=["Status"])


@router.get("/status")
def database_status():
    try:
        payload = get_db_status()
        return JSONResponse(status_code=200, content=payload)
    except Exception as exc:
        return JSONResponse(
            status_code=503,
            content={
                "status": "offline",
                "error": str(exc),
            },
        )
