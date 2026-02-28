# app/routers/weather.py
from fastapi import APIRouter
import requests
from app.config import OPENWEATHER_API_KEY  # your WeatherAPI key
from datetime import datetime

router = APIRouter(
    prefix="/weather",
    tags=["weather"]
)

LOCATION = "London"

@router.get("/")
def get_today_weather():
    if not OPENWEATHER_API_KEY:
        return {"error": "OPENWEATHER_API_KEY not set!"}

    url = f"http://api.weatherapi.com/v1/forecast.json?key={OPENWEATHER_API_KEY}&q={LOCATION}&days=2&aqi=no&alerts=no"
    resp = requests.get(url)
    data = resp.json()

    # Basic error handling
    if "forecast" not in data or "forecastday" not in data["forecast"]:
        return {"error": "Invalid response from WeatherAPI", "raw": data}

    # Today
    today = data["forecast"]["forecastday"][0]["day"]
    weather_summary = {
        "temp_day": today["avgtemp_c"],
        "temp_night": today["mintemp_c"],  # using min as night temp
        "rain_mm": today.get("totalprecip_mm", 0),
        "weather": today["condition"]["text"],  # e.g., "Partly cloudy"
        "description": today["condition"]["text"]
    }

    # Tomorrow
    tomorrow = data["forecast"]["forecastday"][1]["day"]
    weather_summary["tomorrow_rain_mm"] = tomorrow.get("totalprecip_mm", 0)

    # Optional: add update timestamp
    weather_summary["last_updated"] = datetime.now().isoformat()

    return weather_summary