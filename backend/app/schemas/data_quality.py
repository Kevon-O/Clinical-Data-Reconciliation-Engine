from datetime import date
from typing import Dict, List, Optional, Union

from pydantic import BaseModel

from app.schemas.common import SeverityLevel

# Defines the demographics model and the request model for the data-quality endpoint.

class Demographics(BaseModel):
    name: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[str] = None


class DataQualityRequest(BaseModel):
    demographics: Demographics
    medications: List[str]
    allergies: List[str]
    conditions: List[str]
    vital_signs: Dict[str, Union[str, int, float]]
    last_updated: date
    recent_labs: Optional[Dict[str, Union[str, int, float]]] = None

# Breaks down the quality score into multiple evaluation factors, next class represents an issue found during data quality evaluating.

class QualityBreakdown(BaseModel):
    completeness: int
    accuracy: int
    timeliness: int
    clinical_plausibility: int


class DataQualityIssue(BaseModel):
    field: str
    issue: str
    severity: SeverityLevel

# Provides explanation for each factor score, defines the response body after validating quality.

class DimensionExplanations(BaseModel):
    completeness: Optional[str] = None
    accuracy: Optional[str] = None
    timeliness: Optional[str] = None
    clinical_plausibility: Optional[str] = None


class DataQualityResponse(BaseModel):
    overall_score: int
    breakdown: QualityBreakdown
    issues_detected: List[DataQualityIssue]
    summary: Optional[str] = None
    dimension_explanations: Optional[DimensionExplanations] = None 