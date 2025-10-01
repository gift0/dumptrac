from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from .database import get_db
from . import models, schemas

router = APIRouter()

# ----------------- Reports -----------------

@router.get("/reports", response_model=List[schemas.ReportRead])
def list_reports(db: Session = Depends(get_db)):
    try:
        reports = db.query(models.Report).order_by(models.Report.created_at.desc()).all()
        return reports
    except Exception as e:
        print("Error fetching reports:", e)
        return []  # Safe fallback so frontend doesn't break

@router.post("/reports", response_model=schemas.ReportRead)
def create_report(report_in: schemas.ReportCreate, db: Session = Depends(get_db)):
    try:
        report = models.Report(
            bin_id=report_in.bin_id,
            status=report_in.status
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        print(f"NOTIFY: Report {report.id} created with status {report.status}")
        return report
    except Exception as e:
        print("Error creating report:", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.put("/reports/{report_id}/clear", response_model=schemas.ReportRead)
def clear_report(report_id: int, db: Session = Depends(get_db)):
    try:
        db_report = db.query(models.Report).filter(models.Report.id == report_id).first()
        if not db_report:
            raise HTTPException(status_code=404, detail="Report not found")
        db_report.status = "done"
        db_report.cleared_at = datetime.utcnow()
        db.commit()
        db.refresh(db_report)
        return db_report
    except Exception as e:
        print(f"Error clearing report {report_id}:", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
