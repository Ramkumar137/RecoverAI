def test_health_endpoint(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok", "service": "RecoverAI"}


def test_list_payments_endpoint(client):
    res = client.get("/api/payments?limit=10")
    assert res.status_code == 200
    items = res.json()
    assert isinstance(items, list)
    assert len(items) <= 10


def test_get_single_payment_endpoint(client):
    res = client.get("/api/payments/pay_demo_01_bank_timeout")
    assert res.status_code == 200
    data = res.json()
    assert data["payment_id"] == "pay_demo_01_bank_timeout"
    assert data["amount"] == 8500.0 or data["amount"] == "8500.00"
    assert data["customer"] is not None


def test_recovery_cases_list_endpoint(client):
    res = client.get("/api/recovery/cases?limit=10")
    assert res.status_code == 200
    items = res.json()
    assert isinstance(items, list)


def test_batch_analysis_endpoint(client):
    res = client.post("/api/recovery/analyze-batch?limit=50")
    assert res.status_code == 200
    data = res.json()
    assert "payments_analyzed" in data
    assert "revenue_at_risk" in data
    assert "potentially_recoverable" in data
    assert "high_recoverability" in data
    assert "medium_recoverability" in data
    assert "low_recoverability" in data


def test_analytics_revenue_risk_endpoint(client):
    res = client.get("/api/analytics/revenue-risk")
    assert res.status_code == 200
    data = res.json()
    assert "revenue_at_risk" in data
    assert "potentially_recoverable" in data
    assert "recovered_revenue" in data
    assert "recovery_rate" in data
    assert "failed_payments" in data
    assert "abandoned_payments" in data
    assert "open_recovery_cases" in data
