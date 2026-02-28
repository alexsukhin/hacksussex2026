from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import schemas, crud, database

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