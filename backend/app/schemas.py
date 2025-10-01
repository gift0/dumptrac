from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional


# ----------- Bin Schemas -----------

class BinBase(BaseModel):
    location: str
    latitude: float = Field(..., description="Latitude of the bin (float)")
    longitude: float = Field(..., description="Longitude of the bin (float)")


class BinCreate(BinBase):
    pass


class BinRead(BinBase):
    id: int

    class Config:
        orm_mode = True


# ----------- Report Schemas -----------

class ReportBase(BaseModel):
    status: str


class ReportCreate(ReportBase):
    bin_id: int  # reports must belong to a bin


class ReportRead(ReportBase):
    id: int
    bin_id: int
    created_at: datetime
    cleared_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# ----------- Bin with Reports -----------

class BinWithReports(BinRead):
    reports: List[ReportRead] = []
