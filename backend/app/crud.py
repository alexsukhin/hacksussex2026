from sqlalchemy.orm import Session
from app import models, schemas

def create_reading(db: Session, reading: schemas.ReadingCreate):
    db_reading = models.Reading(**reading.dict())
    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)
    return db_reading