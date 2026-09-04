from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Payment, Customer, PaymentStatus
from app.schemas.payment import PaymentRead, PaymentDetail

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.get(
    "",
    response_model=List[PaymentRead],
    summary="List payments",
    description="Retrieve paginated payment transactions with optional status, failure reason, and keyword search filtering.",
)
def list_payments(
    skip: int = Query(0, ge=0, description="Pagination skip offset"),
    limit: int = Query(50, ge=1, le=200, description="Pagination limit"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by payment status (SUCCESS, FAILED, PENDING, ABANDONED, EXPIRED, RECOVERED)"),
    failure_reason: Optional[str] = Query(None, description="Filter by failure reason (e.g. BANK_TIMEOUT, INSUFFICIENT_FUNDS)"),
    search: Optional[str] = Query(None, description="Search by payment reference, customer name, or email"),
    db: Session = Depends(get_db),
) -> List[PaymentRead]:
    query = db.query(Payment)
    if status_filter:
        query = query.filter(Payment.status == status_filter.upper())
    if failure_reason:
        query = query.filter(Payment.failure_reason == failure_reason.upper())
    if search:
        search_term = f"%{search.strip()}%"
        query = query.join(Payment.customer).filter(
            (Payment.payment_id.ilike(search_term))
            | (Customer.name.ilike(search_term))
            | (Customer.email.ilike(search_term))
        )
    return query.order_by(Payment.created_at.desc()).offset(skip).limit(limit).all()


@router.get(
    "/{payment_id}",
    response_model=PaymentDetail,
    summary="Get payment details",
    description="Retrieve a single payment's complete metadata including customer profile and merchant context by internal ID or payment reference string.",
)
def get_payment(
    payment_id: str,
    db: Session = Depends(get_db),
) -> PaymentDetail:
    # Try finding by numeric primary key or reference string
    payment = None
    try:
        numeric_id = int(payment_id)
        payment = db.query(Payment).filter(Payment.id == numeric_id).first()
    except ValueError:
        pass

    if not payment:
        payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment '{payment_id}' not found.",
        )
    return payment
