from fastapi import FastAPI
from app.routers import readings, sensors

app = FastAPI(
    title="Orchard Monitoring Backend",
    version="1.0.0"
)

app.include_router(readings.router)
app.include_router(sensors.router)

@app.get("/")
def root():
    return {"message": "Backend running 🌱"}