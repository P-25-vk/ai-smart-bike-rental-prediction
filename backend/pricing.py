"""
Dynamic Pricing Algorithm
Base price: ₹50
Rules:
  - Demand > 100  → +30%
  - Demand > 70   → +15%
  - Rainfall > 20 → -10%
"""


def calculate_price(predicted_demand: float, rainfall: float) -> dict:
    """
    Computes dynamic rental price based on demand and weather.

    Args:
        predicted_demand : predicted number of rentals
        rainfall         : mm of rainfall

    Returns:
        dict with base_price, final_price, adjustments applied
    """
    BASE_PRICE = 50.0
    price = BASE_PRICE
    adjustments = []

    # Demand-based surge pricing
    if predicted_demand > 100:
        price *= 1.30
        adjustments.append("Surge +30% (high demand > 100)")
    elif predicted_demand > 70:
        price *= 1.15
        adjustments.append("Surge +15% (demand > 70)")

    # Rainfall discount
    if rainfall > 20:
        price *= 0.90
        adjustments.append("Discount -10% (heavy rainfall)")

    return {
        "base_price":   BASE_PRICE,
        "final_price":  round(price, 2),
        "currency":     "INR",
        "adjustments":  adjustments if adjustments else ["Standard pricing applied"]
    }


def get_price_tier(final_price: float) -> str:
    """Returns a human-readable price tier label."""
    if final_price >= 65:
        return "Premium"
    elif final_price >= 55:
        return "Standard+"
    elif final_price <= 45:
        return "Discounted"
    else:
        return "Standard"


# ── Quick test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    scenarios = [
        (120, 0),    # high demand, no rain
        (80,  0),    # moderate demand
        (30,  0),    # low demand
        (110, 25),   # high demand + rain
        (50,  30),   # low demand + heavy rain
    ]
    print(f"{'Demand':>8}  {'Rainfall':>10}  {'Price (₹)':>10}  Adjustments")
    print("-" * 70)
    for demand, rain in scenarios:
        result = calculate_price(demand, rain)
        print(f"{demand:>8}  {rain:>10}mm  ₹{result['final_price']:>8}  {result['adjustments']}")
