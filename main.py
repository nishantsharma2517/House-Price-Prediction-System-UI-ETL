# ---------------- FASTAPI BACKEND (RAW → PROCESSED → PREDICTION) ----------------
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import numpy as np
import joblib
import logging

# ---------------- LOGGING ----------------
logging.basicConfig(
    filename="pipeline.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("FastAPI backend started")

# ---------------- LOAD MODEL + SCALER ----------------
model = joblib.load("house_price_model.pkl")
scaler = joblib.load("scaler.pkl")

logging.info("Model and scaler loaded successfully")

app = FastAPI(title="House Price Prediction API")

# ---------------- INPUT SCHEMA (RAW USER DATA) ----------------
class HouseInput(BaseModel):
    longitude: float
    latitude: float
    housing_median_age: float
    total_rooms: float
    total_bedrooms: float
    population: float
    households: float
    median_income: float
    ocean_proximity: str

# ---------------- PREPROCESS (RAW → PROCESSED FEATURES) ----------------
def preprocess_input(data: dict):
    logging.info("Starting raw to processed data transformation")

    df = pd.DataFrame([data])

    # Feature Engineering (same as training)
    df["rooms_per_household"] = df["total_rooms"] / df["households"]
    df["bedrooms_per_room"] = df["total_bedrooms"] / df["total_rooms"]
    df["population_per_household"] = df["population"] / df["households"]

    # One-hot encoding (same as training)
    ocean_cols = [
        "ocean_proximity_<1H OCEAN",
        "ocean_proximity_INLAND",
        "ocean_proximity_ISLAND",
        "ocean_proximity_NEAR BAY",
        "ocean_proximity_NEAR OCEAN"
    ]

    for col in ocean_cols:
        df[col] = 0

    selected_col = f"ocean_proximity_{data['ocean_proximity']}"
    if selected_col in df.columns:
        df[selected_col] = 1

    # Drop original categorical column
    df.drop(columns=["ocean_proximity"], inplace=True)

    # EXACT FEATURE ORDER (must match training)
    feature_columns = [
        'longitude', 'latitude', 'housing_median_age', 'total_rooms',
        'total_bedrooms', 'population', 'households', 'median_income',
        'rooms_per_household', 'bedrooms_per_room',
        'population_per_household',
        'ocean_proximity_<1H OCEAN', 'ocean_proximity_INLAND',
        'ocean_proximity_ISLAND', 'ocean_proximity_NEAR BAY',
        'ocean_proximity_NEAR OCEAN'
    ]

    df = df.reindex(columns=feature_columns, fill_value=0)

    # Scale numeric features (same scaler used in training)
    numeric_cols = df.select_dtypes(include=np.number).columns
    df[numeric_cols] = scaler.transform(df[numeric_cols])

    logging.info("Data successfully converted from RAW → PROCESSED format")
    return df

# ---------------- PREDICTION API ----------------
@app.post("/predict")
def predict(input_data: HouseInput):
    logging.info("Prediction request received from frontend")

    try:
        data_dict = input_data.dict()
        processed_df = preprocess_input(data_dict)

        prediction = model.predict(processed_df)[0]

        logging.info(f"Prediction successful: {prediction}")

        return {
            "predicted_house_price": round(float(prediction), 2),
            "status": "success"
        }

    except Exception as e:
        logging.error(f"Prediction error: {str(e)}")
        return {"error": str(e)}