from typing import List, Optional
from pydantic import BaseModel, Field


class EvidenceFactor(BaseModel):
    factor: str = Field(description="Name or key signal of the evidence factor, e.g., 'Customer Success Rate'")
    impact: str = Field(description="Impact classification: POSITIVE, NEGATIVE, or NEUTRAL")
    description: str = Field(description="Specific finding or rationale for how this signal influences recoverability")


class AIInvestigationResponse(BaseModel):
    diagnosis: str = Field(
        description="High-level root-cause diagnosis (e.g. TEMPORARY_BANK_FAILURE, INSUFFICIENT_FUNDS, CHECKOUT_ABANDONMENT, PAYMENT_METHOD_DECLINED, PAYMENT_LIMIT_EXCEEDED, UNSPECIFIED_FAILURE)"
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score in the diagnosis and recommendation between 0.0 and 1.0",
    )
    summary: str = Field(
        description="Comprehensive 2-4 sentence executive summary of what happened, root cause, and customer context."
    )
    evidence: List[EvidenceFactor] = Field(
        default_factory=list,
        description="Key evidence factors supporting the diagnosis and chosen recovery strategy",
    )
    recommended_action: str = Field(
        description="Recommended action type: RETRY_PAYMENT, RETRY_LATER, SEND_PAYMENT_LINK, SEND_REMINDER, CHANGE_PAYMENT_METHOD, ESCALATE_TO_HUMAN, or STOP_RECOVERY"
    )
    recommended_action_rationale: str = Field(
        description="Clear justification explaining why this specific action is the optimal recovery path"
    )
    recovery_channel: Optional[str] = Field(
        default=None,
        description="Recommended execution channel, e.g., SMS, WHATSAPP, EMAIL, IN_APP, GATEWAY_RETRY",
    )
    wait_time_minutes: Optional[int] = Field(
        default=0,
        description="Recommended cooldown or delay window in minutes before initiating recovery action (e.g. 30 for bank timeout)",
    )
