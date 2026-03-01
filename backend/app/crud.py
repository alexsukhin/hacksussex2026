from sqlalchemy.orm import Session
from sqlalchemy import and_
from app import models, schemas
from datetime import datetime, timezone, timedelta
from collections import defaultdict

BASELINE_L_PER_M2_DAY = 5.0
ZONE_AREA_M2           = 100.0
WATER_COST_PER_L       = 0.003
PUMP_KW                = 0.75
ENERGY_COST_PER_KWH    = 0.28
PUMP_HOURS_PER_L       = 0.0005

def create_reading(db: Session, reading: schemas.ReadingCreate):
    db_reading = models.Reading(**reading.dict())
    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)
    return db_reading

def get_readings(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Reading).order_by(models.Reading.created_at.desc()).offset(skip).limit(limit).all()

def _savings_for_day(avg_moisture: float, ideal_moisture: int):
    if ideal_moisture == 0:
        return dict(water_saved_l=0.0, cost_saved_gbp=0.0, energy_saved_kwh=0.0)
    deficit  = max(0.0, (ideal_moisture - avg_moisture) / ideal_moisture)
    baseline = BASELINE_L_PER_M2_DAY * ZONE_AREA_M2
    actual   = baseline * deficit
    saved_l  = max(0.0, baseline - actual)
    return dict(
        water_saved_l    = saved_l,
        cost_saved_gbp   = saved_l * WATER_COST_PER_L + saved_l * PUMP_HOURS_PER_L * PUMP_KW * ENERGY_COST_PER_KWH,
        energy_saved_kwh = saved_l * PUMP_HOURS_PER_L * PUMP_KW,
    )

def upsert_zone_stat(db: Session, plot_id, moisture: int, ideal_moisture: int):
    """Called on every incoming reading. Upserts today's ZoneStat row."""
    today = datetime.now(timezone.utc).date()
    stat  = db.query(models.ZoneStat).filter(
        and_(models.ZoneStat.plot_id == plot_id, models.ZoneStat.stat_date == today)
    ).first()

    if stat is None:
        stat = models.ZoneStat(
            plot_id=plot_id, stat_date=today,
            reading_count=0, avg_moisture=0.0,
            ideal_moisture=ideal_moisture,
            water_saved_l=0.0, cost_saved_gbp=0.0,
            energy_saved_kwh=0.0, optimal_readings=0,
        )
        db.add(stat)

    n = stat.reading_count
    stat.avg_moisture    = (stat.avg_moisture * n + moisture) / (n + 1)
    stat.reading_count   = n + 1
    stat.ideal_moisture  = ideal_moisture

    score = (moisture / ideal_moisture * 100) if ideal_moisture else 0
    if 80 <= score <= 120:
        stat.optimal_readings += 1

    s = _savings_for_day(stat.avg_moisture, ideal_moisture)
    stat.water_saved_l    = s["water_saved_l"]
    stat.cost_saved_gbp   = s["cost_saved_gbp"]
    stat.energy_saved_kwh = s["energy_saved_kwh"]

    db.commit()
    db.refresh(stat)
    return stat

def get_stats_summary(db: Session, days: int = 7):
    days   = min(max(days, 1), 365)
    cutoff = datetime.now(timezone.utc).date() - timedelta(days=days)
    rows   = db.query(models.ZoneStat).filter(models.ZoneStat.stat_date >= cutoff).all()

    if not rows:
        return dict(period_days=days, total_water_saved_l=0.0,
                    total_cost_saved_gbp=0.0, total_energy_saved_kwh=0.0,
                    overall_optimal_pct=0.0, daily_breakdown=[], zone_breakdown=[])

    total_water  = sum(r.water_saved_l for r in rows)
    total_cost   = sum(r.cost_saved_gbp for r in rows)
    total_energy = sum(r.energy_saved_kwh for r in rows)
    total_reads  = sum(r.reading_count for r in rows)
    total_opt    = sum(r.optimal_readings for r in rows)
    opt_pct      = round(total_opt / total_reads * 100, 1) if total_reads else 0.0

    daily = defaultdict(lambda: {"baseline_l": 0.0, "actual_l": 0.0, "saved_l": 0.0})
    for r in rows:
        d        = str(r.stat_date)
        baseline = BASELINE_L_PER_M2_DAY * ZONE_AREA_M2
        deficit  = max(0.0, (r.ideal_moisture - r.avg_moisture) / r.ideal_moisture) if r.ideal_moisture else 0
        daily[d]["baseline_l"] += round(baseline, 1)
        daily[d]["actual_l"]   += round(baseline * deficit, 1)
        daily[d]["saved_l"]    += round(r.water_saved_l, 1)
    daily_breakdown = [{"date": k, **v} for k, v in sorted(daily.items())]

    zone_map = defaultdict(lambda: {"plot_id": None, "water_saved_l": 0.0,
                                     "reading_count": 0, "optimal_readings": 0})
    for r in rows:
        key = str(r.plot_id)
        zone_map[key]["plot_id"]          = key
        zone_map[key]["water_saved_l"]   += r.water_saved_l
        zone_map[key]["reading_count"]   += r.reading_count
        zone_map[key]["optimal_readings"] += r.optimal_readings

    zone_breakdown = []
    for z in zone_map.values():
        eff = round(z["optimal_readings"] / z["reading_count"] * 100, 1) if z["reading_count"] else 0
        zone_breakdown.append({"plot_id": z["plot_id"],
                                "efficiency_pct": eff,
                                "water_saved_l": round(z["water_saved_l"], 1)})

    return dict(
        period_days=days,
        total_water_saved_l=round(total_water, 1),
        total_cost_saved_gbp=round(total_cost, 2),
        total_energy_saved_kwh=round(total_energy, 2),
        overall_optimal_pct=opt_pct,
        daily_breakdown=daily_breakdown,
        zone_breakdown=zone_breakdown,
    )