from datetime import date

from app.models.internal import (
    NormalizedMedicationCase,
    NormalizedMedicationRecord,
    NormalizedPatientContext,
)
from app.schemas.common import ClinicalSafetyCheck, SourceReliability
from app.services.medication_reconciliation import reconcile_medication_case


# Verifies that the lower metformin dose wins when kidney function is reduced.
def test_reconcile_medication_prefers_lower_metformin_dose_with_low_egfr():
    case = NormalizedMedicationCase(
        patient_context=NormalizedPatientContext(
            age=67,
            conditions=["Type 2 Diabetes", "Hypertension"],
            recent_labs={"eGFR": 45},
        ),
        records=[
            NormalizedMedicationRecord(
                source_system="Hospital EHR",
                raw_medication_text="Metformin 1000mg twice daily",
                event_date=date(2024, 10, 15),
                event_date_type="last_updated",
                source_reliability=SourceReliability.high,
            ),
            NormalizedMedicationRecord(
                source_system="Primary Care",
                raw_medication_text="Metformin 500mg twice daily",
                event_date=date(2025, 1, 20),
                event_date_type="last_updated",
                source_reliability=SourceReliability.high,
            ),
            NormalizedMedicationRecord(
                source_system="Pharmacy",
                raw_medication_text="Metformin 1000mg daily",
                event_date=date(2025, 1, 25),
                event_date_type="last_filled",
                source_reliability=SourceReliability.medium,
            ),
        ],
    )

    result = reconcile_medication_case(case)

    assert result.reconciled_medication == "Metformin 500mg twice daily"
    assert result.clinical_safety_check == ClinicalSafetyCheck.PASSED
    assert result.confidence_score > 0.0


# Verifies that the service still returns actions when sources disagree.
def test_reconcile_medication_returns_actions_when_sources_disagree():
    case = NormalizedMedicationCase(
        patient_context=NormalizedPatientContext(
            recent_labs={"eGFR": 45},
        ),
        records=[
            NormalizedMedicationRecord(
                source_system="Primary Care",
                raw_medication_text="Metformin 1000mg twice daily",
                event_date=date(2025, 1, 20),
                event_date_type="last_updated",
                source_reliability=SourceReliability.high,
            ),
            NormalizedMedicationRecord(
                source_system="Hospital EHR",
                raw_medication_text="Metformin 500mg daily",
                event_date=date(2024, 10, 15),
                event_date_type="last_updated",
                source_reliability=SourceReliability.high,
            ),
        ],
    )

    result = reconcile_medication_case(case)

    assert result.recommended_actions
    assert result.confidence_score > 0.0