from app.models.internal import (
    NormalizedDemographics,
    NormalizedMedicationCase,
    NormalizedMedicationRecord,
    NormalizedPatientContext,
    NormalizedPatientRecord,
)
from app.schemas.data_quality import DataQualityRequest
from app.schemas.medication import MedicationReconciliationRequest


# Converts the public medication request into the app's normalized internal format.
def to_normalized_medication_case(
    payload: MedicationReconciliationRequest,
) -> NormalizedMedicationCase:
    if payload.patient_context is None:
        patient_context = NormalizedPatientContext()
    else:
        patient_context = NormalizedPatientContext(
            age=payload.patient_context.age,
            conditions=list(payload.patient_context.conditions or []),
            recent_labs=dict(payload.patient_context.recent_labs or {}),
        )

    records = []

    for source in payload.sources:
        event_date = source.last_updated or source.last_filled

        if source.last_updated is not None:
            event_date_type = "last_updated"
        elif source.last_filled is not None:
            event_date_type = "last_filled"
        else:
            event_date_type = None

        records.append(
            NormalizedMedicationRecord(
                source_system=source.system,
                raw_medication_text=source.medication,
                event_date=event_date,
                event_date_type=event_date_type,
                source_reliability=source.source_reliability,
            )
        )

    return NormalizedMedicationCase(
        patient_context=patient_context,
        records=records,
    )


# Converts the public data-quality request into the app's normalized patient record format.
def to_normalized_patient_record(payload: DataQualityRequest) -> NormalizedPatientRecord:
    demographics = NormalizedDemographics(
        name=payload.demographics.name,
        dob=payload.demographics.dob,
        gender=payload.demographics.gender,
    )

    return NormalizedPatientRecord(
        demographics=demographics,
        medications=list(payload.medications),
        allergies=list(payload.allergies),
        conditions=list(payload.conditions),
        vital_signs=dict(payload.vital_signs),
        recent_labs=dict(payload.recent_labs or {}),
        last_updated=payload.last_updated,
    )