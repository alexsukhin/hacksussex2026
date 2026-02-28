from app.database import Base, engine
from app.models import Plot, Reading

print("Creating tables in Supabase...")
Base.metadata.create_all(bind=engine)
print("Tables created successfully!")