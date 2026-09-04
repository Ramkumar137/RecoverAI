import os
from typing import Tuple
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, accuracy_score
from app.ml.feature_extractor import FeatureExtractor
from app.utils.logger import logger


def generate_training_data(n_samples: int = 2500, random_state: int = 42) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generates synthetic training dataset mimicking realistic Razorpay payment failure and recovery telemetry.
    """
    np.random.seed(random_state)

    amounts = np.random.exponential(scale=3500.0, size=n_samples) + 200.0
    customer_avg = amounts * np.random.uniform(0.7, 1.3, size=n_samples)

    succ_counts = np.random.geometric(p=0.15, size=n_samples) - 1
    fail_counts = np.random.geometric(p=0.45, size=n_samples) - 1

    total = succ_counts + fail_counts
    succ_rate = np.where(total > 0, succ_counts / total, 0.8)
    fail_rate = 1.0 - succ_rate

    retries = np.random.choice([0, 1, 2, 3], p=[0.55, 0.25, 0.15, 0.05], size=n_samples)

    # 0: None/Abandoned, 1: Bank Timeout, 2: Network Error, 3: Insufficient Funds, 4: Auth Failed, 5: Card Declined, 6: Limit Exceeded, 7: Unknown
    reasons = np.random.choice(
        [0, 1, 2, 3, 4, 5, 6, 7],
        p=[0.15, 0.20, 0.12, 0.25, 0.10, 0.10, 0.05, 0.03],
        size=n_samples,
    )

    methods = np.random.choice([0, 1, 2, 3, 4], p=[0.50, 0.25, 0.15, 0.08, 0.02], size=n_samples)
    account_age = np.random.exponential(scale=180.0, size=n_samples) + 5.0
    time_since_failure = np.random.exponential(scale=12.0, size=n_samples)
    is_sub = np.random.choice([0.0, 1.0], p=[0.7, 0.3], size=n_samples)
    hist_rec_rate = np.random.normal(loc=0.55, scale=0.10, size=n_samples).clip(0.1, 0.95)

    # Assemble feature matrix
    X = np.column_stack([
        amounts,
        customer_avg,
        succ_rate,
        fail_rate,
        succ_counts.astype(float),
        fail_counts.astype(float),
        retries.astype(float),
        reasons.astype(float),
        methods.astype(float),
        account_age,
        time_since_failure,
        is_sub,
        hist_rec_rate,
    ])

    # True latent recovery probability
    # Bank/Network (1,2) -> high; Card/Limit (5,6) -> low; Retries penalize; Success rate boosts
    logits = (
        (np.isin(reasons, [1, 2]) * 1.8)
        + (reasons == 0) * 1.4
        + (reasons == 3) * 0.4
        - (np.isin(reasons, [5, 6]) * 1.6)
        + (succ_rate * 1.5)
        + (succ_counts > 5) * 0.6
        - (retries * 1.1)
        - (amounts > 15000) * 0.4
        + (account_age > 60) * 0.3
        + np.random.normal(0, 0.4, size=n_samples)
    )

    probs = 1.0 / (1.0 + np.exp(-logits))
    y = (probs >= 0.50).astype(int)

    return X, y


def train_and_save_model():
    logger.info("Generating synthetic training dataset for recoverability model...")
    X, y = generate_training_data(n_samples=3000, random_state=42)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    logger.info(f"Training RandomForestClassifier on {len(X_train)} samples...")
    clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=8,
        min_samples_leaf=4,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    clf.fit(X_train, y_train)

    y_pred_proba = clf.predict_proba(X_test)[:, 1]
    y_pred = (y_pred_proba >= 0.5).astype(int)

    auc = roc_auc_score(y_test, y_pred_proba)
    acc = accuracy_score(y_test, y_pred)
    logger.info(f"Model Training Results: ROC AUC = {auc:.4f}, Accuracy = {acc:.4f}")

    # Ensure output directory exists
    model_dir = os.path.join(os.path.dirname(__file__), "saved_models")
    os.makedirs(model_dir, exist_ok=True)
    out_path = os.path.join(model_dir, "recoverability_rf.joblib")

    joblib.dump(clf, out_path)
    logger.info(f"Successfully saved trained model to {out_path}")
    return out_path


if __name__ == "__main__":
    train_and_save_model()
