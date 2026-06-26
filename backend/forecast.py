"""
24-Hour Demand Forecasting
Generates next 24 hours of predictions for a given station/conditions.
"""
import pickle
import numpy as np
import pandas as pd
from datetime import datetime

EVENT_MAP = {"None": 0, "Festival": 1, "Concert": 2, "Sports": 3}


def load_model(path="bike_model.pkl"):
    with open(path, "rb") as f:
        return pickle.load(f)


def forecast_24h(
    station_id: int,
    temperature: float,
    humidity: float,
    windspeed: float,
    rainfall: float,
    available_bikes: int,
    weekday: int,
    month: int,
    holiday: bool = False,
    event_type: str = "None",
    model_path: str = "bike_model.pkl"
) -> list[dict]:
    """
    Returns a list of 24 dicts, one per hour, with predicted demand.
    """
    pkg       = load_model(model_path)
    model     = pkg["model"]
    event_code = EVENT_MAP.get(event_type, 0)

    rows = []
    for hour in range(24):
        rows.append({
            "temperature":    temperature,
            "humidity":       humidity,
            "hour":           hour,
            "weekday":        weekday,
            "holiday":        int(holiday),
            "month":          month,
            "windspeed":      windspeed,
            "rainfall":       rainfall,
            "available_bikes": available_bikes,
            "event_code":     event_code,
        })

    X   = pd.DataFrame(rows)[pkg["features"]]
    raw = model.predict(X)
    preds = np.clip(raw, 0, None)

    result = []
    for hour, pred in enumerate(preds):
        result.append({
            "hour":             hour,
            "label":            f"{hour:02d}:00",
            "predicted_demand": round(float(pred), 1),
            "peak":             bool(pred == preds.max()),
        })
    return result


def get_peak_hours(forecast: list[dict], top_n: int = 3) -> list[dict]:
    return sorted(forecast, key=lambda x: x["predicted_demand"], reverse=True)[:top_n]


if __name__ == "__main__":
    f = forecast_24h(
        station_id=1, temperature=25, humidity=60,
        windspeed=10, rainfall=0, available_bikes=20,
        weekday=1, month=6
    )
    print("Hour | Demand")
    for h in f:
        bar = "█" * int(h["predicted_demand"] / 3)
        print(f"  {h['label']}  {h['predicted_demand']:6.1f}  {bar}")
