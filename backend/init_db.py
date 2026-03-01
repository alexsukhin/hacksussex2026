from app.database import Base, engine
from app.models import Plot, Reading, ZoneStat

print("Creating tables in Supabase...")
Base.metadata.create_all(bind=engine)
print("Tables created: plots, readings, zone_stats")