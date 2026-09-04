from app.ml.feature_extractor import FeatureExtractor
from app.ml.model import RecoverabilityPredictor


def test_feature_extraction_completeness():
    features = FeatureExtractor.extract_features(
        amount=8500.0,
        customer_avg_amount=8000.0,
        customer_successful_payments=15,
        customer_failed_payments=2,
        customer_account_age_days=180,
        retry_count=1,
        failure_reason="BANK_TIMEOUT",
        payment_method="UPI",
    )

    for name in FeatureExtractor.FEATURE_NAMES:
        assert name in features
        assert isinstance(features[name], (int, float))

    vec = FeatureExtractor.to_vector(features)
    assert vec.shape == (len(FeatureExtractor.FEATURE_NAMES),)


def test_ml_predictor_score_and_tier():
    features = FeatureExtractor.extract_features(
        amount=8500.0,
        customer_avg_amount=8000.0,
        customer_successful_payments=15,
        customer_failed_payments=2,
        customer_account_age_days=180,
        retry_count=0,
        failure_reason="BANK_TIMEOUT",
        payment_method="UPI",
    )

    score, tier = RecoverabilityPredictor.predict_score(features)
    assert 0.0 <= score <= 100.0
    assert tier in ["LOW", "MEDIUM", "HIGH"]
    assert tier == "HIGH"  # Bank timeout + 15 succ / 2 fail should be HIGH


def test_ml_predictor_low_tier_decline():
    features = FeatureExtractor.extract_features(
        amount=18000.0,
        customer_avg_amount=3000.0,
        customer_successful_payments=1,
        customer_failed_payments=7,
        customer_account_age_days=15,
        retry_count=2,
        failure_reason="CARD_DECLINED",
        payment_method="CARD",
    )

    score, tier = RecoverabilityPredictor.predict_score(features)
    assert 0.0 <= score <= 100.0
    assert tier == "LOW"
