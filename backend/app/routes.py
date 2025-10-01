from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from .database import get_db
from . import models, schemas

router = APIRouter()

# ----------------- Bins -----------------

@router.post("/bins", response_model=schemas.BinRead)
def create_bin(bin_in: schemas.BinCreate, db: Session = Depends(get_db)):
    """
    Ensure a bin exists; create new if missing.
    Latitude and longitude are required.
    """
    try:
        print("📩 Incoming bin payload:", bin_in.dict())  # Debug log

        if not bin_in.latitude or not bin_in.longitude:
            raise HTTPException(status_code=400, detail="Latitude and longitude are required")

        # Check if bin already exists by location
        existing = db.query(models.Bin).filter(models.Bin.location == bin_in.location).first()
        if existing:
            print(f"ℹ️ Bin already exists: ID={existing.id}, Location={existing.location}")
            return existing

        # Create new bin
        bin_obj = models.Bin(
            location=bin_in.location,
            latitude=str(bin_in.latitude),
            longitude=str(bin_in.longitude)
        )
        db.add(bin_obj)
        db.commit()
        db.refresh(bin_obj)

        print(f"✅ Created new bin: ID={bin_obj.id}, Location={bin_obj.location}")
        return bin_obj

    except Exception as e:
        print("❌ Error in /bins:", e)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/bins", response_model=List[schemas.BinRead])
def list_bins(db: Session = Depends(get_db)):
    """List all bins, newest first."""
    try:
        bins = db.query(models.Bin).order_by(models.Bin.id.desc()).all()
        print(f"📦 Retrieved {len(bins)} bins")
        return bins
    except Exception as e:
        print("❌ Error in /bins GET:", e)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ----------------- Reports -----------------

@router.get("/reports", response_model=List[schemas.ReportRead])
def list_reports(db: Session = Depends(get_db)):
    """List all reports, newest first."""
    try:
        reports = db.query(models.Report).order_by(models.Report.created_at.desc()).all()
        print(f"📑 Retrieved {len(reports)} reports")
        return reports
    except Exception as e:
        print("❌ Error in /reports GET:", e)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/reports", response_model=schemas.ReportRead)
def create_report(report_in: schemas.ReportCreate, db: Session = Depends(get_db)):
    """
    Create a report for an existing bin.
    """
    try:
        bin_obj = db.query(models.Bin).filter(models.Bin.id == report_in.bin_id).first()
        if not bin_obj:
            raise HTTPException(status_code=404, detail="Bin not found")

        report = models.Report(
            bin_id=report_in.bin_id,
            status=report_in.status
        )
        db.add(report)
        db.commit()
        db.refresh(report)

        print(
            f"📢 NOTIFY: Bin {bin_obj.id} at '{bin_obj.location}' "
            f"reported as {report.status} "
            f"[lat={bin_obj.latitude}, lng={bin_obj.longitude}]"
        )

        return report
    except Exception as e:
        print("❌ Error in /reports POST:", e)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/reports/{report_id}/clear", response_model=schemas.ReportRead)
def clear_report(report_id: int, db: Session = Depends(get_db)):
    """
    Mark a report as cleared and set cleared_at timestamp.
    """
    try:
        db_report = db.query(models.Report).filter(models.Report.id == report_id).first()
        if not db_report:
            raise HTTPException(status_code=404, detail="Report not found")

        db_report.status = "done"
        db_report.cleared_at = datetime.utcnow()
        db.commit()
        db.refresh(db_report)

        print(f"✅ Cleared report ID={db_report.id}")
        return db_report
    except Exception as e:
        print("❌ Error in /reports CLEAR:", e)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
