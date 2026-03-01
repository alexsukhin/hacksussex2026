from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app import schemas, crud, database, models
from app.services.irrigation import evaluate_irrigation
from app.services.email import send_alert

router = APIRouter(prefix="/readings", tags=["readings"])

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
    # 1. Save the reading
    new_reading = crud.create_reading(db, reading)

    # 2. Get plot — if no plot exists yet, auto-create one so stats always work
    plot = db.query(models.Plot).filter(models.Plot.id == new_reading.plot_id).first()

    if plot is None:
        # Auto-create a placeholder plot so readings are never orphaned
        plot = models.Plot(
            id=new_reading.plot_id,
            name=f"Zone (auto)",
            crop_type="other",
            ideal_moisture=60,
        )
        db.add(plot)
        db.commit()
        db.refresh(plot)

    irrigation_data = evaluate_irrigation(new_reading.moisture, plot.ideal_moisture)

    # 3. Upsert today's ZoneStat row — persists across refreshes
    crud.upsert_zone_stat(db, new_reading.plot_id, new_reading.moisture, plot.ideal_moisture)

    # 4. Email alerts (wrapped so a mail failure never breaks the response)
    try:
        if irrigation_data["status"] == "Dry":
            background_tasks.add_task(send_alert,
                to_email="sukhinalexander5679@gmail.com",
                subject=f"Zone {plot.name} Needs Water",
                body=f"Zone {plot.name} is dry!\n\nMoisture: {new_reading.moisture}%")
        elif irrigation_data["status"] == "Oversaturated":
            background_tasks.add_task(send_alert,
                to_email="sukhinalexander5679@gmail.com",
                subject=f"Zone {plot.name} Oversaturated",
                body=f"Zone {plot.name} is oversaturated!\n\nMoisture: {new_reading.moisture}%")
    except Exception as e:
        print(f"Alert scheduling error: {e}")

    return new_reading

@router.get("/", response_model=List[schemas.ReadingResponse])
def read_readings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    readings = crud.get_readings(db, skip=skip, limit=limit)
    dashboard_data = []
    for r in readings:
        plot = db.query(models.Plot).filter(models.Plot.id == r.plot_id).first()
        if not plot:
            continue
        irrigation_data = evaluate_irrigation(r.moisture, plot.ideal_moisture)
        dashboard_data.append({
            "id": r.id, "plot_id": r.plot_id,
            "moisture": r.moisture, "light": r.light,
            "created_at": r.created_at,
            "plot_name": plot.name,
            "score": irrigation_data["score"],
            "status": irrigation_data["status"],
            "color": irrigation_data["color"],
        })
    return dashboard_data