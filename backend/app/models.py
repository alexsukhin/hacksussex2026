from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
import uuid

class Crop(Base):
    __tablename__ = "crops"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    ideal_moisture_min = Column(Integer, nullable=False)
    ideal_moisture_max = Column(Integer, nullable=False)

class Sensor(Base):
    __tablename__ = "sensors"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    location = Column(String)
    crop_id = Column(UUID(as_uuid=True), ForeignKey("crops.id"))

class Reading(Base):
    __tablename__ = "readings"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sensor_id = Column(UUID(as_uuid=True), ForeignKey("sensors.id"))
    moisture = Column(Integer, nullable=False)
    light = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())