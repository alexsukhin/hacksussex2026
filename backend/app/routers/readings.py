from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app import schemas, crud, database, models
from app.services.irrigation import evaluate_irrigation

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
def create_reading(reading: schemas.ReadingCreate, db: Session = Depends(get_db)):
    return crud.create_reading(db, reading)

@router.get("/", response_model=List[schemas.ReadingResponse])
def read_readings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # 1. Fetch the raw readings from the database
    readings = crud.get_readings(db, skip=skip, limit=limit)
    
    dashboard_data = []
    
    # 2. Loop through and enrich the data with the watering score
    for r in readings:
        # Get the plot info to find the ideal_moisture and name
        plot = db.query(models.Plot).filter(models.Plot.id == r.plot_id).first()
        
        if plot:
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