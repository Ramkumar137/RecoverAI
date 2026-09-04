from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.recovery_case import RecoveryCaseRead, RecoveryCaseDetail
from app.schemas.recovery_action import RecoveryActionRead
from app.schemas.audit_log import AuditLogRead
from app.services.recovery_service import RecoveryService

router = APIRouter(prefix="/recovery-cases", tags=["Recovery Cases"])


@router.get("", response_model=List[RecoveryCaseRead])
def list_recovery_cases(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
) -> List[RecoveryCaseRead]:
    return RecoveryService.get_recovery_cases(db, skip=skip, limit=limit)


@router.get("/{case_id}", response_model=RecoveryCaseDetail)
def get_recovery_case(
    case_id: int,
    db: Session = Depends(get_db),
) -> RecoveryCaseDetail:
    case = RecoveryService.get_recovery_case_by_id(db, case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recovery case #{case_id} not found",
        )
    return case


@router.get("/{case_id}/actions", response_model=List[RecoveryActionRead])
def get_case_actions(
    case_id: int,
    db: Session = Depends(get_db),
) -> List[RecoveryActionRead]:
    return RecoveryService.get_recovery_actions_by_case(db, case_id)


@router.get("/{case_id}/audit-logs", response_model=List[AuditLogRead])
def get_case_audit_logs(
    case_id: int,
    db: Session = Depends(get_db),
) -> List[AuditLogRead]:
    return RecoveryService.get_audit_logs_by_case(db, case_id)
