from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    recovery_case_id = Column(Integer, ForeignKey("recovery_cases.id", ondelete="SET NULL"), nullable=True, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=False)
    actor = Column(String(100), default="SYSTEM", nullable=False)
    metadata_ = Column("metadata", JSON, nullable=True)  # 'metadata' is a reserved attribute on DeclarativeBase
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    recovery_case = relationship("RecoveryCase", back_populates="audit_logs")

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, event_type='{self.event_type}', actor='{self.actor}')>"
