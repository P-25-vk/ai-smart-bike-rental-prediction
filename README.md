# 🚲 AI-Powered Smart Bike Rental Demand Prediction System

> Predict bike rental demand in real-time using XGBoost ML, Flask REST API, React dashboard, and PostgreSQL.

---

## 📋 Project Overview

This system predicts the number of bike rentals based on weather conditions, time of day, and station data. It provides dynamic pricing and weather-based recommendations to help operators manage bike availability efficiently.

**Tech Stack:**
| Layer       | Technology                    |
|-------------|-------------------------------|
| Frontend    | React 18, Chart.js, Axios     |
| Backend     | Flask 3, Flask-CORS           |
| ML Model    | XGBoost, scikit-learn         |
| Database    | PostgreSQL 15                 |
| Deployment  | AWS EC2, RDS, S3              |

---

## 🏗️ Architecture

```
React Frontend (Port 3000)
        │
        ▼
Flask REST API (Port 5000)
        │
   ┌────┴────┐
   ▼         ▼
XGBoost   PostgreSQL
Model      (15k rows)
   │
   ▼
Predictions + Pricing + Recommendations
```

**AWS Deployment:**
```
EC2
├── Flask Backend
└── React Frontend (built static)

RDS
└── PostgreSQL

S3
├── bike_rental.csv
├── bike_model.pkl
└── Backup files
```

---

## 📁 Project Structure

```
AI-Powered Smart Bike Rental Demand Prediction System/
├── backend/
│   ├── generate_dataset.py   ← Create 15k synthetic records
│   ├── db_insert.py          ← Batch insert to PostgreSQL
│   ├── eda.py                ← Exploratory Data Analysis
│   ├── train_model.py        ← XGBoost training
│   ├── recommendation.py     ← Weather recommendation engine
│   ├── pricing.py            ← Dynamic pricing algorithm
│   ├── app.py                ← Flask API
│   ├── requirements.txt      ← Python dependencies
│   └── tests/
│       └── test_api.py       ← pytest test suite
├── frontend/
│   ├── public/index.html
│   ├── src/
│   │   ├── App.js
│   │   ├── App.css
│   │   ├── index.js
│   │   ├── index.css
│   │   └── components/
│   │       ├── Header.js
│   │       ├── PredictionForm.js
│   │       ├── ResultCards.js
│   │       └── GraphDashboard.js
│   └── package.json
└── README.md
```

---

## ⚙️ Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 15+

### 1. Clone & Setup Backend

```bash
cd backend
pip install -r requirements.txt
```

### 2. Generate Dataset

```bash
python generate_dataset.py
# Creates: bike_rental.csv (15,000 rows)
```

### 3. Setup PostgreSQL

```sql
CREATE DATABASE bike_rental_db;
```
Update `DB_CONFIG` in `db_insert.py` with your credentials, then:

```bash
python db_insert.py
```

### 4. Run EDA

```bash
python eda.py
# Saves 8 plots to eda_plots/
```

### 5. Train the Model

```bash
python train_model.py
# Saves: bike_model.pkl
# Saves: feature_importance.png, actual_vs_predicted.png
```

### 6. Start Flask Backend

```bash
python app.py
# Running on http://localhost:5000
```

### 7. Setup & Start Frontend

```bash
cd frontend
npm install
npm start
# Running on http://localhost:3000
```

---

## 📊 Dataset

**15,000 synthetic records** generated with realistic patterns:

| Column          | Type    | Description                    |
|-----------------|---------|--------------------------------|
| date            | DATE    | Calendar date                  |
| hour            | INT     | Hour of day (0–23)             |
| weekday         | INT     | Day of week (0=Mon, 6=Sun)     |
| month           | INT     | Month (1–12)                   |
| holiday         | BOOLEAN | Public holiday flag            |
| temperature     | FLOAT   | Temperature in °C              |
| humidity        | FLOAT   | Humidity percentage            |
| windspeed       | FLOAT   | Wind speed in km/h             |
| rainfall        | FLOAT   | Rainfall in mm                 |
| station_id      | INT     | Station identifier (1–20)      |
| available_bikes | INT     | Bikes available at station     |
| rentals         | INT     | **Target: number of rentals**  |

---

## 🤖 Model Training

**Algorithm:** XGBoost Regressor  
**Features:** temperature, humidity, hour, weekday, holiday, month, windspeed, rainfall, available_bikes  
**Split:** 80% train / 20% test  

Typical performance:
- MAE:  ~4–6
- RMSE: ~6–9
- R²:   ~0.92–0.96

---

## 🔌 API Documentation

### `GET /`
Health check.
```json
{ "status": "ok", "service": "Bike Rental Prediction API", "model": "loaded" }
```

### `POST /predict`
**Request:**
```json
{
  "temperature": 25.0,
  "humidity": 60.0,
  "hour": 8,
  "weekday": 1,
  "holiday": false,
  "month": 6,
  "windspeed": 10.0,
  "rainfall": 0.0,
  "available_bikes": 20
}
```

**Response:**
```json
{
  "predicted_demand": 87.3,
  "price": 57.50,
  "base_price": 50.0,
  "currency": "INR",
  "price_tier": "Standard+",
  "price_adjustments": ["Surge +15% (demand > 70)"],
  "recommendation": "☀️ Ideal cycling weather — demand likely high.",
  "demand_category": "High",
  "operational_tip": "Ensure sufficient bike availability."
}
```

### `GET /stats`
Returns aggregated stats for dashboard charts.
```json
{
  "hourly_avg":    { "0": 12.3, "8": 45.6, ... },
  "monthly_avg":   { "1": 30.1, "6": 72.4, ... },
  "station_total": { "1": 3200, "2": 2800, ... }
}
```

---

## 💰 Dynamic Pricing Logic

| Condition         | Adjustment      |
|-------------------|-----------------|
| Demand > 100      | +30% surge      |
| Demand > 70       | +15% surge      |
| Rainfall > 20mm   | -10% discount   |
| Base price        | ₹50             |

---

## 🌤️ Weather Recommendation Engine

| Condition               | Recommendation                         |
|-------------------------|----------------------------------------|
| Rainfall > 20mm         | 🌧️ Low demand expected                 |
| Temperature 20–30°C     | ☀️ Ideal cycling weather               |
| Humidity > 85%          | 💧 Demand may decrease                 |
| Temperature < 10°C      | 🥶 Cold — lower demand                 |
| Temperature > 35°C      | 🌡️ Very hot — demand may decrease      |

---

## 🧪 Testing

```bash
cd backend
pytest tests/test_api.py -v
```

Tests cover:
- Prediction endpoint (happy path, missing fields, edge cases)
- Pricing function (all pricing rules, edge values)
- Recommendation function (all weather conditions)

---

## 🚀 Deployment (AWS)

### EC2 (Flask + React)
```bash
# Install dependencies
sudo apt update && sudo apt install python3-pip nodejs npm nginx -y
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Build React
npm run build
# Serve via Nginx
```

### RDS (PostgreSQL)
- Create RDS PostgreSQL 15 instance
- Update `DB_CONFIG` in `db_insert.py`
- Run `python db_insert.py`

### S3
```bash
aws s3 cp bike_rental.csv s3://your-bucket/dataset/
aws s3 cp bike_model.pkl  s3://your-bucket/models/
```

---

## 📸 Screenshots

| Component            | Description                                      |
|----------------------|--------------------------------------------------|
| Prediction Form      | Input 9 weather + time features, click Predict  |
| Result Cards         | Demand count, price, weather insight, ops tip   |
| Analytics Dashboard  | 4 Chart.js charts + 4 KPI summary cards         |

---

## 🔮 Future Enhancements

- [ ] Real-time data ingestion from weather APIs (OpenWeatherMap)
- [ ] LSTM model for time-series forecasting
- [ ] User authentication & per-station dashboards
- [ ] WebSocket live demand updates
- [ ] Mobile app (React Native)
- [ ] Automated model retraining pipeline
- [ ] A/B testing for dynamic pricing strategies
- [ ] Geospatial heatmap of station demand

---

## 📄 License

MIT License — free to use and modify.
