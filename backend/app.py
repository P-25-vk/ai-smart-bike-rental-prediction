"""
Flask Backend - Bike Rental Prediction API
POST /predict      →  predicted_demand, price, recommendation
POST /forecast     →  24-hour demand forecast
POST /operations/analyze    →  station alerts
POST /operations/redistribute → redistribution plan
GET  /operations/demo       →  demo station data
POST /sustainability        →  CO2 savings
GET  /sustainability/fleet  →  fleet-wide CO2 stats
POST /maintenance/assess    →  single bike health
POST /maintenance/fleet     →  fleet maintenance report
GET  /maintenance/demo      →  demo fleet data
GET  /stats                 →  aggregated analytics
GET  /export/stats          →  CSV export
GET  /admin/model-info      →  model metrics
POST /admin/retrain         →  trigger retraining
GET  /user/<id>/history     →  ride history
GET  /user/<id>/favorites   →  favorite stations
GET  /user/<id>/eco         →  eco profile
"""

import os
import pickle
import threading
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

from recommendation import get_weather_recommendation, get_full_recommendation
from pricing import calculate_price, get_price_tier
from forecast import forecast_24h, get_peak_hours
from redistribution import analyze_stations, redistribution_plan
from sustainability import calculate_co2_savings, fleet_co2_stats, get_user_eco_summary
from maintenance import assess_bike_health, fleet_maintenance_report
from dataclasses import asdict

app = Flask(__name__)

# ── CORS: allow frontend origin (restrict in production via env var) ───────────
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "*")
CORS(app, origins=ALLOWED_ORIGINS)

# ── Admin API key (set via env var in production) ─────────────────────────────
ADMIN_KEY = os.environ.get("ADMIN_KEY", "admin-secret-key")

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE_DIR, "bike_model.pkl")
CSV_PATH   = os.path.join(BASE_DIR, "bike_rental.csv")

# ── S3 config (set via environment variables) ─────────────────────────────────
S3_BUCKET     = os.environ.get("S3_BUCKET", "")
AWS_REGION    = os.environ.get("AWS_REGION", "ap-south-1")
AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "")

# ── Event mapping (matches train_model.py) ────────────────────────────────────
EVENT_MAP = {"None": 0, "Festival": 1, "Concert": 2, "Sports": 3}

model = None

def download_from_s3(s3_key, local_path):
    """Download a file from S3 to local path."""
    try:
        import boto3
        s3 = boto3.client(
            "s3",
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY
        )
        s3.download_file(S3_BUCKET, s3_key, local_path)
        print(f"Downloaded {s3_key} from S3.")
        return True
    except Exception as e:
        print(f"S3 download failed for {s3_key}: {e}")
        return False

def load_model():
    global model
    # Try local first
    if not os.path.exists(MODEL_PATH) and S3_BUCKET:
        print("Model not found locally. Downloading from S3...")
        download_from_s3("models/bike_model.pkl", MODEL_PATH)
    # Load CSV from S3 if not local
    if not os.path.exists(CSV_PATH) and S3_BUCKET:
        print("Dataset not found locally. Downloading from S3...")
        download_from_s3("dataset/bike_rental.csv", CSV_PATH)
    try:
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
        print("Model loaded successfully.")
    except FileNotFoundError:
        print("bike_model.pkl not found. Run train_model.py first.")

load_model()

# ── Feature order must match training (10 features including event_code) ──────
FEATURE_ORDER = [
    "temperature", "humidity", "hour", "weekday", "holiday",
    "month", "windspeed", "rainfall", "available_bikes"
]

def load_csv():
    """Load CSV once, return DataFrame. Returns None if file missing."""
    if not os.path.exists(CSV_PATH):
        return None
    return pd.read_csv(CSV_PATH)


# ═══════════════════════════════════════════════════════════════════════════════
# HEALTH CHECK
# ═══════════════════════════════════════════════════════════════════════════════
@app.route("/", methods=["GET"])
def health():
    metrics = {}
    if model and isinstance(model, dict):
        metrics = model.get("metrics", {})
    return jsonify({
        "status":  "ok",
        "service": "Smart Bike Rental Prediction API",
        "model":   "loaded" if model else "not loaded",
        "metrics": metrics
    })


# ═══════════════════════════════════════════════════════════════════════════════
# PREDICTION
# ═══════════════════════════════════════════════════════════════════════════════
@app.route("/predict", methods=["POST"])
def predict():
    if model is None:
        return jsonify({"error": "Model not loaded. Run train_model.py first."}), 503

    data = request.get_json(force=True)

    missing = [f for f in FEATURE_ORDER if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    try:
        event_code = EVENT_MAP.get(data.get("event_type", "None"), 0)

        features = pd.DataFrame([[
            float(data["temperature"]),
            float(data["humidity"]),
            int(data["hour"]),
            int(data["weekday"]),
            int(bool(data["holiday"])),
            int(data["month"]),
            float(data["windspeed"]),
            float(data["rainfall"]),
            int(data["available_bikes"]),
            event_code
        ]], columns=model["features"])

        raw_pred         = model["model"].predict(features)[0]
        predicted_demand = max(0, round(float(raw_pred), 1))

        pricing    = calculate_price(predicted_demand, float(data["rainfall"]))
        price_tier = get_price_tier(pricing["final_price"])
        full_rec   = get_full_recommendation(
            rainfall         = float(data["rainfall"]),
            temperature      = float(data["temperature"]),
            humidity         = float(data["humidity"]),
            predicted_demand = predicted_demand
        )

        return jsonify({
            "predicted_demand":  predicted_demand,
            "price":             pricing["final_price"],
            "base_price":        pricing["base_price"],
            "currency":          "INR",
            "price_tier":        price_tier,
            "price_adjustments": pricing["adjustments"],
            "recommendation":    full_rec["weather_recommendation"],
            "demand_category":   full_rec["demand_category"],
            "operational_tip":   full_rec["operational_tip"]
        })

    except (ValueError, KeyError) as e:
        return jsonify({"error": f"Invalid input: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# 24-HOUR FORECAST
# ═══════════════════════════════════════════════════════════════════════════════
@app.route("/forecast", methods=["POST"])
def forecast():
    if model is None:
        return jsonify({"error": "Model not loaded."}), 503

    data = request.get_json(force=True)
    required = ["temperature", "humidity", "windspeed", "rainfall",
                "available_bikes", "weekday", "month"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    try:
        result = forecast_24h(
            station_id      = int(data.get("station_id", 1)),
            temperature     = float(data["temperature"]),
            humidity        = float(data["humidity"]),
            windspeed       = float(data["windspeed"]),
            rainfall        = float(data["rainfall"]),
            available_bikes = int(data["available_bikes"]),
            weekday         = int(data["weekday"]),
            month           = int(data["month"]),
            holiday         = bool(data.get("holiday", False)),
            event_type      = data.get("event_type", "None"),
            model_path      = MODEL_PATH
        )
        return jsonify({
            "forecast":   result,
            "peak_hours": get_peak_hours(result, top_n=3)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# SMART OPERATIONS
# ═══════════════════════════════════════════════════════════════════════════════
@app.route("/operations/analyze", methods=["POST"])
def operations_analyze():
    data = request.get_json(force=True)
    stations = data.get("stations", [])
    if not stations:
        return jsonify({"error": "stations array required"}), 400
    try:
        return jsonify({"stations": analyze_stations(stations)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/operations/redistribute", methods=["POST"])
def operations_redistribute():
    data = request.get_json(force=True)
    stations = data.get("stations", [])
    if not stations:
        return jsonify({"error": "stations array required"}), 400
    try:
        return jsonify({"plan": redistribution_plan(stations)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/operations/demo", methods=["GET"])
def operations_demo():
    """Returns simulated station data from CSV averages."""
    try:
        df = load_csv()
        if df is None:
            return jsonify({"error": "bike_rental.csv not found"}), 500

        station_avg = (
            df.groupby("station_id")
              .agg(avg_rentals=("rentals", "mean"),
                   avg_bikes=("available_bikes", "mean"),
                   avg_docks=("total_docks", "mean"))
              .reset_index()
              .head(10)
        )
        stations = []
        for _, row in station_avg.iterrows():
            avail = max(1, int(row["avg_bikes"]))
            docks = max(avail + 5, int(row["avg_docks"]))
            stations.append({
                "station_id":       int(row["station_id"]),
                "available_bikes":  avail,
                "total_docks":      docks,
                "predicted_demand": round(float(row["avg_rentals"]), 1)
            })

        analyzed = analyze_stations(stations)
        plan     = redistribution_plan(stations)
        return jsonify({"stations": analyzed, "redistribution_plan": plan})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# SUSTAINABILITY
# ═══════════════════════════════════════════════════════════════════════════════
@app.route("/sustainability", methods=["POST"])
def sustainability():
    data     = request.get_json(force=True)
    dist_km  = float(data.get("distance_km", 0))
    trips    = int(data.get("trips", 1))
    if dist_km < 0 or trips < 1:
        return jsonify({"error": "distance_km must be >= 0 and trips >= 1"}), 400
    try:
        result = calculate_co2_savings(dist_km, trips)
        return jsonify(asdict(result))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/sustainability/fleet", methods=["GET"])
def sustainability_fleet():
    try:
        df = load_csv()
        if df is None:
            return jsonify({"error": "bike_rental.csv not found"}), 500
        records = df[["distance_km"]].to_dict(orient="records")
        return jsonify(fleet_co2_stats(records))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# MAINTENANCE
# ═══════════════════════════════════════════════════════════════════════════════
@app.route("/maintenance/assess", methods=["POST"])
def maintenance_assess():
    data = request.get_json(force=True)
    required = ["bike_id", "usage_hours", "days_since_service"]
    missing  = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400
    try:
        result = assess_bike_health(
            int(data["bike_id"]),
            float(data["usage_hours"]),
            int(data["days_since_service"])
        )
        return jsonify(asdict(result))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/maintenance/fleet", methods=["POST"])
def maintenance_fleet():
    data  = request.get_json(force=True)
    bikes = data.get("bikes", [])
    if not bikes:
        return jsonify({"error": "bikes array required"}), 400
    try:
        return jsonify(fleet_maintenance_report(bikes))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/maintenance/demo", methods=["GET"])
def maintenance_demo():
    """Returns simulated fleet report from CSV data (20 unique bikes)."""
    try:
        df = load_csv()
        if df is None:
            return jsonify({"error": "bike_rental.csv not found"}), 500

        sample = (
            df[["bike_id", "usage_hours", "days_since_service"]]
              .drop_duplicates("bike_id")
              .head(20)
        )
        bikes = sample.rename(columns={"days_since_service": "days_since_service"}).to_dict(orient="records")
        return jsonify(fleet_maintenance_report(bikes))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# STATS (extended)
# ═══════════════════════════════════════════════════════════════════════════════
@app.route("/stats", methods=["GET"])
def stats():
    try:
        df = load_csv()
        if df is None:
            return jsonify({"error": "bike_rental.csv not found"}), 500

        hourly   = df.groupby("hour")["rentals"].mean().round(1).to_dict()
        monthly  = df.groupby("month")["rentals"].mean().round(1).to_dict()
        station  = df.groupby("station_id")["rentals"].sum().round(1).to_dict()
        weekday  = df.groupby("weekday")["rentals"].mean().round(1).to_dict()

        # Weather buckets
        df["temp_bucket"] = pd.cut(
            df["temperature"],
            bins=[-999, 10, 20, 30, 999],
            labels=["<10°C", "10–20°C", "20–30°C", "30°C+"]
        )
        weather_buckets = df.groupby("temp_bucket", observed=True)["rentals"].mean().round(1).to_dict()
        weather_buckets = {str(k): v for k, v in weather_buckets.items()}

        # Event impact
        event_impact = {}
        if "event_type" in df.columns:
            event_impact = df.groupby("event_type")["rentals"].mean().round(1).to_dict()

        return jsonify({
            "hourly_avg":     hourly,
            "monthly_avg":    monthly,
            "station_total":  station,
            "weekday_avg":    weekday,
            "weather_buckets": weather_buckets,
            "event_impact":   event_impact,
            "total_records":  int(len(df)),
            "avg_rentals":    round(float(df["rentals"].mean()), 1)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# CSV EXPORT
# ═══════════════════════════════════════════════════════════════════════════════
@app.route("/export/stats", methods=["GET"])
def export_stats():
    try:
        df    = load_csv()
        if df is None:
            return jsonify({"error": "bike_rental.csv not found"}), 500

        limit = min(int(request.args.get("limit", 1000)), 5000)
        cols  = ["date", "hour", "station_id", "rentals",
                 "temperature", "humidity", "windspeed", "rainfall"]
        if "event_type" in df.columns:
            cols.append("event_type")

        csv_data = df[cols].head(limit).to_csv(index=False)
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=bike_rental_stats.csv"}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# USER ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════
@app.route("/user/<int:user_id>/history", methods=["GET"])
def user_history(user_id):
    try:
        df = load_csv()
        if df is None:
            return jsonify({"error": "bike_rental.csv not found"}), 500

        cols = ["date", "hour", "station_id", "distance_km",
                "ride_duration", "co2_saved_g", "eco_score"]
        hist = df[df["user_id"] == user_id][cols].tail(20).to_dict(orient="records")
        return jsonify({"user_id": user_id, "history": hist, "total": len(hist)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/user/<int:user_id>/favorites", methods=["GET"])
def user_favorites(user_id):
    try:
        df = load_csv()
        if df is None:
            return jsonify({"error": "bike_rental.csv not found"}), 500

        favs = (
            df[df["user_id"] == user_id]["station_id"]
              .value_counts()
              .head(3)
              .reset_index()
              .rename(columns={"station_id": "station_id", "count": "visits"})
              .to_dict(orient="records")
        )
        return jsonify({"user_id": user_id, "favorite_stations": favs})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/user/<int:user_id>/eco", methods=["GET"])
def user_eco(user_id):
    try:
        df = load_csv()
        if df is None:
            return jsonify({"error": "bike_rental.csv not found"}), 500

        rides = df[df["user_id"] == user_id][["distance_km"]].to_dict(orient="records")
        if not rides:
            return jsonify({"error": f"No rides found for user {user_id}"}), 404

        return jsonify(get_user_eco_summary(rides))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# ADMIN ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════
@app.route("/admin/model-info", methods=["GET"])
def admin_model_info():
    if model is None:
        return jsonify({"error": "Model not loaded"}), 503
    info = {
        "features":     model.get("features", []),
        "metrics":      model.get("metrics", {}),
        "retrained_at": model.get("retrained_at", "original training"),
    }
    return jsonify(info)


@app.route("/admin/retrain", methods=["POST"])
def admin_retrain():
    key = request.headers.get("X-Admin-Key", "")
    if key != ADMIN_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    def run_retrain():
        from retrain import retrain
        retrain()
        load_model()  # reload updated model

    thread = threading.Thread(target=run_retrain, daemon=True)
    thread.start()
    return jsonify({
        "status":  "retraining_started",
        "message": "Model retraining started in background. Check /admin/model-info after ~2 minutes."
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
