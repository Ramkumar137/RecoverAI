from datetime import datetime, timezone
from typing import Set, Dict
from app.models.enums import RecoveryCaseStatus
from app.models.recovery_case import RecoveryCase


class InvalidStateTransitionError(Exception):
    """Raised when an illegal state transition is attempted on a RecoveryCase."""
    pass


class RecoveryCaseStateMachine:
    """
    Formal state machine governing RecoveryCase lifecycle.
    Prevents unauthorized state transitions and ensures linear compliance.
    """

    # Allowed forward/branching transitions
    VALID_TRANSITIONS: Dict[RecoveryCaseStatus, Set[RecoveryCaseStatus]] = {
        RecoveryCaseStatus.OPEN: {
            RecoveryCaseStatus.INVESTIGATING,
            RecoveryCaseStatus.RECOVERY_RECOMMENDED,
            RecoveryCaseStatus.ACTION_APPROVED,
            RecoveryCaseStatus.STOPPED,
            RecoveryCaseStatus.ESCALATED,
            RecoveryCaseStatus.IN_PROGRESS,
        },
        RecoveryCaseStatus.INVESTIGATING: {
            RecoveryCaseStatus.RECOVERY_RECOMMENDED,
            RecoveryCaseStatus.ACTION_APPROVED,
            RecoveryCaseStatus.ESCALATED,
            RecoveryCaseStatus.STOPPED,
        },
        RecoveryCaseStatus.RECOVERY_RECOMMENDED: {
            RecoveryCaseStatus.ACTION_APPROVED,
            RecoveryCaseStatus.ESCALATED,
            RecoveryCaseStatus.STOPPED,
        },
        RecoveryCaseStatus.ACTION_APPROVED: {
            RecoveryCaseStatus.ACTION_EXECUTED,
            RecoveryCaseStatus.ESCALATED,
            RecoveryCaseStatus.STOPPED,
        },
        RecoveryCaseStatus.ACTION_EXECUTED: {
            RecoveryCaseStatus.RECOVERED,
            RecoveryCaseStatus.FAILED,
            RecoveryCaseStatus.ESCALATED,
            RecoveryCaseStatus.STOPPED,
        },
        RecoveryCaseStatus.FAILED: {
            RecoveryCaseStatus.INVESTIGATING,
            RecoveryCaseStatus.ACTION_APPROVED,
            RecoveryCaseStatus.ACTION_EXECUTED,
            RecoveryCaseStatus.ESCALATED,
            RecoveryCaseStatus.STOPPED,
        },
        RecoveryCaseStatus.IN_PROGRESS: {
            RecoveryCaseStatus.INVESTIGATING,
            RecoveryCaseStatus.RECOVERY_RECOMMENDED,
            RecoveryCaseStatus.ACTION_APPROVED,
            RecoveryCaseStatus.ACTION_EXECUTED,
            RecoveryCaseStatus.RECOVERED,
            RecoveryCaseStatus.FAILED,
            RecoveryCaseStatus.ESCALATED,
            RecoveryCaseStatus.STOPPED,
            RecoveryCaseStatus.CLOSED,
        },
        # Terminal states
        RecoveryCaseStatus.RECOVERED: set(),
        RecoveryCaseStatus.ESCALATED: set(),
        RecoveryCaseStatus.STOPPED: set(),
        RecoveryCaseStatus.CLOSED: set(),
    }

    @classmethod
    def can_transition(cls, from_status: RecoveryCaseStatus, to_status: RecoveryCaseStatus) -> bool:
        if from_status == to_status:
            return True
        allowed = cls.VALID_TRANSITIONS.get(from_status, set())
        return to_status in allowed

    @classmethod
    def transition(cls, case: RecoveryCase, to_status: RecoveryCaseStatus) -> RecoveryCase:
        from_status = case.status
        if from_status == to_status:
            return case

        if not cls.can_transition(from_status, to_status):
            raise InvalidStateTransitionError(
                f"Invalid RecoveryCase state transition from '{from_status.value}' to '{to_status.value}'."
            )

        case.status = to_status
        case.updated_at = datetime.now(timezone.utc)
        return case
