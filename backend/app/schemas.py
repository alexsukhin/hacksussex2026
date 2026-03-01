from pydantic import BaseModel
from uuid import UUID
from datetime import datetime, date
from typing import Optional, List

class ReadingCreate(BaseModel):
    plot_id: UUID
    moisture: int
    light: int

class ReadingResponse(BaseModel):
    id: UUID
    plot_id: UUID
    moisture: int
    light: int
    created_at: datetime
    plot_name: Optional[str] = None
    score: Optional[int] = None
    status: Optional[str] = None
    color: Optional[str] = None
    class Config:
        from_attributes = True

class ZoneStatResponse(BaseModel):
    plot_id: UUID
    stat_date: date
    reading_count: int
    avg_moisture: float
    ideal_moisture: int
    water_saved_l: float
    cost_saved_gbp: float
    energy_saved_kwh: float
    optimal_readings: int
    class Config:
        from_attributes = True

class StatsSummaryResponse(BaseModel):
    period_days: int
    total_water_saved_l: float
    total_cost_saved_gbp: float
    total_energy_saved_kwh: float
    overall_optimal_pct: float
    daily_breakdown: List[dict]
    zone_breakdown: List[dict]