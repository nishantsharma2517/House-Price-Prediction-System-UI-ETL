# ---------------- STREAMLIT FRONTEND (CONNECTED TO FASTAPI BACKEND) ----------------
import streamlit as st
import requests
import logging

logging.basicConfig(
    filename="pipeline.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("Streamlit frontend started")

st.set_page_config(page_title="House Price Predictor", page_icon="🏠")

st.title("🏠 House Price Prediction (Production System)")
st.write("Raw User Input → Processed Data → ML Model → Prediction")

st.subheader("Enter Housing Details")

col1, col2 = st.columns(2)

with col1:
    longitude = st.number_input("Longitude", value=-122.25)
    latitude = st.number_input("Latitude", value=37.85)
    housing_median_age = st.slider("Housing Median Age", 1, 60, 30)
    total_rooms = st.number_input("Total Rooms", value=2000)
    total_bedrooms = st.number_input("Total Bedrooms", value=400)

with col2:
    population = st.number_input("Population", value=1200)
    households = st.number_input("Households", value=350)
    median_income = st.number_input("Median Income", value=6.5)
    ocean_proximity = st.selectbox(
        "Ocean Proximity",
        ["<1H OCEAN", "INLAND", "ISLAND", "NEAR BAY", "NEAR OCEAN"]
    )

if st.button("🔮 Predict House Price"):
    logging.info("Sending raw data to FastAPI backend")

    url = "http://127.0.0.1:8000/predict"

    payload = {
        "longitude": longitude,
        "latitude": latitude,
        "housing_median_age": housing_median_age,
        "total_rooms": total_rooms,
        "total_bedrooms": total_bedrooms,
        "population": population,
        "households": households,
        "median_income": median_income,
        "ocean_proximity": ocean_proximity
    }

    try:
        response = requests.post(url, json=payload)
        result = response.json()

        if "predicted_house_price" in result:
            st.success(f"🏠 Predicted House Price: ${result['predicted_house_price']:,}")
            logging.info("Prediction displayed successfully")
        else:
            st.error("Prediction failed from backend")

    except Exception as e:
        st.error("❌ Cannot connect to FastAPI backend. Is server running?")
        logging.error(str(e))