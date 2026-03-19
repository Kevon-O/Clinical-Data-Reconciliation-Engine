from datetime import date
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field

from app.schemas.common import SourceReliability


# Stores normalized patient context used during medication reconciliation.
class NormalizedPatientContext(BaseModel):
    age: Optional[int] = None
    conditions: List[str] = Field(default_factory=list)
    recent_labs: Dict[str, float] = Field(default_factory=dict)


# Represents one normalized medication record from any source system.
class NormalizedMedicationRecord(BaseModel):
    source_system: str
    raw_medication_text: str
    event_date: Optional[date] = None
    event_date_type: Optional[str] = None
    source_reliability: Optional[SourceReliability] = None


# Represents the full normalized medication reconciliation case.
class NormalizedMedicationCase(BaseModel):
    patient_context: NormalizedPatientContext = Field(default_factory=NormalizedPatientContext)
    records: List[NormalizedMedicationRecord] = Field(default_factory=list)


# Stores normalized demographic information for data quality validation.
class NormalizedDemographics(BaseModel):
    name: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[str] = None


# Represents one normalized patient record for data quality validation.
class NormalizedPatientRecord(BaseModel):
    demographics: NormalizedDemographics
    medications: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    conditions: List[str] = Field(default_factory=list)
    vital_signs: Dict[str, Union[str, int, float]] = Field(default_factory=dict)
    recent_labs: Dict[str, Union[str, int, float]] = Field(default_factory=dict)
    last_updated: date