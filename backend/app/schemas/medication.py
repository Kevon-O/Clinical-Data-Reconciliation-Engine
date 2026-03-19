from datetime import date
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.schemas.common import ClinicalSafetyCheck, SourceReliability

# Defines the patient context model, medication source model and the request model for reconciliation endpoint.

class PatientContext(BaseModel):
    age: Optional[int] = None
    conditions: Optional[List[str]] = None
    recent_labs: Optional[Dict[str, float]] = None


class MedicationSourceRecord(BaseModel):
    system: str
    medication: str
    last_updated: Optional[date] = None
    last_filled: Optional[date] = None
    source_reliability: Optional[SourceReliability] = None

class MedicationReconciliationRequest(BaseModel):
    patient_context: Optional[PatientContext] = None
    sources: List[MedicationSourceRecord] = Field(..., min_length=2)

# Defines the structured decision facotr breakdown for confidence score, and the medication response model after reconciliation.


class DecisionFactors(BaseModel):
    source_agreement: Optional[float] = None
    recency: Optional[float] = None
    source_reliability: Optional[float] = None
    clinical_context_match: Optional[float] = None


class MedicationReconciliationResponse(BaseModel):
    reconciled_medication: str
    confidence_score: float
    reasoning: str
    recommended_actions: List[str]
    clinical_safety_check: ClinicalSafetyCheck
    decision_factors: Optional[DecisionFactors] = None