from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class SourceReliability(str, Enum):
    low = "low"
    medium = "medium"   
    high = "high"


class ClinicalSafetyCheck(str, Enum):
    PASSED = "PASSED"
    REVIEW = "REVIEW"
    FAILED = "FAILED"


class SeverityLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class ErrorDetail(BaseModel):
    field: str
    issue: str


class ErrorBody(BaseModel):
    code: str
    message: str
    details: Optional[List[ErrorDetail]] = None


class ErrorResponse(BaseModel):
    error: ErrorBody