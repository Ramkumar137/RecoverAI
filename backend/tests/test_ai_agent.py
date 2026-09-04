from unittest.mock import patch, MagicMock
import pytest
from app.agents.investigation_tools import (
    get_customer_profile,
    get_payment_details,
    get_payment_history,
    get_failure_history,
    get_recovery_history,
    get_subscription_status,
    get_customer_payment_patterns,
)
from app.agents.investigation_context import InvestigationContextBuilder, InvestigationContext
from app.agents.schemas import AIInvestigationResponse, EvidenceFactor
from app.agents.gemini_agent import GeminiAgent
from app.recovery.policy_engine import PolicyEngine
from app.models.enums import RecoveryActionType


# ==========================================
# 1. Investigation Tools Tests
# ==========================================

def test_investigation_tools_read_only(db_session):
    # Test get_payment_details with demo payment
    payment = get_payment_details("pay_demo_01_bank_timeout", db_session)
    assert payment is not None
    assert payment["payment_id"] == "pay_demo_01_bank_timeout"
    assert payment["amount"] > 0
    assert "customer_id" in payment

    # Test get_customer_profile
    customer = get_customer_profile(payment["customer_id"], db_session)
    assert customer is not None
    assert "success_rate" in customer
    assert "total_payments" in customer

    # Test get_payment_history
    history = get_payment_history(payment["customer_id"], db_session, limit=5)
    assert isinstance(history, list)
    assert len(history) > 0

    # Test get_failure_history
    failures = get_failure_history(payment["customer_id"], db_session)
    assert isinstance(failures, list)

    # Test get_recovery_history
    recovery_hist = get_recovery_history(payment["customer_id"], db_session)
    assert isinstance(recovery_hist, list)

    # Test get_subscription_status
    subs = get_subscription_status(payment["customer_id"], db_session)
    assert isinstance(subs, list)

    # Test get_customer_payment_patterns
    patterns = get_customer_payment_patterns(payment["customer_id"], db_session)
    assert "preferred_method" in patterns
    assert "method_distribution" in patterns
    assert "failure_rate_by_method" in patterns


def test_investigation_tools_graceful_missing_records(db_session):
    assert get_payment_details("non_existent_pay_id_99999", db_session) is None
    assert get_customer_profile("non_existent_cust_id", db_session) == {}
    assert get_payment_history(999999, db_session) == []
    assert get_failure_history(999999, db_session) == []
    assert get_recovery_history(999999, db_session) == []
    assert get_subscription_status(999999, db_session) == []
    patterns = get_customer_payment_patterns(999999, db_session)
    assert patterns["total_recorded"] == 0


# ==========================================
# 2. Context Builder Tests
# ==========================================

def test_investigation_context_builder(db_session):
    context = InvestigationContextBuilder.build("pay_demo_01_bank_timeout", db_session)
    assert context is not None
    assert context.payment["payment_id"] == "pay_demo_01_bank_timeout"
    assert "score" in context.ml_prediction
    assert "diagnosis" in context.deterministic_diagnosis
    assert "action_type" in context.deterministic_strategy

    prompt_text = context.to_prompt_text()
    assert "CURRENT TRANSACTION UNDER INVESTIGATION" in prompt_text
    assert "pay_demo_01_bank_timeout" in prompt_text


# ==========================================
# 3. Policy Engine Safety Rules Tests
# ==========================================

def test_policy_engine_max_retries_override(db_session):
    context = InvestigationContextBuilder.build("pay_demo_05_max_retries_halted", db_session)
    assert context is not None
    assert context.payment["retry_count"] >= 3

    # AI tries to recommend retry
    ai_proposal = AIInvestigationResponse(
        diagnosis="TEMPORARY_BANK_FAILURE",
        confidence=0.9,
        summary="Transient issue, should retry.",
        evidence=[],
        recommended_action="RETRY_PAYMENT",
        recommended_action_rationale="Retry will likely succeed.",
    )

    policy_result = PolicyEngine.evaluate(context, ai_proposal)
    assert policy_result.result == "DENIED"
    assert policy_result.final_action == RecoveryActionType.STOP_RECOVERY.value
    assert "OVERRIDE_MAX_RETRIES_EXCEEDED" in policy_result.policy_applied


def test_policy_engine_max_retries_compliant(db_session):
    context = InvestigationContextBuilder.build("pay_demo_05_max_retries_halted", db_session)
    assert context is not None

    # AI recommends STOP_RECOVERY
    ai_proposal = AIInvestigationResponse(
        diagnosis="MAX_RETRIES_REACHED",
        confidence=0.95,
        summary="Too many attempts.",
        evidence=[],
        recommended_action="STOP_RECOVERY",
        recommended_action_rationale="Protect customer experience.",
    )

    policy_result = PolicyEngine.evaluate(context, ai_proposal)
    assert policy_result.result == "ALLOWED"
    assert policy_result.final_action == RecoveryActionType.STOP_RECOVERY.value
    assert policy_result.policy_applied == "POLICY_MAX_RETRIES_COMPLIANT"


def test_policy_engine_card_decline_no_retry(db_session):
    context = InvestigationContextBuilder.build("pay_demo_03_card_declined", db_session)
    assert context is not None

    # AI hallucinates a retry on hard card decline
    ai_proposal = AIInvestigationResponse(
        diagnosis="PAYMENT_METHOD_DECLINED",
        confidence=0.8,
        summary="Card declined, trying again.",
        evidence=[],
        recommended_action="RETRY_PAYMENT",
        recommended_action_rationale="Retry transaction.",
    )

    policy_result = PolicyEngine.evaluate(context, ai_proposal)
    assert policy_result.result == "DENIED"
    assert policy_result.final_action in [
        RecoveryActionType.CHANGE_PAYMENT_METHOD.value,
        RecoveryActionType.ESCALATE_TO_HUMAN.value,
    ]
    assert "OVERRIDE_CARD_DECLINE_NO_RETRY" in policy_result.policy_applied


def test_policy_engine_allowed_recommendation(db_session):
    context = InvestigationContextBuilder.build("pay_demo_01_bank_timeout", db_session)
    assert context is not None

    ai_proposal = AIInvestigationResponse(
        diagnosis="TEMPORARY_BANK_FAILURE",
        confidence=0.88,
        summary="Bank timeout detected with high recoverability.",
        evidence=[],
        recommended_action="RETRY_LATER",
        recommended_action_rationale="Retry after 30 min cooldown.",
    )

    policy_result = PolicyEngine.evaluate(context, ai_proposal)
    assert policy_result.result == "ALLOWED"
    assert policy_result.final_action == RecoveryActionType.RETRY_LATER.value
    assert policy_result.policy_applied == "AI_RECOMMENDATION_APPROVED"


# ==========================================
# 4. Gemini Agent & Fallback Mode Tests
# ==========================================

def test_gemini_agent_fallback_mode(db_session):
    context = InvestigationContextBuilder.build("pay_demo_02_insufficient_funds", db_session)
    assert context is not None

    fallback = GeminiAgent.generate_fallback_investigation(context)
    assert isinstance(fallback, AIInvestigationResponse)
    assert fallback.diagnosis == "INSUFFICIENT_FUNDS"
    assert fallback.recommended_action == RecoveryActionType.SEND_PAYMENT_LINK.value
    assert fallback.confidence > 0.0
    assert len(fallback.evidence) > 0


def test_gemini_agent_mocked_llm(db_session):
    context = InvestigationContextBuilder.build("pay_demo_01_bank_timeout", db_session)

    mock_llm_json = """{
        "diagnosis": "TEMPORARY_BANK_FAILURE",
        "confidence": 0.92,
        "summary": "Forensic audit confirms the issuing bank gateway timed out.",
        "evidence": [
            {"factor": "Bank Gateway", "impact": "NEGATIVE", "description": "HDFC switch latency exceeded 15s."},
            {"factor": "Customer Loyalty", "impact": "POSITIVE", "description": "Customer has 95% historical success."}
        ],
        "recommended_action": "RETRY_LATER",
        "recommended_action_rationale": "Retry in 30 minutes after switch clears.",
        "recovery_channel": "GATEWAY_RETRY",
        "wait_time_minutes": 30
    }"""

    with patch("app.agents.gemini_agent.settings.GEMINI_API_KEY", "test_key_12345"):
        with patch("app.agents.gemini_agent.genai.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.text = mock_llm_json
            mock_client.models.generate_content.return_value = mock_response
            mock_client_class.return_value = mock_client

            result, ai_available = GeminiAgent.investigate(context)
            assert ai_available is True
            assert result.diagnosis == "TEMPORARY_BANK_FAILURE"
            assert result.recommended_action == "RETRY_LATER"
            assert result.confidence == 0.92
            assert len(result.evidence) == 2


# ==========================================
# 5. API Endpoints & Demo Cases Integration
# ==========================================

def test_ai_investigate_endpoint_demo_cases(client):
    demo_cases = [
        ("pay_demo_01_bank_timeout", "TEMPORARY_BANK_FAILURE", "RETRY_LATER"),
        ("pay_demo_02_insufficient_funds", "INSUFFICIENT_FUNDS", "SEND_PAYMENT_LINK"),
        ("pay_demo_03_card_declined", "PAYMENT_METHOD_DECLINED", "CHANGE_PAYMENT_METHOD"),
        ("pay_demo_04_checkout_abandoned", "CHECKOUT_ABANDONMENT", "SEND_REMINDER"),
        ("pay_demo_05_max_retries_halted", "INSUFFICIENT_FUNDS", "STOP_RECOVERY"),
    ]

    with patch("app.services.investigation_service.GeminiAgent.investigate") as mock_investigate:
        def side_effect(ctx):
            fb = GeminiAgent.generate_fallback_investigation(ctx)
            return fb, False

        mock_investigate.side_effect = side_effect

        for payment_id, expected_diag, expected_final_action in demo_cases:
            response = client.post(f"/api/ai/investigate/{payment_id}?force_refresh=true")
            assert response.status_code == 200, f"Failed for {payment_id}: {response.text}"
            data = response.json()
            assert data["payment_id"] == payment_id
            assert "recovery_case_id" in data
            assert "confidence" in data
            assert "summary" in data
            assert "evidence" in data
            assert "policy_result" in data
            assert "final_action" in data

            if payment_id == "pay_demo_03_card_declined":
                assert data["final_action"] in [
                    RecoveryActionType.CHANGE_PAYMENT_METHOD.value,
                    RecoveryActionType.ESCALATE_TO_HUMAN.value,
                ]
            elif payment_id == "pay_demo_05_max_retries_halted":
                assert data["final_action"] == "STOP_RECOVERY"
            else:
                assert data["final_action"] == expected_final_action


def test_get_existing_ai_investigation_endpoint(client):
    with patch("app.services.investigation_service.GeminiAgent.investigate") as mock_investigate:
        def side_effect(ctx):
            fb = GeminiAgent.generate_fallback_investigation(ctx)
            return fb, False

        mock_investigate.side_effect = side_effect

        # Investigate first
        client.post("/api/ai/investigate/pay_demo_01_bank_timeout?force_refresh=true")

        # Fetch investigation
        response = client.get("/api/ai/investigations/pay_demo_01_bank_timeout")
        assert response.status_code == 200
        data = response.json()
        assert data["payment_id"] == "pay_demo_01_bank_timeout"
        assert data["diagnosis"] in ["TEMPORARY_BANK_FAILURE", "BANK_TIMEOUT"]
        assert "evidence" in data
        assert len(data["evidence"]) > 0


def test_ai_investigation_not_found(client):
    response = client.post("/api/ai/investigate/invalid_pay_id_999999")
    assert response.status_code == 404

    response_get = client.get("/api/ai/investigations/invalid_pay_id_999999")
    assert response_get.status_code == 404
