from fastapi import APIRouter, Depends

from app.auth.api_key import require_api_key
from app.llm.enrichment import enrich_data_quality_response, enrich_medication_response
from app.schemas.data_quality import DataQualityRequest, DataQualityResponse
from app.schemas.medication import (
    MedicationReconciliationRequest,
    MedicationReconciliationResponse,
)
from app.services.adapters import (
    to_normalized_medication_case,
    to_normalized_patient_record,
)
from app.services.data_quality import validate_patient_record
from app.services.medication_reconciliation import reconcile_medication_case


# Creates a router that groups the API endpoints for this app.
router = APIRouter()


# Defines the medication reconciliation endpoint and protects it with an API key.
# The deterministic result is produced first, then the LLM enrichment layer is attempted.
@router.post(
    "/api/reconcile/medication",
    response_model=MedicationReconciliationResponse,
    dependencies=[Depends(require_api_key)],
)
def reconcile_medication(payload: MedicationReconciliationRequest):
    normalized_case = to_normalized_medication_case(payload)
    deterministic_result = reconcile_medication_case(normalized_case)
    return enrich_medication_response(normalized_case, deterministic_result)


# Defines the data quality validation endpoint and protects it with an API key.
# The deterministic result is produced first, then the LLM enrichment layer is attempted.
@router.post(
    "/api/validate/data-quality",
    response_model=DataQualityResponse,
    dependencies=[Depends(require_api_key)],
)
def validate_data_quality(payload: DataQualityRequest):
    normalized_record = to_normalized_patient_record(payload)
    deterministic_result = validate_patient_record(normalized_record)
    return enrich_data_quality_response(normalized_record, deterministic_result)