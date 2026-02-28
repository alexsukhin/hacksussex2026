from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class ReadingCreate(BaseModel):
    plot_id: UUID
    moisture: int

class ReadingResponse(BaseModel):
    id: UUID
    plot_id: UUID
    moisture: int
    created_at: datetime
    
    plot_name: Optional[str] = None
    score: Optional[int] = None
    status: Optional[str] = None
    color: Optional[str] = None

    class Config:
        from_attributes = True