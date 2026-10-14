def test_health_endpoint_reports_database_ready(client) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "configured"}


def test_missing_rate_history_uses_global_calculation_handler(client) -> None:
    response = client.get(
        "/api/v1/analytics/volatility",
        params={"currency": "USD", "source": "eltoque"},
    )

    assert response.status_code == 422
    assert "three distinct days" in response.json()["detail"]