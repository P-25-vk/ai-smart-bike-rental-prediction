"""
Bike Maintenance Module
- Health monitoring
- Predictive maintenance alerts
- Service scheduling
- Usage-based wear analysis
"""
from dataclasses import dataclass, asdict
from typing import Optional


# Thresholds
SERVICE_HOURS_LIMIT  = 1500   # hours before mandatory service
WEAR_WARNING_HOURS   = 1200   # early warning
SERVICE_DAYS_LIMIT   = 180    # days between services
CRITICAL_DAYS_LIMIT  = 270    # critical overdue


@dataclass
class BikeHealth:
    bike_id:          int
    usage_hours:      float
    days_since_service: int
    health_score:     int        # 0–100
    status:           str        # Good / Warning / Critical
    maintenance_due:  bool
    alert:            Optional[str]
    next_service_in:  str
    wear_components:  dict


def assess_bike_health(
    bike_id: int,
    usage_hours: float,
    days_since_service: int
) -> BikeHealth:
    """
    Returns full health assessment for a single bike.
    """
    # Health score (100 = perfect, 0 = needs immediate service)
    usage_score   = max(0, 100 - (usage_hours / SERVICE_HOURS_LIMIT) * 100)
    service_score = max(0, 100 - (days_since_service / SERVICE_DAYS_LIMIT) * 100)
    health_score  = int((usage_score * 0.6 + service_score * 0.4))

    # Status
    if health_score >= 70:
        status = "Good"
    elif health_score >= 40:
        status = "Warning"
    else:
        status = "Critical"

    # Alert message
    alert = None
    maintenance_due = False
    if usage_hours >= SERVICE_HOURS_LIMIT:
        alert = f"🔴 CRITICAL: {usage_hours:.0f} usage hours — immediate service required!"
        maintenance_due = True
    elif usage_hours >= WEAR_WARNING_HOURS:
        alert = f"🟡 WARNING: Approaching service limit ({usage_hours:.0f}/{SERVICE_HOURS_LIMIT}h)"
        maintenance_due = True
    elif days_since_service >= CRITICAL_DAYS_LIMIT:
        alert = f"🔴 OVERDUE: {days_since_service} days since last service!"
        maintenance_due = True
    elif days_since_service >= SERVICE_DAYS_LIMIT:
        alert = f"🟡 SERVICE DUE: {days_since_service} days since last service"
        maintenance_due = True

    # Next service estimate
    hours_remaining = max(0, SERVICE_HOURS_LIMIT - usage_hours)
    if hours_remaining < 100:
        next_service_in = "Immediate"
    elif hours_remaining < 300:
        next_service_in = f"~{int(hours_remaining / 8)} days (high use)"
    else:
        next_service_in = f"~{int(hours_remaining / 4)} days (normal use)"

    # Wear component estimates
    wear_pct = min(100, round(usage_hours / SERVICE_HOURS_LIMIT * 100, 1))
    wear_components = {
        "brakes":      min(100, round(wear_pct * 1.1, 1)),
        "chain":       min(100, round(wear_pct * 1.3, 1)),
        "tyres":       min(100, round(wear_pct * 0.9, 1)),
        "gears":       min(100, round(wear_pct * 0.8, 1)),
        "bearings":    min(100, round(wear_pct * 0.7, 1)),
    }

    return BikeHealth(
        bike_id=bike_id,
        usage_hours=usage_hours,
        days_since_service=days_since_service,
        health_score=health_score,
        status=status,
        maintenance_due=maintenance_due,
        alert=alert,
        next_service_in=next_service_in,
        wear_components=wear_components,
    )


def fleet_maintenance_report(bikes: list[dict]) -> dict:
    """
    bikes: list of dicts with bike_id, usage_hours, days_since_service
    Returns fleet-wide summary.
    """
    assessments = [
        asdict(assess_bike_health(
            b["bike_id"], b["usage_hours"], b["days_since_service"]
        ))
        for b in bikes
    ]

    critical = [b for b in assessments if b["status"] == "Critical"]
    warnings = [b for b in assessments if b["status"] == "Warning"]
    good     = [b for b in assessments if b["status"] == "Good"]
    due      = [b for b in assessments if b["maintenance_due"]]

    avg_health = round(sum(b["health_score"] for b in assessments) / len(assessments), 1) if assessments else 0

    return {
        "total_bikes":         len(bikes),
        "critical_count":      len(critical),
        "warning_count":       len(warnings),
        "good_count":          len(good),
        "maintenance_due":     len(due),
        "avg_health_score":    avg_health,
        "bikes_needing_service": [b["bike_id"] for b in due],
        "assessments":         assessments,
    }


def schedule_service(bikes_due: list[int], available_slots: int = 5) -> list[dict]:
    """Simple service scheduling — returns first N bikes to service today."""
    return [
        {"bike_id": bid, "scheduled": "Today", "slot": i + 1}
        for i, bid in enumerate(bikes_due[:available_slots])
    ]


if __name__ == "__main__":
    h = assess_bike_health(bike_id=101, usage_hours=1450, days_since_service=160)
    print(f"Bike {h.bike_id} | Health: {h.health_score}/100 | Status: {h.status}")
    print(f"Alert: {h.alert}")
    print(f"Next service: {h.next_service_in}")
    print(f"Wear: {h.wear_components}")
