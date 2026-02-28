from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
from app.routers import readings, sensors

app = FastAPI(
    title="Orchard Monitoring Backend",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(readings.router)
app.include_router(sensors.router)

@app.get("/")
def root():
    return {"message": "Backend running 🌱"}