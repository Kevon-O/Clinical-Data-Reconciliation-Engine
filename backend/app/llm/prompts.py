import json

from app.models.internal import NormalizedMedicationCase, NormalizedPatientRecord
from app.schemas.data_quality import DataQualityResponse
from app.schemas.medication import MedicationReconciliationResponse


# Builds the system prompt for medication reconciliation enrichment.
def build_medication_system_prompt() -> str:
    return (
        "You are assisting a clinician-facing medication reconciliation workflow. "
        "You must not change the deterministic winner, confidence score, or safety status. "
        "Your job is to improve the explanation quality and suggest practical next steps. "
        "Use the provided patient context and source disagreement. "
        "Return JSON with keys: reasoning, recommended_actions, plausibility_notes."
    )


# Builds the user prompt for medication reconciliation enrichment.
def build_medication_user_prompt(
    case: NormalizedMedicationCase,
    deterministic_result: MedicationReconciliationResponse,
) -> str:
    payload = {
        "patient_context": case.patient_context.model_dump(mode="json"),
        "records": [record.model_dump(mode="json") for record in case.records],
        "deterministic_result": deterministic_result.model_dump(mode="json"),
    }
    return json.dumps(payload, indent=2)


# Builds the system prompt for data-quality enrichment.
def build_data_quality_system_prompt() -> str:
    return (
        "You are assisting a clinician-facing EHR data-quality review workflow. "
        "Do not change the deterministic overall score or score breakdown. "
        "Your job is to provide clearer human-readable explanations and optionally flag "
        "additional plausible issues that were not already surfaced. "
        "Return JSON with keys: summary, dimension_explanations, additional_issues. "
        "dimension_explanations must contain completeness, accuracy, timeliness, and clinical_plausibility. "
        "additional_issues must be a list of objects with field, issue, severity."
    )


# Builds the user prompt for data-quality enrichment.
def build_data_quality_user_prompt(
    record: NormalizedPatientRecord,
    deterministic_result: DataQualityResponse,
) -> str:
    payload = {
        "normalized_record": record.model_dump(mode="json"),
        "deterministic_result": deterministic_result.model_dump(mode="json"),
    }
    return json.dumps(payload, indent=2)