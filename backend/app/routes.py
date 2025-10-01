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
    if bin_in.latitude is None or bin_in.longitude is None:
        raise HTTPException(status_code=400, detail="Latitude and longitude are required")

    existing = db.query(models.Bin).filter(models.Bin.location == bin_in.location).first()
    if existing:
        return existing

    bin_obj = models.Bin(
        location=bin_in.location,
        latitude=str(bin_in.latitude),
        longitude=str(bin_in.longitude)
    )
    db.add(bin_obj)
    db.commit()
    db.refresh(bin_obj)
    return bin_obj


@router.get("/bins", response_model=List[schemas.BinRead])
def list_bins(db: Session = Depends(get_db)):
    """List all bins, newest first."""
    return db.query(models.Bin).order_by(models.Bin.id.desc()).all()


# ----------------- Reports -----------------

@router.get("/reports", response_model=List[schemas.ReportRead])
def list_reports(db: Session = Depends(get_db)):
    """List all reports, newest first."""
    return db.query(models.Report).order_by(models.Report.created_at.desc()).all()


@router.post("/reports", response_model=schemas.ReportRead)
def create_report(report_in: schemas.ReportCreate, db: Session = Depends(get_db)):
    """
    Create a report for an existing bin.
    """
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
        f"NOTIFY: Bin {bin_obj.id} at '{bin_obj.location}' reported as "
        f"{report.status} [lat={bin_obj.latitude}, lng={bin_obj.longitude}]"
    )

    return report


@router.put("/reports/{report_id}/clear", response_model=schemas.ReportRead)
def clear_report(report_id: int, db: Session = Depends(get_db)):
    """
    Mark a report as cleared and set cleared_at timestamp.
    """
    db_report = db.query(models.Report).filter(models.Report.id == report_id).first()
    if not db_report:
        raise HTTPException(status_code=404, detail="Report not found")

    db_report.status = "done"
    db_report.cleared_at = datetime.utcnow()
    db.commit()
    db.refresh(db_report)
    return db_report
