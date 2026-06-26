"""
Smart Operations Module
- Bike redistribution suggestions
- Low-stock alerts
- Shortage notifications
- Station occupancy forecasting
"""
import pandas as pd
import numpy as np
from dataclasses import dataclass, asdict
from typing import Optional


LOW_STOCK_THRESHOLD   = 5    # bikes
HIGH_STOCK_THRESHOLD  = 50   # bikes
OCCUPANCY_WARN        = 0.85  # 85% full


@dataclass
class StationStatus:
    station_id:       int
    available_bikes:  int
    total_docks:      int
    occupancy_pct:    float
    predicted_demand: float
    alert:            Optional[str]
    action:           Optional[str]


def analyze_stations(stations: list[dict]) -> list[dict]:
    """
    stations: list of dicts with keys:
        station_id, available_bikes, total_docks, predicted_demand
    Returns enriched list with alerts and redistribution actions.
    """
    results = []
    for s in stations:
        avail   = s["available_bikes"]
        docks   = s["total_docks"]
        demand  = s.get("predicted_demand", 0)
        occ_pct = round((docks - avail) / docks * 100, 1) if docks > 0 else 0

        alert  = None
        action = None

        if avail <= LOW_STOCK_THRESHOLD:
            alert  = f"⚠️ LOW STOCK: Only {avail} bikes remaining!"
            action = "Request bike transfer from nearby high-stock station"
        elif avail > HIGH_STOCK_THRESHOLD and demand < 20:
            alert  = f"📦 OVERSTOCKED: {avail} bikes, low demand expected"
            action = "Redistribute excess bikes to low-stock stations"
        elif occ_pct >= OCCUPANCY_WARN * 100:
            alert  = f"🚨 NEAR FULL: {occ_pct}% dock occupancy"
            action = "Move bikes out before station locks up"
        elif demand > avail * 1.5:
            alert  = f"📈 SHORTAGE RISK: Demand ({demand:.0f}) >> Available ({avail})"
            action = "Pre-position additional bikes within 2 hours"

        results.append(asdict(StationStatus(
            station_id=s["station_id"],
            available_bikes=avail,
            total_docks=docks,
            occupancy_pct=occ_pct,
            predicted_demand=round(demand, 1),
            alert=alert,
            action=action,
        )))
    return results


def redistribution_plan(stations: list[dict]) -> list[dict]:
    """
    Returns a list of transfer recommendations:
    move bikes FROM high-stock TO low-stock stations.
    """
    analyzed = analyze_stations(stations)
    donors    = [s for s in analyzed if s["available_bikes"] > HIGH_STOCK_THRESHOLD]
    receivers = [s for s in analyzed if s["available_bikes"] <= LOW_STOCK_THRESHOLD + 5]

    plan = []
    for r in receivers:
        if not donors:
            break
        donor   = max(donors, key=lambda d: d["available_bikes"])
        transfer = min(10, donor["available_bikes"] - LOW_STOCK_THRESHOLD)
        plan.append({
            "from_station":   donor["station_id"],
            "to_station":     r["station_id"],
            "bikes_to_move":  transfer,
            "priority":       "High" if r["available_bikes"] <= 2 else "Medium",
            "reason":         f"Station {r['station_id']} has only {r['available_bikes']} bikes",
        })
        donor["available_bikes"] -= transfer
    return plan


def get_low_stock_alerts(stations: list[dict]) -> list[dict]:
    analyzed = analyze_stations(stations)
    return [s for s in analyzed if s["alert"] and "LOW STOCK" in s["alert"]]


def occupancy_forecast(available: int, total_docks: int, hourly_demand: list) -> list[dict]:
    """Simulate occupancy over 24h given hourly demand predictions."""
    current = available
    result  = []
    for hour, demand in enumerate(hourly_demand):
        current    = max(0, min(total_docks, current - demand + np.random.randint(0, 5)))
        occ        = round((total_docks - current) / total_docks * 100, 1)
        result.append({"hour": hour, "available": int(current), "occupancy_pct": occ})
    return result


if __name__ == "__main__":
    test_stations = [
        {"station_id": 1,  "available_bikes": 3,  "total_docks": 30, "predicted_demand": 45},
        {"station_id": 2,  "available_bikes": 55, "total_docks": 60, "predicted_demand": 10},
        {"station_id": 3,  "available_bikes": 20, "total_docks": 40, "predicted_demand": 22},
        {"station_id": 4,  "available_bikes": 1,  "total_docks": 25, "predicted_demand": 60},
    ]
    print("=== Station Alerts ===")
    for s in analyze_stations(test_stations):
        if s["alert"]:
            print(f"  Station {s['station_id']}: {s['alert']}")
            print(f"    → {s['action']}")

    print("\n=== Redistribution Plan ===")
    for p in redistribution_plan(test_stations):
        print(f"  Move {p['bikes_to_move']} bikes: Station {p['from_station']} → {p['to_station']}  [{p['priority']}]")
