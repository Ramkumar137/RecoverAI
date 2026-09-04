from typing import List, Optional
from sqlalchemy.orm import Session
from app.models import RecoveryCase, RecoveryAction, AuditLog
from app.schemas.recovery_case import RecoveryCaseRead, RecoveryCaseDetail
from app.schemas.recovery_action import RecoveryActionRead


class RecoveryService:
    @staticmethod
    def get_recovery_cases(db: Session, skip: int = 0, limit: int = 100) -> List[RecoveryCase]:
        return db.query(RecoveryCase).offset(skip).limit(limit).all()

    @staticmethod
    def get_recovery_case_by_id(db: Session, case_id: int) -> Optional[RecoveryCase]:
        return db.query(RecoveryCase).filter(RecoveryCase.id == case_id).first()

    @staticmethod
    def get_recovery_actions_by_case(db: Session, case_id: int) -> List[RecoveryAction]:
        return db.query(RecoveryAction).filter(RecoveryAction.recovery_case_id == case_id).all()

    @staticmethod
    def get_audit_logs_by_case(db: Session, case_id: int) -> List[AuditLog]:
        return db.query(AuditLog).filter(AuditLog.recovery_case_id == case_id).order_by(AuditLog.created_at.desc()).all()
