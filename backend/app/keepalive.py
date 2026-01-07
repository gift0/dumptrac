from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import SessionLocal
from app import models

DEFAULT_LOCATION = "System Auto Check Location"
DEFAULT_LAT = "6.5244"
DEFAULT_LNG = "3.3792"

def keep_db_alive():
    db: Session = SessionLocal()
    try:
        # Ensure default bin exists
        bin_obj = db.query(models.Bin).filter(
            models.Bin.location == DEFAULT_LOCATION
        ).first()

        if not bin_obj:
            bin_obj = models.Bin(
                location=DEFAULT_LOCATION,
                latitude=DEFAULT_LAT,
                longitude=DEFAULT_LNG,
            )
            db.add(bin_obj)
            db.commit()
            db.refresh(bin_obj)

        # Insert a report (this creates real activity)
        report = models.Report(
            bin_id=bin_obj.id,
            status="auto-check",
            created_at=datetime.utcnow(),
        )
        db.add(report)
        db.commit()

        print("🟢 Keepalive job executed successfully")

    except Exception as e:
        print("🔴 Keepalive job failed:", e)

    finally:
        db.close()


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        keep_db_alive,
        trigger="interval",
        weeks=2,
        id="db_keepalive_job",
        replace_existing=True,
    )
    scheduler.start()
