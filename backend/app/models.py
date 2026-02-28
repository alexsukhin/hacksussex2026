from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
import uuid

class Plot(Base):
    __tablename__ = "plots"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    crop_type = Column(String, nullable=False)
    ideal_moisture = Column(Integer, nullable=False)

class Reading(Base):
    __tablename__ = "readings"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plot_id = Column(UUID(as_uuid=True), ForeignKey("plots.id"))
    moisture = Column(Integer, nullable=False)
    light = Column(Integer, nullable=False) 
    created_at = Column(DateTime(timezone=True), server_default=func.now())