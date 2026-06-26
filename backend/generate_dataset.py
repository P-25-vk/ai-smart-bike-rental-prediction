"""
Enhanced Dataset Generator
- 15,000 records, 75 stations, event-aware, maintenance fields
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)
N = 15000
NUM_STATIONS = 75

start_date = datetime(2022, 1, 1)
dates = sorted([start_date + timedelta(days=np.random.randint(0, 730)) for _ in range(N)])

hours    = np.random.choice(range(24), N)
weekdays = [d.weekday() for d in dates]
months   = [d.month for d in dates]
holidays = np.random.choice([True, False], N, p=[0.05, 0.95])

# Events: concerts / festivals / sports on ~8% of days
events      = np.random.choice([0, 1, 2, 3], N, p=[0.92, 0.03, 0.03, 0.02])
event_names = ["None", "Festival", "Concert", "Sports"]

temperature = np.clip(
    [15 + 10 * np.sin((m - 3) * np.pi / 6) + np.random.normal(0, 3) for m in months],
    2, 42)
humidity    = np.random.uniform(30, 95, N)
windspeed   = np.clip(np.abs(np.random.normal(12, 7, N)), 0, 40)
rainfall    = np.where(np.random.random(N) < 0.15, np.random.exponential(15, N), 0.0)
rainfall    = np.clip(rainfall, 0, 120)

station_id      = np.random.randint(1, NUM_STATIONS + 1, N)
available_bikes = np.random.randint(3, 61, N)
total_docks     = np.random.randint(20, 80, N)

# Demand model
hour_effect    = np.array([-12 if h<5 else 5 if h<7 else 22 if h in[7,8,9]
                            else 12 if h<17 else 28 if h in[17,18,19]
                            else 6 if h<22 else -4 for h in hours])
weekend_effect = np.array([12 if w >= 5 else 0 for w in weekdays])
holiday_effect = np.array([18 if h else 0 for h in holidays])
event_effect   = events * 20   # 0/20/20/20

base = (20 + 0.8*temperature - 0.2*humidity - 0.3*windspeed
        - 0.4*rainfall + 0.5*available_bikes)
rentals = np.clip(base + hour_effect + weekend_effect + holiday_effect
                  + event_effect + np.random.normal(0, 5, N), 0, None).astype(int)

# Ride history / user columns
user_id         = np.random.randint(1001, 5001, N)
ride_duration   = np.clip(np.random.exponential(25, N), 2, 180).astype(int)  # minutes
distance_km     = np.round(ride_duration * 0.25 + np.random.normal(0, 0.5, N), 2)
distance_km     = np.clip(distance_km, 0.2, 40)
co2_saved_g     = np.round(distance_km * 120, 2)   # avg car: 120g CO2/km
eco_score       = np.clip(np.round(distance_km * 3 + np.random.normal(0,2,N), 1), 0, 100)

# Maintenance
bike_id         = np.random.randint(1, 3001, N)
usage_hours     = np.round(np.random.uniform(0, 2000, N), 1)
maintenance_due = usage_hours > 1500
last_service    = np.random.randint(0, 365, N)   # days since last service

df = pd.DataFrame({
    "date":            [d.strftime("%Y-%m-%d") for d in dates],
    "hour":            hours,
    "weekday":         weekdays,
    "month":           months,
    "holiday":         holidays,
    "event_type":      [event_names[e] for e in events],
    "temperature":     np.round(temperature, 2),
    "humidity":        np.round(humidity, 2),
    "windspeed":       np.round(windspeed, 2),
    "rainfall":        np.round(rainfall, 2),
    "station_id":      station_id,
    "available_bikes": available_bikes,
    "total_docks":     total_docks,
    "rentals":         rentals,
    "user_id":         user_id,
    "bike_id":         bike_id,
    "ride_duration":   ride_duration,
    "distance_km":     distance_km,
    "co2_saved_g":     co2_saved_g,
    "eco_score":       eco_score,
    "usage_hours":     usage_hours,
    "maintenance_due": maintenance_due,
    "days_since_service": last_service,
})

df.to_csv("bike_rental.csv", index=False)
print(f"✅ Dataset saved: bike_rental.csv  |  Rows: {len(df)}  |  Stations: {NUM_STATIONS}")
print(df.head(3).to_string())
