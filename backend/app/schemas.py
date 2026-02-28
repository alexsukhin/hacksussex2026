from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class ReadingCreate(BaseModel):
    sensor_id: UUID
    moisture: int
    light: int

class ReadingResponse(BaseModel):
    id: UUID
    sensor_id: UUID
    moisture: int
    light: int
    created_at: datetime

    class Config:
        from_attributes = True