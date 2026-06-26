"""
Exploratory Data Analysis - Bike Rental Dataset
Covers: missing values, correlation, histograms, demand trends,
        rental distribution, peak hours, weekend analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

sns.set_theme(style="whitegrid", palette="muted")
os.makedirs("eda_plots", exist_ok=True)

# ── Load Data ─────────────────────────────────────────────────────────────────
df = pd.read_csv("bike_rental.csv", parse_dates=["date"])
print("Shape:", df.shape)
print("\n── Data Types ──")
print(df.dtypes)

# ── 1. Missing Values ─────────────────────────────────────────────────────────
print("\n── Missing Values ──")
missing = df.isnull().sum()
print(missing[missing > 0] if missing.any() else "No missing values.")

fig, ax = plt.subplots(figsize=(10, 4))
missing.plot(kind="bar", ax=ax, color="coral")
ax.set_title("Missing Values Per Column")
ax.set_ylabel("Count")
plt.tight_layout()
plt.savefig("eda_plots/01_missing_values.png", dpi=150)
plt.close()

# ── 2. Correlation Matrix ─────────────────────────────────────────────────────
numeric_cols = ["temperature", "humidity", "windspeed", "rainfall",
                "available_bikes", "rentals", "hour", "weekday", "month"]
corr = df[numeric_cols].corr()

fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", ax=ax, linewidths=0.5)
ax.set_title("Correlation Matrix")
plt.tight_layout()
plt.savefig("eda_plots/02_correlation_matrix.png", dpi=150)
plt.close()
print("\nCorrelation with rentals:")
print(corr["rentals"].sort_values(ascending=False))

# ── 3. Histogram Plots ────────────────────────────────────────────────────────
hist_cols = ["temperature", "humidity", "windspeed", "rainfall", "rentals", "available_bikes"]
fig, axes = plt.subplots(2, 3, figsize=(15, 8))
axes = axes.flatten()
for i, col in enumerate(hist_cols):
    axes[i].hist(df[col], bins=40, color="steelblue", edgecolor="white", alpha=0.85)
    axes[i].set_title(f"Distribution of {col}")
    axes[i].set_xlabel(col)
    axes[i].set_ylabel("Frequency")
plt.suptitle("Feature Distributions", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig("eda_plots/03_histograms.png", dpi=150)
plt.close()

# ── 4. Demand Trends Over Time ────────────────────────────────────────────────
daily = df.groupby("date")["rentals"].sum().reset_index()
fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(daily["date"], daily["rentals"], color="teal", linewidth=0.8, alpha=0.7)
ax.fill_between(daily["date"], daily["rentals"], alpha=0.2, color="teal")
ax.set_title("Daily Rental Demand Over Time")
ax.set_xlabel("Date")
ax.set_ylabel("Total Rentals")
plt.tight_layout()
plt.savefig("eda_plots/04_demand_trends.png", dpi=150)
plt.close()

# ── 5. Rental Distribution ───────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
axes[0].hist(df["rentals"], bins=50, color="mediumseagreen", edgecolor="white")
axes[0].set_title("Rental Count Distribution")
axes[0].set_xlabel("Rentals")
axes[0].set_ylabel("Frequency")

axes[1].boxplot(df["rentals"], patch_artist=True,
                boxprops=dict(facecolor="lightblue", color="navy"))
axes[1].set_title("Rentals Box Plot")
axes[1].set_ylabel("Rentals")
plt.tight_layout()
plt.savefig("eda_plots/05_rental_distribution.png", dpi=150)
plt.close()

# ── 6. Peak Hours ─────────────────────────────────────────────────────────────
hourly = df.groupby("hour")["rentals"].mean().reset_index()
fig, ax = plt.subplots(figsize=(12, 5))
bars = ax.bar(hourly["hour"], hourly["rentals"],
              color=plt.cm.RdYlGn(hourly["rentals"] / hourly["rentals"].max()))
ax.set_title("Average Rentals by Hour (Peak Hour Analysis)")
ax.set_xlabel("Hour of Day")
ax.set_ylabel("Average Rentals")
ax.set_xticks(range(0, 24))
plt.tight_layout()
plt.savefig("eda_plots/06_peak_hours.png", dpi=150)
plt.close()
print("\nPeak hours:")
print(hourly.sort_values("rentals", ascending=False).head(5))

# ── 7. Weekend vs Weekday Analysis ───────────────────────────────────────────
df["day_type"] = df["weekday"].apply(lambda x: "Weekend" if x >= 5 else "Weekday")
weekend_avg = df.groupby("day_type")["rentals"].mean()

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
weekend_avg.plot(kind="bar", ax=axes[0], color=["steelblue", "coral"], edgecolor="white")
axes[0].set_title("Avg Rentals: Weekday vs Weekend")
axes[0].set_ylabel("Average Rentals")
axes[0].set_xticklabels(weekend_avg.index, rotation=0)

for day_type, grp in df.groupby("day_type"):
    axes[1].hist(grp["rentals"], bins=40, alpha=0.6, label=day_type)
axes[1].set_title("Rental Distribution by Day Type")
axes[1].set_xlabel("Rentals")
axes[1].legend()
plt.tight_layout()
plt.savefig("eda_plots/07_weekend_analysis.png", dpi=150)
plt.close()

# ── 8. Monthly Trends ─────────────────────────────────────────────────────────
month_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
monthly = df.groupby("month")["rentals"].mean().reset_index()
monthly["month_name"] = monthly["month"].apply(lambda x: month_names[x-1])

fig, ax = plt.subplots(figsize=(12, 5))
ax.bar(monthly["month_name"], monthly["rentals"], color="mediumpurple", edgecolor="white")
ax.set_title("Average Rentals by Month")
ax.set_xlabel("Month")
ax.set_ylabel("Average Rentals")
plt.tight_layout()
plt.savefig("eda_plots/08_monthly_trends.png", dpi=150)
plt.close()

print("\n✅ All EDA plots saved to eda_plots/")
print("\nSummary Statistics:")
print(df[["temperature","humidity","windspeed","rainfall","available_bikes","rentals"]].describe().round(2))
