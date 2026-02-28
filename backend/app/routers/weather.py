from fastapi import APIRouter
import requests
from datetime import datetime, timedelta
from app.config import OPENWEATHER_API_KEY

router = APIRouter(prefix="/weather", tags=["weather"])
LAT, LON = 51.5074, -0.1278

@router.get("/hourly")
def get_hourly_weather():
    if not OPENWEATHER_API_KEY:
        return {"error": "OPENWEATHER_API_KEY not set!"}
    
    url = f"http://api.weatherapi.com/v1/forecast.json?key={OPENWEATHER_API_KEY}&q={LAT},{LON}&days=2&aqi=no&alerts=no"
    resp = requests.get(url)
    data = resp.json()

    if "forecast" not in data:
        return {"error": "Invalid response from WeatherAPI", "raw": data}

    now = datetime.utcnow()
    end = now + timedelta(hours=24)

    hourly_data = []
    # Flatten all hours from both days
    all_hours = []
    for day in data["forecast"]["forecastday"]:
        all_hours.extend(day["hour"])

    # Filter only next 24 hours
    for hour in all_hours:
        hour_time = datetime.strptime(hour["time"], "%Y-%m-%d %H:%M")
        if now <= hour_time <= end:
            hourly_data.append({
                "time": hour["time"],
                "temp_c": hour["temp_c"],
                "condition": hour["condition"]["text"],
                "chance_of_rain": hour["chance_of_rain"],
                "rain_mm": hour["precip_mm"]
            })

    return {"location": data["location"]["name"], "hourly": hourly_data}