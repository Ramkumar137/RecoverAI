from sqlalchemy import Column, Integer, String, Numeric, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.enums import RecoveryActionType, ActionExecutionStatus


class RecoveryAction(Base):
    __tablename__ = "recovery_actions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    recovery_case_id = Column(Integer, ForeignKey("recovery_cases.id", ondelete="CASCADE"), nullable=False, index=True)
    action_type = Column(
        SQLEnum(RecoveryActionType, name="recovery_action_type_enum"),
        nullable=False,
        index=True,
    )
    reason = Column(Text, nullable=True)
    status = Column(
        SQLEnum(ActionExecutionStatus, name="action_execution_status_enum"),
        default=ActionExecutionStatus.PENDING,
        nullable=False,
        index=True,
    )
    executed_at = Column(DateTime(timezone=True), nullable=True)
    result = Column(Text, nullable=True)
    recovered_amount = Column(Numeric(12, 2), default=0.00, nullable=False)

    # Relationships
    recovery_case = relationship("RecoveryCase", back_populates="recovery_actions")

    def __repr__(self) -> str:
        return f"<RecoveryAction(id={self.id}, case_id={self.recovery_case_id}, action='{self.action_type}', status='{self.status}')>"
