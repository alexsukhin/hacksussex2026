from sqlalchemy.orm import Session
from app import models, schemas

def create_reading(db: Session, reading: schemas.ReadingCreate):
    db_reading = models.Reading(**reading.dict())
    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)
    return db_reading

def get_readings(db: Session, skip: int = 0, limit: int = 100):
    # Fetches the most recent readings first
    return db.query(models.Reading).order_by(models.Reading.created_at.desc()).offset(skip).limit(limit).all()