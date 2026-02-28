from fastapi import APIRouter
import requests
from app.config import OPENWEATHER_API_KEY

router = APIRouter(prefix="/weather", tags=["weather"])
LAT, LON = 51.5074, -0.1278

@router.get("/hourly")
def get_hourly_weather():
    if not OPENWEATHER_API_KEY:
        return {"error": "OPENWEATHER_API_KEY not set!"}
    
    url = f"http://api.weatherapi.com/v1/forecast.json?key={OPENWEATHER_API_KEY}&q={LAT},{LON}&days=1&aqi=no&alerts=no"
    resp = requests.get(url)
    data = resp.json()

    if "forecast" not in data:
        return {"error": "Invalid response from WeatherAPI", "raw": data}

    hourly_data = []
    for hour in data["forecast"]["forecastday"][0]["hour"]:
        hourly_data.append({
            "time": hour["time"],
            "temp_c": hour["temp_c"],
            "condition": hour["condition"]["text"],
            "chance_of_rain": hour["chance_of_rain"],
            "rain_mm": hour["precip_mm"]
        })

    return {"location": data["location"]["name"], "hourly": hourly_data}