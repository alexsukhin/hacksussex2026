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
    __tablename__ = "zone_stats"
    id               = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plot_id          = Column(UUID(as_uuid=True), ForeignKey("plots.id"), nullable=False)
    stat_date        = Column(Date, nullable=False)
    reading_count    = Column(Integer, default=0)
    avg_moisture     = Column(Float, default=0.0)
    ideal_moisture   = Column(Integer, nullable=False)
    water_saved_l    = Column(Float, default=0.0)
    cost_saved_gbp   = Column(Float, default=0.0)
    energy_saved_kwh = Column(Float, default=0.0)
    optimal_readings = Column(Integer, default=0)
    created_at       = Column(DateTime(timezone=True), server_default=func.now())
    updated_at       = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class EmailLog(Base):
    __tablename__ = "email_log"
    plot_id    = Column(UUID(as_uuid=True), ForeignKey("plots.id"), primary_key=True)
    last_sent  = Column(DateTime(timezone=True), nullable=False)