from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app import schemas, crud, database, models
from app.services.irrigation import evaluate_irrigation
from app.services.email import send_alert

router = APIRouter(
    prefix="/readings",
    tags=["readings"]
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.ReadingResponse)
def create_reading(
    reading: schemas.ReadingCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):

    # 1. Save reading
    new_reading = crud.create_reading(db, reading)

    # 2. Get plot
    plot = db.query(models.Plot).filter(models.Plot.id == new_reading.plot_id).first()

    if plot and new_reading.moisture is not None:
        irrigation_data = evaluate_irrigation(
            new_reading.moisture,
            plot.ideal_moisture
        )

        print("Status:", irrigation_data["status"])

        # 3. Trigger alerts if needed
        if irrigation_data["status"] == "Dry":
            # Direct call for testing
            send_alert(
                to_email="sukhinalexander5679@gmail.com",
                subject=f"Zone {plot.name} Needs Water",
                body=f"Zone {plot.name} is dry!\n\nMoisture: {new_reading.moisture}%"
            )
        elif irrigation_data["status"] == "Oversaturated":
            send_alert(
                to_email="sukhinalexander5679@gmail.com",
                subject=f"Zone {plot.name} Oversaturated",
                body=f"Zone {plot.name} is oversaturated!\n\nMoisture: {new_reading.moisture}%"
            )

    return new_reading

@router.get("/", response_model=List[schemas.ReadingResponse])
def read_readings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), background_tasks: BackgroundTasks = None):
    # 1. Fetch the raw readings from the database
    readings = crud.get_readings(db, skip=skip, limit=limit)
    dashboard_data = []
    
    # 2. Loop through and enrich the data with the watering score
    for r in readings:
        # Get the plot info to find the ideal_moisture and name
        plot = db.query(models.Plot).filter(models.Plot.id == r.plot_id).first()
        
        if not plot:
            continue

        irrigation_data = evaluate_irrigation(r.moisture, plot.ideal_moisture)
        # Package it perfectly for the frontend
        enriched_reading = {
            "id": r.id,
            "plot_id": r.plot_id,
            "moisture": r.moisture,
            "light": r.light,
            "created_at": r.created_at,
            "plot_name": plot.name,
            "score": irrigation_data["score"],
            "status": irrigation_data["status"],
            "color": irrigation_data["color"]
        }
        dashboard_data.append(enriched_reading)
            
    return dashboard_data