import os
from typing import Dict, Tuple, Optional
import numpy as np
import joblib
from app.ml.feature_extractor import FeatureExtractor
from app.utils.logger import logger


class RecoverabilityPredictor:
    """
    Inference service for predicting payment recoverability probability (0-100).
    Loads a serialized scikit-learn RandomForest model from disk, with a calibrated
    expert-rules fallback if model weights are not yet generated or fail to load.
    """

    MODEL_DIR = os.path.join(os.path.dirname(__file__), "saved_models")
    MODEL_PATH = os.path.join(MODEL_DIR, "recoverability_rf.joblib")

    _pipeline = None

    @classmethod
    def get_tier(cls, score: float) -> str:
        """
        Maps numerical score (0-100) to recovery confidence tier.
        0-29: LOW
        30-69: MEDIUM
        70-100: HIGH
        """
        if score >= 70.0:
            return "HIGH"
        elif score >= 30.0:
            return "MEDIUM"
        else:
            return "LOW"

    @classmethod
    def load_model(cls):
        if cls._pipeline is None:
            if os.path.exists(cls.MODEL_PATH):
                try:
                    cls._pipeline = joblib.load(cls.MODEL_PATH)
                    logger.info(f"Loaded ML recoverability model from {cls.MODEL_PATH}")
                except Exception as e:
                    logger.warning(f"Failed to load model from {cls.MODEL_PATH}: {e}. Falling back to heuristic engine.")
            else:
                logger.info("Model file not found; using calibrated heuristic recoverability scoring.")
        return cls._pipeline

    @classmethod
    def predict_score(cls, feature_dict: Dict[str, float]) -> Tuple[float, str]:
        """
        Predicts recoverability score (0.0 to 100.0) and tier (LOW, MEDIUM, HIGH)
        from a raw feature dictionary.
        """
        pipeline = cls.load_model()

        if pipeline is not None:
            try:
                vec = FeatureExtractor.to_vector(feature_dict).reshape(1, -1)
                # Predict probability of class 1 (recoverable)
                proba = float(pipeline.predict_proba(vec)[0][1])
                score = round(max(0.0, min(100.0, proba * 100.0)), 1)
                return score, cls.get_tier(score)
            except Exception as e:
                logger.error(f"ML inference error: {e}. Reverting to calibrated fallback.")

        # Robust calibrated heuristic scoring
        return cls._heuristic_score(feature_dict)

    @classmethod
    def _heuristic_score(cls, f: Dict[str, float]) -> Tuple[float, str]:
        """
        Deterministic, well-calibrated expert scoring matching realistic payment dynamics:
        - Bank timeouts & network drops have very high recovery rates (~85-95%)
        - Abandoned checkouts have high recovery rates (~75-90%) with prompt
        - Loyal customers (high success rate, older accounts) have higher scores
        - Multiple retries degrade recoverability (~ -15% per retry)
        - Insufficient funds depends heavily on customer payment history (~40-75%)
        - Card declines & Limit exceeded are harder to recover (~15-45%)
        """
        reason_enc = int(f.get("failure_reason_encoded", 7))
        retry_count = int(f.get("retry_count", 0))
        success_rate = float(f.get("customer_successful_payment_rate", 0.8))
        prev_success = int(f.get("number_of_previous_successful_payments", 0))
        account_age = float(f.get("customer_account_age", 30))
        amount = float(f.get("payment_amount", 1000.0))

        # Base prior by failure signal
        # Map: 1=BANK_TIMEOUT, 2=NETWORK_ERROR, 3=INSUFFICIENT_FUNDS, 4=AUTHENTICATION_FAILED, 5=CARD_DECLINED, 6=LIMIT_EXCEEDED, 7=UNKNOWN
        if reason_enc in [1, 2]:  # Bank timeout, Network error
            base = 86.0
        elif reason_enc == 3:  # Insufficient funds
            base = 58.0
        elif reason_enc == 4:  # Auth failed
            base = 65.0
        elif reason_enc in [5, 6]:  # Card declined, Limit exceeded
            base = 32.0
        elif reason_enc == 0:  # Abandoned / None
            base = 82.0
        else:
            base = 50.0

        # Customer loyalty multiplier
        loyalty_bonus = 0.0
        if prev_success >= 10 and success_rate >= 0.85:
            loyalty_bonus += 12.0
        elif prev_success >= 3 and success_rate >= 0.70:
            loyalty_bonus += 6.0
        elif success_rate < 0.50:
            loyalty_bonus -= 15.0

        if account_age > 90:
            loyalty_bonus += 4.0

        # Retry penalty
        retry_penalty = retry_count * 14.0

        # Amount penalty (very high amounts have slightly lower spontaneous recovery)
        amount_adj = -5.0 if amount > 25000.0 else (3.0 if amount < 3000.0 else 0.0)

        raw_score = base + loyalty_bonus - retry_penalty + amount_adj

        # Hard bounds
        score = round(max(5.0, min(98.0, raw_score)), 1)
        return score, cls.get_tier(score)
