# backend/seed_db.py
from app.database import engine, SessionLocal, Base
from app.models import Plot

# This automatically creates the tables in Supabase if they don't exist yet!
Base.metadata.create_all(bind=engine)

def seed_plots():
    db = SessionLocal()
    try:
        # Check if plots already exist so we don't duplicate them
        if db.query(Plot).count() == 0:
            print("🌱 Seeding database with initial plots...")
            zones = [
                Plot(name="Zone 1 (Arduino)", crop_type="Tomatoes", ideal_moisture=60),
                Plot(name="Zone 2 (Mock)", crop_type="Lettuce", ideal_moisture=70),
                Plot(name="Zone 3 (Mock)", crop_type="Carrots", ideal_moisture=50),
                Plot(name="Zone 4 (Mock)", crop_type="Peppers", ideal_moisture=65),
                Plot(name="Zone 5 (Mock)", crop_type="Cabbage", ideal_moisture=55),
                Plot(name="Zone 6 (Mock)", crop_type="Spinach", ideal_moisture=60),
                Plot(name="Zone 7 (Mock)", crop_type="Broccoli", ideal_moisture=65),
                Plot(name="Zone 8 (Mock)", crop_type="Kale", ideal_moisture=60),
                Plot(name="Zone 9 (Mock)", crop_type="Radish", ideal_moisture=50),
            ]
            db.add_all(zones)
            db.commit()
            
            print("✅ Database seeded successfully!\nCopy these IDs into your mock_hardware.py script:")
            for zone in zones:
                print(f"{zone.name}: '{zone.id}'")
        else:
            print("✅ Plots already exist in the database. Here are your IDs:")
            for zone in db.query(Plot).all():
                print(f"{zone.name}: '{zone.id}'")
    finally:
        db.close()

if __name__ == "__main__":
    seed_plots()