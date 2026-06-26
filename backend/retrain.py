"""
Automatic Weekly Model Retraining
Can be scheduled via cron:  0 2 * * 0  python retrain.py
Or run manually.
"""
import os
import pickle
import shutil
import logging
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBRegressor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("retrain.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

MODEL_PATH   = "bike_model.pkl"
BACKUP_DIR   = "model_backups"
DATA_PATH    = "bike_rental.csv"
FEATURES     = ["temperature", "humidity", "hour", "weekday", "holiday",
                "month", "windspeed", "rainfall", "available_bikes", "event_code"]


def backup_model():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    if os.path.exists(MODEL_PATH):
        ts     = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = os.path.join(BACKUP_DIR, f"bike_model_{ts}.pkl")
        shutil.copy(MODEL_PATH, backup)
        log.info(f"Model backed up to {backup}")


def retrain():
    log.info("=== Starting model retraining ===")

    if not os.path.exists(DATA_PATH):
        log.error(f"Data file not found: {DATA_PATH}")
        return False

    # Load data
    df = pd.read_csv(DATA_PATH)
    df["holiday"]    = df["holiday"].astype(int)
    df["event_code"] = LabelEncoder().fit_transform(df.get("event_type", pd.Series(["None"] * len(df))))
    log.info(f"Loaded {len(df)} rows")

    X = df[FEATURES]
    y = df["rentals"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train
    model = XGBRegressor(
        n_estimators=600, max_depth=6, learning_rate=0.04,
        subsample=0.8, colsample_bytree=0.8,
        min_child_weight=3, random_state=42, n_jobs=-1,
        early_stopping_rounds=30, eval_metric="rmse"
    )
    model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)

    y_pred = np.clip(model.predict(X_test), 0, None)
    mae    = mean_absolute_error(y_test, y_pred)
    rmse   = np.sqrt(mean_squared_error(y_test, y_pred))
    r2     = r2_score(y_test, y_pred)
    log.info(f"New model — MAE={mae:.3f}  RMSE={rmse:.3f}  R²={r2:.4f}")

    # Compare to existing model
    improved = True
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "rb") as f:
            old = pickle.load(f)
        old_r2 = old.get("metrics", {}).get("r2", 0)
        if r2 < old_r2 - 0.01:  # allow 1% tolerance
            log.warning(f"New R²={r2:.4f} worse than old R²={old_r2:.4f}. Keeping old model.")
            improved = False

    if improved:
        backup_model()
        with open(MODEL_PATH, "wb") as f:
            pickle.dump({
                "model":    model,
                "features": FEATURES,
                "metrics":  {"mae": mae, "rmse": rmse, "r2": r2},
                "retrained_at": datetime.now().isoformat(),
            }, f)
        log.info("✅ Model updated successfully.")
    return improved


if __name__ == "__main__":
    success = retrain()
    print("Retraining complete." if success else "Retraining skipped.")
