# Requirements — AI-Powered Smart Bike Rental Demand Prediction System

## Overview

A full-stack ML-powered platform that predicts bike rental demand across 50–100 stations using XGBoost, provides dynamic pricing, weather-based recommendations, smart operations management, sustainability tracking, and bike maintenance monitoring — served through a Flask REST API and a React dashboard.

---

## Current Implementation Status

The following is already built and working:

| Module | Status |
|---|---|
| Synthetic dataset generation (15k rows, 75 stations) | ✅ Done |
| XGBoost model training with event awareness (10 features) | ✅ Done |
| `/predict` API endpoint (9 features — **feature mismatch bug**) | ⚠️ Bug |
| `/stats` API endpoint (hourly, monthly, station aggregates) | ✅ Done |
| Dynamic pricing engine (`pricing.py`) | ✅ Done |
| Weather recommendation engine (`recommendation.py`) | ✅ Done |
| 24-hour forecast logic (`forecast.py`) | ✅ Logic only — no API endpoint |
| Bike redistribution & alerts (`redistribution.py`) | ✅ Logic only — no API endpoint |
| Sustainability / CO₂ calculator (`sustainability.py`) | ✅ Logic only — no API endpoint |
| Predictive maintenance (`maintenance.py`) | ✅ Logic only — no API endpoint |
| Weekly auto-retraining (`retrain.py`) | ✅ Standalone script |
| EDA plots (`eda.py`) | ✅ Standalone script |
| PostgreSQL batch insert (`db_insert.py`) | ⚠️ Hardcoded password, incomplete schema |
| React prediction form + result cards | ✅ Done |
| React analytics dashboard (4 Chart.js charts) | ✅ Done |
| Pytest suite (predict, pricing, recommendation) | ✅ Done |
| AWS deployment configs (nginx, gunicorn, deploy script) | ✅ Done |

The following features are listed in the feature spec but **not yet implemented**:

- Bonus: AI chatbot assistant
- Bonus: Admin dashboard
- Bonus: Export reports as PDF/CSV
- Bonus: Dark/Light mode
- Bonus: Email alerts for bike shortages
- Bonus: API documentation with Swagger
- Frontend tabs: Forecast, Operations, Sustainability, Maintenance, Notifications
- Event type input in prediction form
- Dark/light theme toggle

---

## Requirements

### REQ-1 — Fix Feature Mismatch (Critical Bug)

**User Story:** As a user submitting a prediction, I want the result to be accurate so that I can trust the demand forecast.

**Acceptance Criteria:**

- 1.1 — `app.py` `FEATURE_ORDER` must include `event_code` as the 10th feature, matching `train_model.py`.
- 1.2 — The `/predict` endpoint must accept an optional `event_type` field (string: "None", "Festival", "Concert", "Sports") and map it to `event_code` using the same `EVENT_MAP` as `forecast.py`.
- 1.3 — When `event_type` is not provided, it defaults to `"None"` (event_code = 0) so existing clients do not break.
- 1.4 — The `PredictionForm` in the frontend must include an Event Type select field with options: None, Festival, Concert, Sports.
- 1.5 — All existing pytest tests must continue to pass after the fix.

---

### REQ-2 — 24-Hour Forecast API Endpoint

**User Story:** As an operator, I want to see predicted demand for every hour of the next 24 hours so I can plan staffing and bike deployment in advance.

**Acceptance Criteria:**

- 2.1 — A `POST /forecast` endpoint must be added to `app.py`.
- 2.2 — The endpoint accepts: `station_id`, `temperature`, `humidity`, `windspeed`, `rainfall`, `available_bikes`, `weekday`, `month`, `holiday` (optional, default false), `event_type` (optional, default "None").
- 2.3 — The response returns an array of 24 objects, each with: `hour` (int), `label` (e.g. "08:00"), `predicted_demand` (float), `peak` (bool).
- 2.4 — It also returns `peak_hours`: the top 3 hours by demand.
- 2.5 — The frontend must have a "📈 24h Forecast" tab that calls this endpoint and renders results as a line chart using Chart.js.
- 2.6 — The forecast tab must allow the user to select event type and shows a highlighted peak hour on the chart.

---

### REQ-3 — Smart Operations API Endpoints

**User Story:** As a fleet operator, I want to see real-time low-stock alerts and redistribution recommendations so I can prevent bike shortages across stations.

**Acceptance Criteria:**

- 3.1 — A `POST /operations/analyze` endpoint must wrap `analyze_stations()` from `redistribution.py`.
- 3.2 — Input: a JSON array `stations`, each with `station_id`, `available_bikes`, `total_docks`, `predicted_demand`.
- 3.3 — Response: enriched station list with `alert`, `action`, `occupancy_pct` for each station.
- 3.4 — A `POST /operations/redistribute` endpoint must wrap `redistribution_plan()` and return a list of transfer recommendations with `from_station`, `to_station`, `bikes_to_move`, `priority`, `reason`.
- 3.5 — A `GET /operations/demo` endpoint must return a simulated dataset of 10 stations (drawn from `bike_rental.csv` station averages) so the frontend can display the operations panel without manual input.
- 3.6 — The frontend must have a "🚦 Operations" tab showing a station status table with color-coded alerts (red = critical, amber = warning, green = good) and a redistribution plan card.

---

### REQ-4 — Sustainability API Endpoint

**User Story:** As a user, I want to see my carbon savings, eco score, and eco badge after entering my ride details so I feel rewarded for choosing a bike over a car.

**Acceptance Criteria:**

- 4.1 — A `POST /sustainability` endpoint must wrap `calculate_co2_savings()` from `sustainability.py`.
- 4.2 — Input: `distance_km` (float), `trips` (int, optional default 1).
- 4.3 — Response: `distance_km`, `co2_saved_kg`, `co2_saved_g`, `trees_equivalent`, `eco_score`, `badge`, `message`.
- 4.4 — A `GET /sustainability/fleet` endpoint must compute fleet-wide CO₂ stats from `bike_rental.csv` using `fleet_co2_stats()`.
- 4.5 — The frontend must have a "🌱 Sustainability" tab with an eco score input panel and a fleet-wide stats summary card.
- 4.6 — The eco badge must be visually displayed with a color-coded badge matching the tier (Starter, Bronze, Silver, Gold, Platinum).

---

### REQ-5 — Bike Maintenance API Endpoints

**User Story:** As a fleet manager, I want a dashboard showing the health status of all bikes so I can schedule servicing before bikes break down.

**Acceptance Criteria:**

- 5.1 — A `POST /maintenance/assess` endpoint must wrap `assess_bike_health()` from `maintenance.py`.
- 5.2 — Input: `bike_id` (int), `usage_hours` (float), `days_since_service` (int).
- 5.3 — Response: `health_score`, `status`, `alert`, `next_service_in`, `wear_components` (per-component wear percentages).
- 5.4 — A `POST /maintenance/fleet` endpoint must wrap `fleet_maintenance_report()` and accept a JSON array of bike objects.
- 5.5 — A `GET /maintenance/demo` endpoint must return a simulated fleet report using `usage_hours` and `days_since_service` from `bike_rental.csv` (sampled 20 unique bikes).
- 5.6 — The frontend must have a "🔧 Maintenance" tab showing a fleet health summary (total, critical, warning, good counts) and a per-bike health table with color-coded status badges.
- 5.7 — Wear component breakdown must be shown as a horizontal progress bar for each component (brakes, chain, tyres, gears, bearings).

---

### REQ-6 — Enhanced Stats Endpoint

**User Story:** As a data analyst, I want richer aggregated stats from the backend so the analytics dashboard can show more insights.

**Acceptance Criteria:**

- 6.1 — The `/stats` endpoint must be extended to also return: `weekday_avg` (avg rentals by weekday 0–6), `event_impact` (avg rentals by event_type), `weather_buckets` (avg rentals grouped by temperature range: <10, 10–20, 20–30, 30+), `total_records` (int), `avg_rentals` (float).
- 6.2 — The `GraphDashboard` frontend component must render two additional charts: "Weekday Demand Pattern" (bar chart) and "Weather Impact on Rentals" (bar chart by temperature bucket).
- 6.3 — The total record count and average rental must be shown in a summary stat line below the dashboard header.

---

### REQ-7 — Dark / Light Mode

**User Story:** As a user, I want to toggle between dark and light themes so the dashboard is comfortable in different lighting environments.

**Acceptance Criteria:**

- 7.1 — A theme toggle button must be present in the `Header` component (🌙/☀️ icon).
- 7.2 — The app must default to light mode.
- 7.3 — Dark mode must override all CSS custom properties (`--surface`, `--background`, `--text`, `--border`, etc.) to dark equivalents via a `data-theme="dark"` attribute on `<body>`.
- 7.4 — Theme preference must be persisted in `localStorage` and applied on page load.
- 7.5 — The toggle must be accessible (keyboard navigable, aria-label provided).

---

### REQ-8 — Notification Center

**User Story:** As an operator, I want a notification panel that surfaces active alerts (low stock, maintenance due, shortage risk) so I can take action without manually checking each tab.

**Acceptance Criteria:**

- 8.1 — A bell icon (🔔) in the `Header` must show a badge count of active alerts.
- 8.2 — Clicking the bell opens a dropdown notification panel.
- 8.3 — Notifications are sourced by calling `/operations/demo` and `/maintenance/demo` on app load.
- 8.4 — Each notification shows: alert type (Low Stock / Maintenance / Shortage), station or bike ID, and the alert message.
- 8.5 — Notifications can be dismissed individually.
- 8.6 — The badge count reflects undismissed alerts only.

---

### REQ-9 — Rental Cost Estimator

**User Story:** As a user, I want to estimate my rental cost before booking so I know what to expect to pay.

**Acceptance Criteria:**

- 9.1 — A "💰 Cost Estimator" section must be added to the "Predict Demand" tab, below the result cards.
- 9.2 — The estimator takes: duration (minutes), and uses the predicted demand and rainfall already present in the form.
- 9.3 — It calls `calculate_price()` internally (no new API endpoint needed) via the `/predict` response price field.
- 9.4 — It displays: estimated cost (price × duration / 60), price tier, and applicable adjustments.
- 9.5 — Duration input range is 5 to 480 minutes.

---

### REQ-10 — Export Reports as CSV

**User Story:** As an administrator, I want to download the current analytics data as a CSV file so I can do further analysis in Excel.

**Acceptance Criteria:**

- 10.1 — A `GET /export/stats` endpoint must return a CSV file with columns: date, hour, station_id, rentals, temperature, humidity, windspeed, rainfall, event_type.
- 10.2 — The endpoint must support an optional query param `limit` (default 1000, max 5000).
- 10.3 — The response must set `Content-Type: text/csv` and `Content-Disposition: attachment; filename=bike_rental_stats.csv`.
- 10.4 — The frontend analytics dashboard must include a "⬇ Export CSV" button that triggers this download.

---

### REQ-11 — Swagger / OpenAPI Documentation

**User Story:** As a developer integrating with this API, I want auto-generated API documentation so I can explore and test all endpoints without reading source code.

**Acceptance Criteria:**

- 11.1 — `flask-swagger-ui` and `flasgger` must be added to `requirements.txt`.
- 11.2 — All existing and new endpoints must have docstring-based Swagger annotations.
- 11.3 — Swagger UI must be served at `GET /docs`.
- 11.4 — The `/predict` endpoint documentation must include a working example request body.

---

### REQ-12 — Fix Database Credentials & Schema

**User Story:** As a developer deploying this project, I want database credentials read from environment variables so I don't accidentally commit passwords to version control.

**Acceptance Criteria:**

- 12.1 — `db_insert.py` must read `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` from environment variables (using `os.environ.get()`), with the current hardcoded values as fallback defaults only.
- 12.2 — The `.env.example` file must document all five database environment variables.
- 12.3 — The `CREATE TABLE` SQL in `db_insert.py` must be updated to include the full dataset schema: `event_type`, `total_docks`, `user_id`, `bike_id`, `ride_duration`, `distance_km`, `co2_saved_g`, `eco_score`, `usage_hours`, `maintenance_due`, `days_since_service`.
- 12.4 — The `INSERT_SQL` must insert all 22 columns from the dataset.

---

### REQ-13 — Ride History & Favorite Stations (User Features)

**User Story:** As a returning user, I want to see my past rides and frequently used stations so I can quickly plan my next rental.

**Acceptance Criteria:**

- 13.1 — A `GET /user/:user_id/history` endpoint must return the last 20 ride records for a given user from the CSV (filtered by `user_id`).
- 13.2 — Each record includes: `date`, `hour`, `station_id`, `distance_km`, `ride_duration`, `co2_saved_g`, `eco_score`.
- 13.3 — A `GET /user/:user_id/favorites` endpoint must return the top 3 most-visited `station_id` values for that user.
- 13.4 — The frontend must have a "👤 My Rides" tab showing a paginated ride history table and a "Favorite Stations" card.

---

### REQ-14 — Reward Badges & Achievements

**User Story:** As a user, I want to earn badges for my eco-friendly riding so I stay motivated to use the bike rental service.

**Acceptance Criteria:**

- 14.1 — A `GET /user/:user_id/eco` endpoint must call `get_user_eco_summary()` using the user's total distance from ride history.
- 14.2 — The response includes: `total_trips`, `total_km`, `co2_saved_kg`, `trees_equivalent`, `eco_score`, `badge`, `message`.
- 14.3 — The "🌱 Sustainability" tab must include a "My Eco Profile" section that displays the badge, eco score progress bar, and CO₂ savings.
- 14.4 — Five badge tiers must be visually distinct: 🌱 Starter (grey), 🥉 Bronze (bronze), 🥈 Silver (silver), 🥇 Gold (gold), 🏆 Platinum (blue-purple gradient).

---

### REQ-15 — Automatic Weekly Retraining — Trigger via API

**User Story:** As an administrator, I want to manually trigger model retraining from the dashboard so I can update the model after adding new data without SSH access.

**Acceptance Criteria:**

- 15.1 — A `POST /admin/retrain` endpoint must call the `retrain()` function from `retrain.py` asynchronously (in a background thread).
- 15.2 — The endpoint immediately returns `{"status": "retraining_started", "message": "..."}` rather than waiting for completion.
- 15.3 — A `GET /admin/model-info` endpoint must return the current model's stored metrics (`mae`, `rmse`, `r2`) and `retrained_at` timestamp if available.
- 15.4 — The frontend analytics dashboard must show a "Model Info" card with current metrics and a "🔄 Retrain Model" button (visible, but not required to call the API — the button can show a toast/confirmation).

---

## Non-Functional Requirements

### Performance
- NFR-1: The `/predict` endpoint must respond in under 500ms for single predictions.
- NFR-2: The `/stats` endpoint must respond in under 2 seconds for 15,000 records.
- NFR-3: The `/forecast` endpoint must return 24-hour predictions in under 1 second.

### Security
- NFR-4: CORS must be restricted to the frontend origin in production (configurable via environment variable `ALLOWED_ORIGINS`).
- NFR-5: All database credentials must come from environment variables, never hardcoded.
- NFR-6: The `/admin/retrain` endpoint should be protected by a simple API key check via the `X-Admin-Key` request header.

### Accessibility
- NFR-7: All interactive elements must be keyboard navigable with visible focus indicators.
- NFR-8: All charts must have aria-label attributes describing their content.
- NFR-9: Color is never the sole means of conveying information (badges always include text labels).

### Maintainability
- NFR-10: All new Flask endpoints must be registered in Swagger with example request/response bodies.
- NFR-11: All new backend modules imported by `app.py` must have corresponding pytest tests.

---

## Out of Scope (for this iteration)

- Real-time weather API integration (OpenWeatherMap) — future enhancement
- WebSocket live demand updates — future enhancement
- Email alerts for bike shortages — future enhancement
- Mobile app (React Native) — future enhancement
- AI chatbot assistant — future enhancement
- User authentication / login system — future enhancement
- LSTM time-series model — future enhancement
