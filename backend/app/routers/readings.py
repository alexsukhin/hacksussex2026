from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone, timedelta
import requests

from app import schemas, crud, database, models
from app.services.irrigation import evaluate_irrigation
from app.services.email import send_alert


router = APIRouter(prefix="/readings", tags=["readings"])

EMAIL_COOLDOWN_HOURS = 0.1 # For testing, set to 1 for production

def _should_send_email(db: Session, plot_id) -> bool:
    """Check DB for last sent time — survives restarts."""
    log = db.query(models.EmailLog).filter(models.EmailLog.plot_id == plot_id).first()
    if log is None:
        return True
    cutoff = datetime.now(timezone.utc) - timedelta(hours=EMAIL_COOLDOWN_HOURS)
    return log.last_sent < cutoff

def _record_email_sent(db: Session, plot_id):
    """Upsert the last-sent timestamp into DB."""
    log = db.query(models.EmailLog).filter(models.EmailLog.plot_id == plot_id).first()
    now = datetime.now(timezone.utc)
    if log is None:
        db.add(models.EmailLog(plot_id=plot_id, last_sent=now))
    else:
        log.last_sent = now
    db.commit()

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
    new_reading = crud.create_reading(db, reading)

    plot = db.query(models.Plot).filter(models.Plot.id == new_reading.plot_id).first()
    if plot is None:
        plot = models.Plot(
            id=new_reading.plot_id,
            name="Zone (auto)",
            crop_type="other",
            ideal_moisture=60,
        )
        db.add(plot)
        db.commit()
        db.refresh(plot)

    irrigation_data = evaluate_irrigation(new_reading.moisture, plot.ideal_moisture)

    crud.upsert_zone_stat(db, new_reading.plot_id, new_reading.moisture, plot.ideal_moisture)

    status = irrigation_data["status"]
    if status in ("Dry", "Oversaturated") and _should_send_email(db, new_reading.plot_id):
        _record_email_sent(db, new_reading.plot_id)
        subject = f"Zone {plot.name} {'Needs Water' if status == 'Dry' else 'Oversaturated'}"
        body = (
            f"Zone {plot.name} is {'dry' if status == 'Dry' else 'oversaturated'}!\n\n"
            f"Moisture: {new_reading.moisture}%\n\n"
            f"Next alert for this zone in {EMAIL_COOLDOWN_HOURS} hour(s)."
        )
        background_tasks.add_task(
            send_alert,
            to_email="sukhinalexander5679@gmail.com",
            subject=subject,
            body=body,
        )

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