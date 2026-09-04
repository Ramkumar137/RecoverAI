from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class InvestigationRequest(BaseModel):
    force_refresh: bool = Field(
        default=False,
        description="If True, re-executes AI investigation and policy evaluation even if cached results exist.",
    )


class EvidenceItem(BaseModel):
    factor: str
    impact: str
    description: str


class InvestigationResultResponse(BaseModel):
    payment_id: Optional[str] = Field(None, description="External payment ID reference, e.g. pay_demo_01_bank_timeout")
    payment_numeric_id: int = Field(..., description="Database internal primary key ID")
    recovery_case_id: int = Field(..., description="Recovery case ID")
    ai_available: bool = Field(..., description="True if Gemini 2.5 Flash performed analysis; False if deterministic fallback engaged")
    diagnosis: str = Field(..., description="Payment failure diagnosis classification")
    confidence: float = Field(..., description="Investigation confidence score (0.0 to 1.0)")
    summary: str = Field(..., description="Executive summary of the failure and recovery trajectory")
    evidence: List[Dict[str, Any]] = Field(default_factory=list, description="Telemetry factors backing diagnosis and recommendation")
    ai_recommended_action: str = Field(..., description="Action proposed by the AI Agent")
    ai_rationale: Optional[str] = Field(None, description="Detailed reasoning provided by the AI Agent")
    policy_result: str = Field(..., description="Policy Engine ruling: ALLOWED or DENIED")
    final_action: str = Field(..., description="Binding recovery action decided by the deterministic Policy Engine")
    policy_applied: str = Field(..., description="Policy rule identifier applied during governance")
    policy_reason: str = Field(..., description="Justification explaining approval or override")
    escalation_required: bool = Field(..., description="Flag indicating if manual human intervention is required")
    recovery_channel: Optional[str] = Field(None, description="Suggested channel: SMS, WHATSAPP, EMAIL, GATEWAY_RETRY")
    wait_time_minutes: Optional[int] = Field(0, description="Recommended delay before action execution")
    recoverability_score: float = Field(..., description="ML recoverability prediction (0.0 to 100.0)")
    revenue_at_risk: float = Field(..., description="Amount of revenue at risk")
    status: str = Field(..., description="Recovery case lifecycle status")
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
