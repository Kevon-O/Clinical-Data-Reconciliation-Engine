from datetime import date

from app.models.internal import NormalizedDemographics, NormalizedPatientRecord
from app.services.data_quality import validate_patient_record


# Verifies that an implausible blood pressure is detected as a high-severity issue.
def test_data_quality_detects_implausible_blood_pressure():
    record = NormalizedPatientRecord(
        demographics=NormalizedDemographics(
            name="John Doe",
            dob=date(1955, 3, 15),
            gender="M",
        ),
        medications=["Metformin 500mg", "Lisinopril 10mg"],
        allergies=[],
        conditions=["Type 2 Diabetes"],
        vital_signs={"blood_pressure": "340/180", "heart_rate": 72},
        recent_labs={},
        last_updated=date(2024, 6, 15),
    )

    result = validate_patient_record(record)

    assert result.overall_score < 100
    assert any(
        issue.field == "vital_signs.blood_pressure" and issue.severity.value == "high"
        for issue in result.issues_detected
    )


# Verifies that an empty allergies list is treated as an issue.
def test_data_quality_detects_missing_allergies():
    record = NormalizedPatientRecord(
        demographics=NormalizedDemographics(
            name="John Doe",
            dob=date(1955, 3, 15),
            gender="M",
        ),
        medications=["Metformin 500mg"],
        allergies=[],
        conditions=["Type 2 Diabetes"],
        vital_signs={"blood_pressure": "120/80", "heart_rate": 72},
        recent_labs={},
        last_updated=date.today(),
    )

    result = validate_patient_record(record)

    assert any(issue.field == "allergies" for issue in result.issues_detected)


# Verifies that stale records lose timeliness score.
def test_data_quality_detects_stale_record():
    record = NormalizedPatientRecord(
        demographics=NormalizedDemographics(
            name="John Doe",
            dob=date(1955, 3, 15),
            gender="M",
        ),
        medications=["Metformin 500mg"],
        allergies=["Penicillin"],
        conditions=["Type 2 Diabetes"],
        vital_signs={"blood_pressure": "120/80", "heart_rate": 72},
        recent_labs={},
        last_updated=date(2023, 1, 1),
    )

    result = validate_patient_record(record)

    assert result.breakdown.timeliness < 100
    assert any(issue.field == "last_updated" for issue in result.issues_detected)