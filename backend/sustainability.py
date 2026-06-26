"""
Sustainability Module
- CO₂ savings calculator
- Eco-score for users
- Total CO₂ reduction stats
"""
from dataclasses import dataclass

# Emission factors
CAR_CO2_PER_KM_G    = 120.0   # grams per km (average petrol car)
BIKE_CO2_PER_KM_G   = 0.0     # zero direct emissions
TRANSIT_CO2_PER_KM  = 68.0    # bus / metro average

# Eco score thresholds
ECO_BRONZE_KM  = 10.0
ECO_SILVER_KM  = 50.0
ECO_GOLD_KM    = 200.0
ECO_PLATINUM_KM = 500.0


@dataclass
class EcoResult:
    distance_km:       float
    co2_saved_g:       float
    co2_saved_kg:      float
    trees_equivalent:  float    # 1 tree absorbs ~21kg CO2/year
    eco_score:         float    # 0–100
    badge:             str
    message:           str


def calculate_co2_savings(distance_km: float, trips: int = 1) -> EcoResult:
    """
    Calculate CO₂ savings vs driving a car.
    """
    total_km      = distance_km * trips
    co2_saved_g   = total_km * CAR_CO2_PER_KM_G
    co2_saved_kg  = round(co2_saved_g / 1000, 3)
    trees_eq      = round(co2_saved_kg / 21, 4)
    eco_score     = min(100, round(total_km * 0.2, 1))

    if total_km >= ECO_PLATINUM_KM:
        badge   = "🏆 Platinum Eco Rider"
        message = "Outstanding! You're a climate champion."
    elif total_km >= ECO_GOLD_KM:
        badge   = "🥇 Gold Eco Rider"
        message = "Excellent contribution to a greener city!"
    elif total_km >= ECO_SILVER_KM:
        badge   = "🥈 Silver Eco Rider"
        message = "Great work — keep pedaling for the planet!"
    elif total_km >= ECO_BRONZE_KM:
        badge   = "🥉 Bronze Eco Rider"
        message = "Good start! Every km counts."
    else:
        badge   = "🌱 Eco Starter"
        message = "Welcome! Start riding to earn your eco badge."

    return EcoResult(
        distance_km      = round(total_km, 2),
        co2_saved_g      = round(co2_saved_g, 2),
        co2_saved_kg     = co2_saved_kg,
        trees_equivalent = trees_eq,
        eco_score        = eco_score,
        badge            = badge,
        message          = message,
    )


def fleet_co2_stats(records: list[dict]) -> dict:
    """
    Aggregate CO₂ stats from a list of ride records.
    records: each has 'distance_km'
    """
    total_km     = sum(r.get("distance_km", 0) for r in records)
    total_co2_kg = round(total_km * CAR_CO2_PER_KM_G / 1000, 2)
    trees_eq     = round(total_co2_kg / 21, 1)
    total_rides  = len(records)

    return {
        "total_rides":      total_rides,
        "total_km":         round(total_km, 2),
        "co2_saved_kg":     total_co2_kg,
        "trees_equivalent": trees_eq,
        "avg_co2_per_ride": round(total_co2_kg / total_rides * 1000, 1) if total_rides else 0,
    }


def get_user_eco_summary(user_rides: list[dict]) -> dict:
    """Full eco profile for a user."""
    total_km    = sum(r.get("distance_km", 0) for r in user_rides)
    total_trips = len(user_rides)
    eco         = calculate_co2_savings(total_km)

    return {
        "total_trips":      total_trips,
        "total_km":         round(total_km, 2),
        "co2_saved_kg":     eco.co2_saved_kg,
        "trees_equivalent": eco.trees_equivalent,
        "eco_score":        eco.eco_score,
        "badge":            eco.badge,
        "message":          eco.message,
    }


if __name__ == "__main__":
    result = calculate_co2_savings(distance_km=5.2, trips=30)
    print(f"Distance : {result.distance_km} km")
    print(f"CO₂ saved: {result.co2_saved_kg} kg  ({result.co2_saved_g}g)")
    print(f"Trees    : {result.trees_equivalent} trees/year equivalent")
    print(f"Badge    : {result.badge}")
    print(f"Eco Score: {result.eco_score}/100")
