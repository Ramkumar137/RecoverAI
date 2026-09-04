from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.health_service import HealthService

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=Dict[str, str])
def health_check() -> Dict[str, str]:
    """
    Standard health check endpoint.
    Expected response:
    {
        "status": "ok",
        "service": "RecoverAI"
    }
    """
    return HealthService.get_health_status()


@router.get("/health/system", response_model=Dict[str, Any])
def system_health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Comprehensive system health check including database connection.
    """
    db_alive = HealthService.check_database_health(db)
    return {
        "status": "ok" if db_alive else "degraded",
        "service": "RecoverAI",
        "components": {
            "api": "healthy",
            "database": "connected" if db_alive else "unreachable",
        },
    }
