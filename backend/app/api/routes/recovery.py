from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import RecoveryCase, AuditLog
from app.schemas.recovery_case import RecoveryCaseRead, RecoveryCaseDetail
from app.schemas.audit_log import AuditLogRead
from app.schemas.analytics import BatchAnalysisResponse
from app.schemas.recovery_execution import (
    RecoveryExecutionResponse,
    BatchRecoveryResponse,
    TimelineEventItem,
)
from app.services.recovery_case_service import RecoveryCaseService
from app.services.recovery_execution_service import RecoveryExecutionService
from app.services.recovery_analytics_service import RecoveryAnalyticsService

router = APIRouter(prefix="/recovery", tags=["Recovery Intelligence"])


@router.get(
    "/cases",
    response_model=List[RecoveryCaseRead],
    summary="List recovery cases",
    description="Retrieve paginated recovery cases with optional filtering by status.",
)
def list_recovery_cases(
    skip: int = Query(0, ge=0, description="Pagination skip offset"),
    limit: int = Query(50, ge=1, le=200, description="Pagination limit"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by case status (OPEN, IN_PROGRESS, RECOVERED, FAILED, ESCALATED, STOPPED)"),
    db: Session = Depends(get_db),
) -> List[RecoveryCaseRead]:
    query = db.query(RecoveryCase)
    if status_filter:
        query = query.filter(RecoveryCase.status == status_filter.upper())
    return query.order_by(RecoveryCase.created_at.desc()).offset(skip).limit(limit).all()


@router.get(
    "/cases/{case_id}",
    response_model=RecoveryCaseDetail,
    summary="Get recovery case detail",
    description="Retrieve full details for a recovery case including payment, failure diagnosis, and recommended recovery strategy.",
)
def get_recovery_case(
    case_id: int,
    db: Session = Depends(get_db),
) -> RecoveryCaseDetail:
    case = db.query(RecoveryCase).filter(RecoveryCase.id == case_id).first()
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recovery case #{case_id} not found.",
        )
    return case


@router.post(
    "/analyze/{payment_id}",
    response_model=RecoveryCaseDetail,
    summary="Analyze individual payment",
    description="Runs the full pipeline (revenue risk detection -> root-cause diagnosis -> feature extraction -> ML recoverability prediction -> strategy selection) for a single payment.",
)
def analyze_payment(
    payment_id: str,
    db: Session = Depends(get_db),
) -> RecoveryCaseDetail:
    # Accept either integer ID or payment_id string
    try:
        numeric_id = int(payment_id)
        case = RecoveryCaseService.create_or_update_recovery_case(numeric_id, db)
    except ValueError:
        case = RecoveryCaseService.create_or_update_recovery_case(payment_id, db)

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment '{payment_id}' could not be found for recovery analysis.",
        )
    return case


@router.post(
    "/analyze-batch",
    response_model=BatchAnalysisResponse,
    summary="Batch analyze eligible payments",
    description="Evaluates all eligible unrecovered failed, abandoned, and expired payments in batch, creating or updating recovery cases and computing aggregate salvageability.",
)
def analyze_batch_payments(
    limit: int = Query(500, ge=1, le=2000, description="Max payments to process in batch"),
    db: Session = Depends(get_db),
) -> BatchAnalysisResponse:
    results = RecoveryCaseService.analyze_batch(db, limit=limit)
    return BatchAnalysisResponse(**results)


@router.post(
    "/execute/{case_id}",
    response_model=RecoveryExecutionResponse,
    summary="Execute simulated recovery action",
    description="Executes the policy-approved recovery action in the simulation environment. Enforces idempotency and stopping rules.",
)
def execute_recovery(
    case_id: int,
    db: Session = Depends(get_db),
) -> RecoveryExecutionResponse:
    result = RecoveryExecutionService.execute_recovery_action(case_id, db)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recovery case #{case_id} not found for execution.",
        )
    return RecoveryExecutionResponse(**result)


@router.post(
    "/run-batch",
    response_model=BatchRecoveryResponse,
    summary="Run recovery across batch of cases",
    description="Processes all eligible unrecovered cases through AI investigation, policy governance, simulated recovery action execution, and outcome settlement.",
)
def run_batch_recovery(
    limit: int = Query(500, ge=1, le=2000, description="Max cases to process"),
    db: Session = Depends(get_db),
) -> BatchRecoveryResponse:
    results = RecoveryExecutionService.execute_batch_recovery(db, limit=limit)
    return BatchRecoveryResponse(**results)


@router.get(
    "/cases/{case_id}/timeline",
    response_model=List[TimelineEventItem],
    summary="Get recovery investigation and execution timeline",
    description="Returns the complete chronological history of audit events for a recovery case.",
)
def get_case_timeline(
    case_id: int,
    db: Session = Depends(get_db),
) -> List[TimelineEventItem]:
    timeline = RecoveryAnalyticsService.get_case_timeline(case_id, db)
    return [TimelineEventItem(**item) for item in timeline]


@router.get(
    "/audit-logs",
    response_model=List[AuditLogRead],
    summary="List all recovery audit logs",
    description="Returns recent system, AI, policy, and recovery execution audit logs with optional filtering.",
)
def list_audit_logs(
    skip: int = Query(0, ge=0, description="Pagination skip offset"),
    limit: int = Query(50, ge=1, le=200, description="Pagination limit"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    case_id: Optional[int] = Query(None, description="Filter by recovery case ID"),
    db: Session = Depends(get_db),
) -> List[AuditLogRead]:
    query = db.query(AuditLog)
    if event_type:
        query = query.filter(AuditLog.event_type == event_type)
    if case_id:
        query = query.filter(AuditLog.recovery_case_id == case_id)
    return query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()


@router.post(
    "/reset-demo",
    summary="Reset canonical demo scenarios (Development Only)",
    description="Resets the 5 demo cases and VIP demo case PAY_10482 to their pristine unrecovered state for rehearsals. Protected against production usage.",
)
def reset_demo_data(
    db: Session = Depends(get_db),
) -> dict:
    from app.config import settings
    from app.utils.seed_data import seed_demo_cases

    if settings.ENVIRONMENT.lower() not in ["development", "local", "test"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Resetting demo scenarios is restricted to development environments.",
        )
    seed_demo_cases(db, reset=True)
    db.commit()
    return {
        "status": "success",
        "message": "Demo cases (including PAY_10482) successfully restored to unrecovered initial state.",
    }


