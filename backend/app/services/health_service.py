from typing import Dict
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.utils.logger import logger


class HealthService:
    @staticmethod
    def get_health_status() -> Dict[str, str]:
        """
        Returns basic service health status adhering to API contract.
        """
        return {
            "status": "ok",
            "service": "RecoverAI",
        }

    @staticmethod
    def check_database_health(db: Session) -> bool:
        """
        Validates whether PostgreSQL connection is alive.
        """
        try:
            db.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
