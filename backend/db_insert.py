"""
Database Insertion Script
Reads bike_rental.csv and inserts all rows into PostgreSQL using batch inserts.
Credentials are read from environment variables (see .env.example).
"""

import os
import psycopg2
import pandas as pd
from psycopg2.extras import execute_batch

# ── DB CONFIG — reads from environment variables ──────────────────────────────
DB_CONFIG = {
    "host":     os.environ.get("DB_HOST",     "localhost"),
    "port":     int(os.environ.get("DB_PORT", 5432)),
    "database": os.environ.get("DB_NAME",     "bike_rental_db"),
    "user":     os.environ.get("DB_USER",     "postgres"),
    "password": os.environ.get("DB_PASSWORD", "your_password"),
}

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS bike_rentals (
    id                  SERIAL PRIMARY KEY,
    date                DATE,
    hour                INT,
    weekday             INT,
    month               INT,
    holiday             BOOLEAN,
    event_type          VARCHAR(20),
    temperature         FLOAT,
    humidity            FLOAT,
    windspeed           FLOAT,
    rainfall            FLOAT,
    station_id          INT,
    available_bikes     INT,
    total_docks         INT,
    rentals             INT,
    user_id             INT,
    bike_id             INT,
    ride_duration       INT,
    distance_km         FLOAT,
    co2_saved_g         FLOAT,
    eco_score           FLOAT,
    usage_hours         FLOAT,
    maintenance_due     BOOLEAN,
    days_since_service  INT
);
"""

INSERT_SQL = """
INSERT INTO bike_rentals
    (date, hour, weekday, month, holiday, event_type,
     temperature, humidity, windspeed, rainfall,
     station_id, available_bikes, total_docks, rentals,
     user_id, bike_id, ride_duration, distance_km,
     co2_saved_g, eco_score, usage_hours, maintenance_due, days_since_service)
VALUES
    (%(date)s, %(hour)s, %(weekday)s, %(month)s, %(holiday)s, %(event_type)s,
     %(temperature)s, %(humidity)s, %(windspeed)s, %(rainfall)s,
     %(station_id)s, %(available_bikes)s, %(total_docks)s, %(rentals)s,
     %(user_id)s, %(bike_id)s, %(ride_duration)s, %(distance_km)s,
     %(co2_saved_g)s, %(eco_score)s, %(usage_hours)s, %(maintenance_due)s,
     %(days_since_service)s);
"""


def load_data(filepath: str) -> list[dict]:
    df = pd.read_csv(filepath)
    df["date"] = pd.to_datetime(df["date"]).dt.date
    df["holiday"] = df["holiday"].astype(bool)
    return df.to_dict(orient="records")


def insert_data(records: list[dict]) -> None:
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Create table
        cursor.execute(CREATE_TABLE_SQL)
        conn.commit()
        print("Table ready.")

        # Batch insert (500 rows per batch)
        BATCH_SIZE = 500
        total = len(records)
        for i in range(0, total, BATCH_SIZE):
            batch = records[i : i + BATCH_SIZE]
            execute_batch(cursor, INSERT_SQL, batch, page_size=BATCH_SIZE)
            conn.commit()
            print(f"Inserted rows {i+1} – {min(i+BATCH_SIZE, total)} / {total}")

        print(f"\n✅ All {total} rows inserted successfully.")

    except psycopg2.OperationalError as e:
        print(f"Connection error: {e}")
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    records = load_data("bike_rental.csv")
    print(f"Loaded {len(records)} records from bike_rental.csv")
    insert_data(records)
