"""
XGBoost Model Training — Enhanced with event awareness
Saves: bike_model.pkl + forecast_model.pkl
"""
import pandas as pd
import numpy as np
import pickle
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBRegressor

df = pd.read_csv("bike_rental.csv")
df["holiday"]    = df["holiday"].astype(int)
df["event_code"] = LabelEncoder().fit_transform(df["event_type"])

FEATURES = ["temperature", "humidity", "hour", "weekday", "holiday",
            "month", "windspeed", "rainfall", "available_bikes", "event_code"]
TARGET   = "rentals"

X = df[FEATURES]
y = df[TARGET]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = XGBRegressor(
    n_estimators=600, max_depth=6, learning_rate=0.04,
    subsample=0.8, colsample_bytree=0.8,
    min_child_weight=3, reg_alpha=0.1, reg_lambda=1.0,
    random_state=42, n_jobs=-1,
    early_stopping_rounds=30, eval_metric="rmse"
)
model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=50)

y_pred = np.clip(model.predict(X_test), 0, None)
mae  = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2   = r2_score(y_test, y_pred)
print(f"\n── Evaluation ──  MAE={mae:.3f}  RMSE={rmse:.3f}  R²={r2:.4f}")

# Feature importance plot
importance = pd.Series(model.feature_importances_, index=FEATURES).sort_values()
fig, ax = plt.subplots(figsize=(9, 5))
importance.plot(kind="barh", ax=ax, color="teal")
ax.set_title("XGBoost Feature Importance")
plt.tight_layout()
plt.savefig("feature_importance.png", dpi=150)
plt.close()

# Actual vs Predicted
fig, ax = plt.subplots(figsize=(8, 6))
ax.scatter(y_test, y_pred, alpha=0.3, s=10, color="royalblue")
lims = [min(y_test.min(), y_pred.min()), max(y_test.max(), y_pred.max())]
ax.plot(lims, lims, "r--", linewidth=1.5)
ax.set_xlabel("Actual Rentals"); ax.set_ylabel("Predicted")
ax.set_title(f"Actual vs Predicted  (R²={r2:.3f})")
plt.tight_layout()
plt.savefig("actual_vs_predicted.png", dpi=150)
plt.close()

with open("bike_model.pkl", "wb") as f:
    pickle.dump({"model": model, "features": FEATURES,
                 "metrics": {"mae": mae, "rmse": rmse, "r2": r2}}, f)

print("✅ bike_model.pkl saved")
