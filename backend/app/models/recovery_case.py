from sqlalchemy import Column, Integer, String, Numeric, Float, Text, DateTime, ForeignKey, Enum as SQLEnum, JSON, Boolean, text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.enums import RecoveryCaseStatus


class RecoveryCase(Base):
    __tablename__ = "recovery_cases"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    payment_id = Column(Integer, ForeignKey("payments.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    revenue_at_risk = Column(Numeric(12, 2), nullable=False)
    recoverability_score = Column(Float, default=0.0, nullable=False)  # 0.0 to 100.0
    diagnosis = Column(Text, nullable=True)
    recommended_action = Column(String(100), nullable=True)
    status = Column(
        SQLEnum(RecoveryCaseStatus, name="recovery_case_status_enum"),
        default=RecoveryCaseStatus.OPEN,
        nullable=False,
        index=True,
    )
    recovered_amount = Column(Numeric(12, 2), default=0.00, nullable=False)

    # AI Investigation Fields (Phase 3)
    ai_diagnosis = Column(String(100), nullable=True)
    ai_confidence = Column(Float, nullable=True)  # 0.0 to 1.0
    ai_summary = Column(Text, nullable=True)
    ai_evidence = Column(JSON, nullable=True)
    ai_recommended_action = Column(String(50), nullable=True)
    policy_result = Column(String(20), nullable=True)  # "ALLOWED" or "DENIED"
    final_action = Column(String(50), nullable=True)
    escalation_required = Column(Boolean, default=False, server_default=text('false'), nullable=False)
    recovery_attempts = Column(Integer, default=0, server_default=text('0'), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    payment = relationship("Payment", back_populates="recovery_case")
    recovery_actions = relationship("RecoveryAction", back_populates="recovery_case", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="recovery_case", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<RecoveryCase(id={self.id}, payment_id={self.payment_id}, score={self.recoverability_score}, final_action='{self.final_action}')>"
