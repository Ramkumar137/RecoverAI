from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.ai_investigation import InvestigationResultResponse, InvestigationRequest
from app.services.investigation_service import InvestigationService

router = APIRouter(prefix="/ai", tags=["AI Recovery Agent"])


@router.post(
    "/investigate/{payment_id}",
    response_model=InvestigationResultResponse,
    summary="Investigate payment failure with Gemini AI Agent",
    description="Invokes the RecoverAI Gemini 2.5 Flash agent to investigate the payment failure, perform telemetry analysis, suggest optimal recovery action, and validate through the deterministic Policy Engine.",
)
def investigate_payment(
    payment_id: str,
    force_refresh: bool = Query(False, description="Whether to bypass cache and re-run Gemini AI analysis"),
    db: Session = Depends(get_db),
) -> InvestigationResultResponse:
    result = InvestigationService.investigate_payment(
        payment_id=payment_id,
        db=db,
        force_refresh=force_refresh,
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment '{payment_id}' not found for AI investigation.",
        )

    return InvestigationResultResponse(**result)


@router.get(
    "/investigations/{payment_id}",
    response_model=InvestigationResultResponse,
    summary="Get existing AI investigation report",
    description="Fetches the previously conducted AI forensic investigation report, evidence factors, and policy decision for a payment.",
)
def get_investigation_report(
    payment_id: str,
    db: Session = Depends(get_db),
) -> InvestigationResultResponse:
    result = InvestigationService.get_investigation(
        payment_id=payment_id,
        db=db,
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No AI investigation found for payment '{payment_id}'. Initiate investigation via POST /api/ai/investigate/{payment_id}.",
        )

    return InvestigationResultResponse(**result)
