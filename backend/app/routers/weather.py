from fastapi import APIRouter, Query
import requests
from datetime import datetime, timedelta
from app.config import OPENWEATHER_API_KEY

router = APIRouter(prefix="/weather", tags=["weather"])

@router.get("/hourly")
def get_hourly_weather(lat: float = Query(51.5074), lon: float = Query(-0.1278)):
    if not OPENWEATHER_API_KEY:
        return {"error": "OPENWEATHER_API_KEY not set!"}

    url = f"http://api.weatherapi.com/v1/forecast.json?key={OPENWEATHER_API_KEY}&q={lat},{lon}&days=2&aqi=no&alerts=no"
    resp = requests.get(url)
    data = resp.json()

    if "forecast" not in data:
        return {"error": "Invalid response from WeatherAPI", "raw": data}

    now = datetime.utcnow()
    end = now + timedelta(hours=24)

    hourly_data = []
    all_hours = []
    for day in data["forecast"]["forecastday"]:
        all_hours.extend(day["hour"])

    for hour in all_hours:
        hour_time = datetime.strptime(hour["time"], "%Y-%m-%d %H:%M")
        if now <= hour_time <= end:
            hourly_data.append({
                "time": hour["time"],
                "temp_c": hour["temp_c"],
                "condition": hour["condition"]["text"],
                "chance_of_rain": hour.get("chance_of_rain", 0),
                "rain_mm": hour["precip_mm"]
            })

    return {"location": data["location"]["name"], "hourly": hourly_data}

@router.get("/search")
def search_location(query: str = Query(..., description="City name to search")):
    if not OPENWEATHER_API_KEY:
        return {"error": "OPENWEATHER_API_KEY not set!"}

    url = f"http://api.weatherapi.com/v1/search.json?key={OPENWEATHER_API_KEY}&q={query}"
    resp = requests.get(url)
    return resp.json()