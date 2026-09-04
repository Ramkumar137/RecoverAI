from typing import Optional
from google import genai
from google.genai import types
from app.config import settings
from app.agents.schemas import AIInvestigationResponse, EvidenceFactor
from app.agents.investigation_context import InvestigationContext
from app.utils.logger import logger


class GeminiAgent:
    """
    Autonomous AI Revenue Recovery Agent powered by Google Gemini (gemini-2.5-flash).
    Conducts forensic payment failure investigation, calculates confidence, evaluates
    evidence factors, and recommends optimal recovery interventions.
    Includes deterministic fallback mode for offline, air-gapped, or rate-limited environments.
    """

    SYSTEM_INSTRUCTION = """You are the Senior Revenue Recovery & Payment Intelligence Analyst for RecoverAI, an autonomous enterprise revenue recovery platform for Razorpay merchants.

Your mission is to perform a rigorous forensic investigation of failed, abandoned, or at-risk payment transactions. You must evaluate the telemetry, identify the true root cause, gauge recoverability probability, and prescribe the optimal, bounded recovery strategy.

Operational Guidelines & Principles:
1. Root Cause Diagnosis: Pinpoint why the transaction was interrupted (e.g. TEMPORARY_BANK_FAILURE, INSUFFICIENT_FUNDS, CHECKOUT_ABANDONMENT, PAYMENT_METHOD_DECLINED, PAYMENT_LIMIT_EXCEEDED, UNSPECIFIED_FAILURE).
2. Recommended Action: Select strictly one from the following standard recovery actions:
   - RETRY_PAYMENT: Immediate gateway retry for transient network drops on initial attempt (retry_count == 0).
   - RETRY_LATER: Scheduled retry after a cooldown window (15-60 min) for transient bank switch congestion or liquidity cycles.
   - SEND_PAYMENT_LINK: Multi-channel payment link dispatch via WhatsApp/SMS/Email, ideal for insufficient funds or alternative funding.
   - SEND_REMINDER: Gentle conversational nudge for abandoned checkouts with high buyer intent.
   - CHANGE_PAYMENT_METHOD: Prompt customer to select an alternative payment method (UPI, Netbanking, alternative Card) when the current instrument is declined or blocked.
   - ESCALATE_TO_HUMAN: Routing to VIP merchant account teams for high-value transactions (>₹10,000) or chronic failures.
   - STOP_RECOVERY: Cease all recovery activity immediately if max automated attempts (>= 3) are reached or recoverability is hopeless to protect merchant reputation and prevent bank penalties.
3. Safety Rules:
   - Never recommend RETRY_PAYMENT or RETRY_LATER on a hard card decline (CARD_DECLINED) or limit exceeded (LIMIT_EXCEEDED).
   - If retry_count >= 3, always recommend STOP_RECOVERY.
4. Output Format:
   - Produce strictly valid JSON matching the AIInvestigationResponse schema.
   - Provide 3-5 distinct EvidenceFactor items highlighting key positive and negative signals (customer loyalty, ticket size, retries, failure type).
   - Provide an executive summary explaining what happened and why this recovery path was chosen.
"""

    @classmethod
    def investigate(cls, context: InvestigationContext) -> tuple[AIInvestigationResponse, bool]:
        """
        Executes forensic investigation using Gemini 2.5 Flash.
        Returns a tuple of (AIInvestigationResponse, ai_available: bool).
        Falls back seamlessly to calibrated deterministic recovery if API is unreachable.
        """
        api_key = settings.GEMINI_API_KEY
        if not api_key or api_key.strip() == "" or "placeholder" in api_key.lower():
            logger.info("No valid Gemini API key configured. Executing deterministic fallback investigation.")
            return cls.generate_fallback_investigation(context), False

        try:
            client = genai.Client(api_key=api_key)
            prompt = context.to_prompt_text()

            logger.info(f"Dispatching forensic investigation to Gemini for payment {context.payment.get('payment_id')}")

            # Resilient model cascade to handle upstream high-demand spikes
            models_to_try = ["gemini-3.6-flash", "gemini-3.7-flash"]
            last_err = None

            for model_name in models_to_try:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=cls.SYSTEM_INSTRUCTION,
                            response_mime_type="application/json",
                            response_json_schema=AIInvestigationResponse.model_json_schema(),
                            temperature=0.2,
                        ),
                    )

                    if response and response.text:
                        parsed = AIInvestigationResponse.model_validate_json(response.text)
                        logger.info(f"Gemini ({model_name}) investigation completed successfully: {parsed.diagnosis} -> {parsed.recommended_action}")
                        return parsed, True
                    else:
                        logger.warning(f"Gemini ({model_name}) returned empty response.")
                except Exception as model_err:
                    last_err = model_err
                    logger.warning(f"Gemini API attempt on '{model_name}' failed: {model_err}. Trying alternate model...")

            logger.error(f"All Gemini models unavailable (last error: {last_err}). Executing deterministic fallback.")
            return cls.generate_fallback_investigation(context), False

        except Exception as e:
            logger.error(f"Gemini API initialization/investigation failed: {e}. Executing deterministic fallback.")
            return cls.generate_fallback_investigation(context), False

    @classmethod
    def generate_fallback_investigation(cls, context: InvestigationContext) -> AIInvestigationResponse:
        """
        Deterministic, robust fallback investigation when LLM is unavailable.
        Synthesizes expert insights from the ML recoverability model and rule engine.
        """
        p = context.payment
        c = context.customer
        ml = context.ml_prediction
        diag = context.deterministic_diagnosis
        strat = context.deterministic_strategy

        diagnosis = diag.get("diagnosis", "UNSPECIFIED_FAILURE")
        score = ml.get("score", 50.0)
        confidence = round(max(0.35, min(0.95, score / 100.0)), 2)
        action = strat.get("action_type", "SEND_PAYMENT_LINK")
        amount = p.get("amount", 0.0)
        retries = p.get("retry_count", 0)
        success_rate = c.get("success_rate", 0.8)

        # Build evidence factors
        evidence = []

        # Customer reliability factor
        if success_rate >= 0.8:
            evidence.append(
                EvidenceFactor(
                    factor="Customer Reliability",
                    impact="POSITIVE",
                    description=f"Customer has a solid track record with {success_rate * 100:.1f}% success rate across {c.get('total_payments', 0)} transactions.",
                )
            )
        elif success_rate < 0.5:
            evidence.append(
                EvidenceFactor(
                    factor="Historical Friction",
                    impact="NEGATIVE",
                    description=f"Low historical success rate ({success_rate * 100:.1f}%) indicates frequent payment difficulties.",
                )
            )

        # Failure reason factor
        evidence.append(
            EvidenceFactor(
                factor="Failure Mechanism",
                impact="POSITIVE" if diag.get("retry_appropriate", True) else "NEGATIVE",
                description=f"{diag.get('explanation')} classified as {diag.get('severity')} severity.",
            )
        )

        # Retries factor
        if retries >= 3:
            evidence.append(
                EvidenceFactor(
                    factor="Maximum Retries Exceeded",
                    impact="NEGATIVE",
                    description=f"Payment has failed {retries} consecutive automated attempts, triggering hard recovery termination.",
                )
            )
        elif retries > 0:
            evidence.append(
                EvidenceFactor(
                    factor="Retry History",
                    impact="NEGATIVE",
                    description=f"Payment has already undergone {retries} retry attempts without resolution.",
                )
            )

        # Ticket size factor
        if amount >= 10000:
            evidence.append(
                EvidenceFactor(
                    factor="High-Value Exposure",
                    impact="NEUTRAL",
                    description=f"Transaction value ₹{amount:,.2f} represents high merchant revenue impact warranting proactive retention.",
                )
            )

        # Construct summary
        summary = (
            f"Payment of ₹{amount:,.2f} failed due to {diagnosis} ({diag.get('explanation')}). "
            f"Customer {c.get('name', 'Unknown')} has {c.get('total_payments', 0)} lifetime transactions with a {success_rate * 100:.1f}% success rate. "
            f"Machine learning models predict a {score:.1f}% recoverability score. "
            f"Recommended strategy: {action} ({strat.get('reason')})."
        )

        # Determine wait time and channel
        wait_time = 30 if action == "RETRY_LATER" else 0
        channel_map = {
            "RETRY_PAYMENT": "GATEWAY_RETRY",
            "RETRY_LATER": "GATEWAY_RETRY",
            "SEND_PAYMENT_LINK": "WHATSAPP",
            "SEND_REMINDER": "SMS",
            "CHANGE_PAYMENT_METHOD": "IN_APP",
            "ESCALATE_TO_HUMAN": "VIP_SUPPORT",
            "STOP_RECOVERY": "INTERNAL_LOG",
        }

        return AIInvestigationResponse(
            diagnosis=diagnosis,
            confidence=confidence,
            summary=summary,
            evidence=evidence,
            recommended_action=action,
            recommended_action_rationale=strat.get("reason", "Standard algorithmic recovery routing."),
            recovery_channel=channel_map.get(action, "WHATSAPP"),
            wait_time_minutes=wait_time,
        )
