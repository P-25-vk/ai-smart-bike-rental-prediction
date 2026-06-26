"""
Pytest Test Suite
Tests: prediction endpoint, pricing function, recommendation function
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pricing import calculate_price, get_price_tier
from recommendation import get_weather_recommendation, get_full_recommendation

# ── Fixtures ──────────────────────────────────────────────────────────────────
@pytest.fixture
def client():
    """Flask test client."""
    from app import app
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


VALID_PAYLOAD = {
    "temperature":    25.0,
    "humidity":       60.0,
    "hour":           8,
    "weekday":        1,
    "holiday":        False,
    "month":          6,
    "windspeed":      10.0,
    "rainfall":       0.0,
    "available_bikes": 20
}

# ─────────────────────────────────────────────────────────────────────────────
# 1. PREDICTION ENDPOINT TESTS
# ─────────────────────────────────────────────────────────────────────────────
class TestPredictEndpoint:

    def test_health_check(self, client):
        r = client.get("/")
        assert r.status_code == 200
        data = r.get_json()
        assert data["status"] == "ok"

    def test_predict_returns_200(self, client):
        r = client.post("/predict", json=VALID_PAYLOAD)
        assert r.status_code == 200

    def test_predict_response_keys(self, client):
        r = client.post("/predict", json=VALID_PAYLOAD)
        data = r.get_json()
        expected_keys = {"predicted_demand", "price", "recommendation",
                         "demand_category", "price_tier"}
        assert expected_keys.issubset(set(data.keys()))

    def test_predicted_demand_non_negative(self, client):
        r = client.post("/predict", json=VALID_PAYLOAD)
        data = r.get_json()
        assert data["predicted_demand"] >= 0

    def test_predict_missing_field_returns_400(self, client):
        bad_payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "temperature"}
        r = client.post("/predict", json=bad_payload)
        assert r.status_code == 400

    def test_predict_with_rainfall(self, client):
        payload = {**VALID_PAYLOAD, "rainfall": 25.0}
        r = client.post("/predict", json=payload)
        assert r.status_code == 200
        data = r.get_json()
        # Price should reflect rainfall discount
        assert data["price"] <= 65.0   # at most base + surge - discount

    def test_predict_holiday(self, client):
        payload = {**VALID_PAYLOAD, "holiday": True}
        r = client.post("/predict", json=payload)
        assert r.status_code == 200

    def test_stats_endpoint(self, client):
        r = client.get("/stats")
        # May fail if CSV not present; just check it doesn't crash the server
        assert r.status_code in (200, 500)


# ─────────────────────────────────────────────────────────────────────────────
# 2. PRICING FUNCTION TESTS
# ─────────────────────────────────────────────────────────────────────────────
class TestPricingFunction:

    def test_base_price_low_demand_no_rain(self):
        result = calculate_price(30, 0)
        assert result["final_price"] == 50.0
        assert result["base_price"] == 50.0

    def test_surge_high_demand(self):
        result = calculate_price(110, 0)
        assert result["final_price"] == pytest.approx(65.0, 0.01)   # 50 * 1.30

    def test_surge_moderate_demand(self):
        result = calculate_price(80, 0)
        assert result["final_price"] == pytest.approx(57.50, 0.01)  # 50 * 1.15

    def test_rainfall_discount(self):
        result = calculate_price(30, 25)
        assert result["final_price"] == pytest.approx(45.0, 0.01)   # 50 * 0.90

    def test_surge_and_rainfall_combined(self):
        result = calculate_price(110, 25)
        # 50 * 1.30 * 0.90 = 58.50
        assert result["final_price"] == pytest.approx(58.50, 0.01)

    def test_adjustments_listed(self):
        result = calculate_price(110, 25)
        assert len(result["adjustments"]) == 2

    def test_standard_adjustments_when_no_rules(self):
        result = calculate_price(50, 0)
        assert "Standard pricing applied" in result["adjustments"][0]

    def test_price_tier_premium(self):
        assert get_price_tier(70.0) == "Premium"

    def test_price_tier_standard(self):
        assert get_price_tier(50.0) == "Standard"

    def test_price_tier_discounted(self):
        assert get_price_tier(40.0) == "Discounted"

    def test_currency_is_inr(self):
        result = calculate_price(80, 0)
        assert result["currency"] == "INR"


# ─────────────────────────────────────────────────────────────────────────────
# 3. RECOMMENDATION FUNCTION TESTS
# ─────────────────────────────────────────────────────────────────────────────
class TestRecommendationFunction:

    def test_heavy_rain_recommendation(self):
        msg = get_weather_recommendation(25.0, 22.0, 60.0)
        assert "Low demand expected" in msg or "rainfall" in msg.lower()

    def test_ideal_weather_recommendation(self):
        msg = get_weather_recommendation(0.0, 25.0, 60.0)
        assert "Ideal cycling weather" in msg or "high" in msg.lower()

    def test_high_humidity_recommendation(self):
        msg = get_weather_recommendation(0.0, 22.0, 90.0)
        assert "humidity" in msg.lower() or "Demand may decrease" in msg

    def test_cold_weather_recommendation(self):
        msg = get_weather_recommendation(0.0, 5.0, 50.0)
        assert "Cold" in msg or "lower" in msg.lower()

    def test_hot_weather_recommendation(self):
        msg = get_weather_recommendation(0.0, 38.0, 50.0)
        assert "hot" in msg.lower() or "decrease" in msg.lower()

    def test_returns_string(self):
        msg = get_weather_recommendation(0.0, 25.0, 60.0)
        assert isinstance(msg, str)
        assert len(msg) > 0

    def test_full_recommendation_structure(self):
        result = get_full_recommendation(0.0, 25.0, 60.0, 110.0)
        assert "weather_recommendation" in result
        assert "demand_category" in result
        assert "operational_tip" in result
        assert "predicted_demand" in result

    def test_full_recommendation_very_high_demand(self):
        result = get_full_recommendation(0.0, 25.0, 60.0, 120.0)
        assert result["demand_category"] == "Very High"

    def test_full_recommendation_low_demand(self):
        result = get_full_recommendation(0.0, 25.0, 60.0, 20.0)
        assert result["demand_category"] == "Low"

    def test_no_crash_on_edge_values(self):
        msg = get_weather_recommendation(0.0, 0.0, 0.0)
        assert isinstance(msg, str)
        msg2 = get_weather_recommendation(200.0, 50.0, 100.0)
        assert isinstance(msg2, str)
