from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Date
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

class ZoneStat(Base):
    """
    One row written per zone per day, storing pre-computed savings metrics.
    Written by the backend every time a reading comes in (upserted by date+plot_id).
    This is what the Statistics tab reads — it survives page refreshes forever.
    """
    __tablename__ = "zone_stats"
    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plot_id       = Column(UUID(as_uuid=True), ForeignKey("plots.id"), nullable=False)
    stat_date     = Column(Date, nullable=False)          # The calendar day this row covers
    reading_count = Column(Integer, default=0)            # How many readings contributed
    avg_moisture  = Column(Float, default=0.0)            # Average moisture for the day
    ideal_moisture= Column(Integer, nullable=False)        # Snapshot of ideal at time of writing
    water_saved_l = Column(Float, default=0.0)            # Litres saved vs. baseline that day
    cost_saved_gbp= Column(Float, default=0.0)            # £ saved that day
    energy_saved_kwh = Column(Float, default=0.0)         # kWh saved that day
    optimal_readings = Column(Integer, default=0)         # Readings that were in optimal range
    created_at    = Column(DateTime(timezone=True), server_default=func.now())
    updated_at    = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())