from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app import crud, database

router = APIRouter(prefix="/stats", tags=["stats"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/summary")
def get_stats_summary(days: int = Query(default=7, ge=1, le=365), db: Session = Depends(get_db)):
    """
    Returns aggregated savings stats for the last `days` days.
    Reads from the zone_stats table — persists across page refreshes.
    """
    return crud.get_stats_summary(db, days=days)