"""
Weather Recommendation Engine
Returns human-readable recommendation strings based on weather conditions.
"""

from typing import List


def get_weather_recommendation(
    rainfall: float,
    temperature: float,
    humidity: float
) -> str:
    """
    Returns a weather-based rental demand recommendation.

    Args:
        rainfall    : mm of rainfall
        temperature : degrees Celsius
        humidity    : percentage (0–100)

    Returns:
        recommendation string
    """
    recommendations: List[str] = []

    # Rainfall check (highest priority)
    if rainfall > 20:
        recommendations.append("🌧️ Low demand expected — heavy rainfall detected.")

    # Temperature check
    if 20 <= temperature <= 30:
        recommendations.append("☀️ Ideal cycling weather — demand likely high.")
    elif temperature < 10:
        recommendations.append("🥶 Cold weather — demand may be lower than usual.")
    elif temperature > 35:
        recommendations.append("🌡️ Very hot conditions — demand may decrease.")

    # Humidity check
    if humidity > 85:
        recommendations.append("💧 High humidity — demand may decrease.")

    # Default positive message
    if not recommendations:
        recommendations.append("✅ Good conditions — normal to high demand expected.")

    return "  |  ".join(recommendations)


def get_full_recommendation(
    rainfall: float,
    temperature: float,
    humidity: float,
    predicted_demand: float
) -> dict:
    """
    Returns structured recommendation with demand category and advice.
    """
    weather_msg = get_weather_recommendation(rainfall, temperature, humidity)

    if predicted_demand > 100:
        demand_category = "Very High"
        operational_tip = "Deploy extra bikes and staff at peak stations."
    elif predicted_demand > 70:
        demand_category = "High"
        operational_tip = "Ensure sufficient bike availability."
    elif predicted_demand > 40:
        demand_category = "Moderate"
        operational_tip = "Standard operations recommended."
    else:
        demand_category = "Low"
        operational_tip = "Consider redistribution from high-stock stations."

    return {
        "weather_recommendation": weather_msg,
        "demand_category":        demand_category,
        "operational_tip":        operational_tip,
        "predicted_demand":       round(predicted_demand, 1)
    }


# ── Quick test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_cases = [
        (25.0, 28.0, 60.0),   # ideal
        (30.0, 22.0, 90.0),   # high humidity
        (0.0,   5.0, 50.0),   # cold
        (50.0, 30.0, 70.0),   # heavy rain
    ]
    for rain, temp, hum in test_cases:
        msg = get_weather_recommendation(rain, temp, hum)
        print(f"Rain={rain}mm Temp={temp}°C Hum={hum}%  →  {msg}")
