# backend/seed_db.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, SessionLocal, Base
from app.models import Plot
import uuid

Base.metadata.create_all(bind=engine)

# These UUIDs MUST match mock_hardware.py exactly
ZONES = [
    ("Zone 1 (Arduino)", "950b5dd5-c2e6-4aeb-b2d0-8cf5b89c033e", "wheat",       55),
    ("Zone 2 (Mock)",    "03256848-ddcf-4e66-b122-30a4a0af27ac", "barley",      50),
    ("Zone 3 (Mock)",    "4084dce6-1537-45e7-a435-05479b6c5263", "potatoes",    75),
    ("Zone 4 (Mock)",    "f65f9eda-4f72-4273-bc83-014c6fc3a7d7", "oats",        60),
    ("Zone 5 (Mock)",    "27b29098-ce21-4b11-b7e5-69d21fe96c92", "maize",       70),
    ("Zone 6 (Mock)",    "ac02134e-594b-403f-a49d-164d04393b60", "sugar_beet",  65),
    ("Zone 7 (Mock)",    "a72aa36a-757b-4132-b710-9dafb93ff030", "peas",        60),
    ("Zone 8 (Mock)",    "b8a51a6b-e674-42c8-bdf6-029aa5e30c94", "rapeseed",    50),
    ("Zone 9 (Mock)",    "e6e36356-163d-4d79-ad3b-9a195cd6d5b8", "field_beans", 65),
]

def seed_plots():
    db = SessionLocal()
    try:
        created = 0
        for name, plot_id, crop_type, ideal_moisture in ZONES:
            existing = db.query(Plot).filter(Plot.id == uuid.UUID(plot_id)).first()
            if existing is None:
                db.add(Plot(
                    id=uuid.UUID(plot_id),
                    name=name,
                    crop_type=crop_type,
                    ideal_moisture=ideal_moisture,
                ))
                created += 1

        db.commit()

        if created:
            print(f"✅ Seeded {created} new plots into the database.")
        else:
            print("✅ All plots already exist — nothing to seed.")

        print("\nPlot IDs in database:")
        for zone in db.query(Plot).all():
            print(f"  {zone.name}: {zone.id}  (ideal moisture: {zone.ideal_moisture}%)")

    finally:
        db.close()

if __name__ == "__main__":
    seed_plots()