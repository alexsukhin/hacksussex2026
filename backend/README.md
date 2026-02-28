# Orchard Monitoring Backend

FastAPI backend for orchard monitoring.
Stores sensor readings (moisture, light) in Supabase/PostgreSQL. Modular, hackathon-ready, and designed to integrate with hardware and frontend dashboards.

Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI entry point
│   ├── config.py        # Environment variables
│   ├── database.py      # SQLAlchemy engine & session
│   ├── models.py        # DB tables: Crops, Sensors, Readings
│   ├── schemas.py       # Pydantic models
│   ├── crud.py          # DB operations
│   ├── routers/         # API endpoints
│   │     ├── __init__.py
│   │     ├── sensors.py
│   │     └── readings.py
│   └── services/        # Business logic (irrigation etc.)
│         ├── __init__.py
│         └── irrigation.py
├── .env                 # Environment variables
├── requirements.txt     # Python dependencies
└── README.md
```

Setup

1. Clone the repo:
```
git clone https://github.com/alexsukhin/hacksussex2026
cd orchard-project/backend
```

2. Create a virtual environment:
```
python -m venv venv
source venv/bin/activate
# Windows: venv\Scripts\activate
```
3. Install dependencies:

```
pip install -r requirements.txt
```

4. Configure .env:

```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.xxxxx.supabase.co:5432/postgres
```

Replace with your Supabase/Postgres credentials.

Run the App

```
uvicorn app.main:app --reload
```

Next Steps

**Database / Models**

* [ ] Auto-create tables in Supabase from SQLAlchemy models (`Base.metadata.create_all`)
* [ ] Add `Alerts` table to store notifications (low/high moisture)
* [ ] Add `Users` table if multi-user support is needed
* [ ] Add `CropSettings` table for dynamic irrigation rules
* [ ] Add indices to frequently queried columns (e.g., `sensor_id`, `created_at`)

**API / CRUD Endpoints**

* [ ] Add CRUD for `Crops` (`POST`, `GET`, `PATCH`, `DELETE`)
* [ ] Add CRUD for `Sensors` (`POST`, `GET`, `PATCH`, `DELETE`)
* [ ] Add `GET /readings` to fetch historical readings by sensor or crop
* [ ] Add filtering parameters (`start_date`, `end_date`, `sensor_id`)
* [ ] Paginate large reading queries for performance
* [ ] Add endpoint to fetch “Overall irrigation score” per plot

**Hardware Integration**

* [ ] Set up POST endpoint for Arduino to send readings
* [ ] Validate readings before saving (check ranges, types)
* [ ] Implement retry mechanism for hardware data if backend fails
* [ ] Simulate sensor POST requests for testing before hardware is connected

**Business Logic / Services**

* [ ] Expand `irrigation.py` to calculate water recommendation based on moisture, light, UV, and crop type
* [ ] Evaluate moisture trends (drop over time) to predict irrigation needs
* [ ] Add thresholds for alerts (low, optimal, oversaturated)
* [ ] Add “critical alert” flag for immediate action

**Real-Time Updates / Notifications**

* [ ] Implement WebSocket or Supabase Realtime for live dashboard updates
* [ ] Trigger alert notifications via SMS (Twilio) or Email (SendGrid)
* [ ] Push notifications to frontend when thresholds are crossed
* [ ] Add “last updated” timestamp per sensor on dashboard

**Logging / Monitoring**

* [ ] Add structured logging (e.g., using Python `logging` module)
* [ ] Log all failed requests, invalid readings, and system errors
* [ ] Monitor database connection health and retries
* [ ] Optionally integrate with monitoring tools (Sentry, Prometheus)

**Optional / Future Enhancements**

* [ ] Add UV sensor data and integrate into irrigation logic
* [ ] Create a dashboard summary endpoint with combined score per quadrant
* [ ] Enable multi-orchard support (if farmer has multiple fields)
* [ ] Implement historical analytics charts (moisture trends, water usage)
* [ ] Add AI/ML recommendations for optimized watering schedule
