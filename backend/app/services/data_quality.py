from datetime import date

from app.models.internal import NormalizedPatientRecord
from app.schemas.common import SeverityLevel
from app.schemas.data_quality import (
    DataQualityIssue,
    DataQualityResponse,
    DimensionExplanations,
    QualityBreakdown,
)


# Adds one structured issue to the running issue list.
def add_issue(
    issues: list[DataQualityIssue],
    field: str,
    issue: str,
    severity: SeverityLevel,
) -> None:
    issues.append(
        DataQualityIssue(
            field=field,
            issue=issue,
            severity=severity,
        )
    )


# Scores whether expected sections are present and populated.
def calculate_completeness_score(
    record: NormalizedPatientRecord,
    issues: list[DataQualityIssue],
) -> int:
    score = 100

    if not record.demographics.name:
        score -= 10
        add_issue(issues, "demographics.name", "Patient name is missing.", SeverityLevel.low)

    if not record.demographics.dob:
        score -= 10
        add_issue(issues, "demographics.dob", "Date of birth is missing.", SeverityLevel.low)

    if not record.demographics.gender:
        score -= 5
        add_issue(issues, "demographics.gender", "Gender is missing.", SeverityLevel.low)

    if not record.medications:
        score -= 20
        add_issue(issues, "medications", "No medications documented.", SeverityLevel.medium)

    if not record.allergies:
        score -= 15
        add_issue(
            issues,
            "allergies",
            "No allergies documented - likely incomplete.",
            SeverityLevel.medium,
        )

    if not record.conditions:
        score -= 10
        add_issue(issues, "conditions", "No conditions documented.", SeverityLevel.medium)

    if not record.vital_signs:
        score -= 15
        add_issue(issues, "vital_signs", "No vital signs documented.", SeverityLevel.medium)

    return max(score, 0)


# Scores whether values are correctly formed and internally reasonable.
def calculate_accuracy_score(
    record: NormalizedPatientRecord,
    issues: list[DataQualityIssue],
) -> int:
    score = 100

    blood_pressure = record.vital_signs.get("blood_pressure")
    if isinstance(blood_pressure, str):
        if "/" not in blood_pressure:
            score -= 20
            add_issue(
                issues,
                "vital_signs.blood_pressure",
                "Blood pressure format is invalid.",
                SeverityLevel.medium,
            )
        else:
            try:
                systolic_str, diastolic_str = blood_pressure.split("/")
                systolic = int(systolic_str)
                diastolic = int(diastolic_str)

                if systolic <= 0 or diastolic <= 0:
                    score -= 25
                    add_issue(
                        issues,
                        "vital_signs.blood_pressure",
                        "Blood pressure cannot be zero or negative.",
                        SeverityLevel.high,
                    )
                elif systolic < diastolic:
                    score -= 20
                    add_issue(
                        issues,
                        "vital_signs.blood_pressure",
                        "Systolic pressure is lower than diastolic pressure.",
                        SeverityLevel.high,
                    )
            except ValueError:
                score -= 20
                add_issue(
                    issues,
                    "vital_signs.blood_pressure",
                    "Blood pressure contains non-numeric values.",
                    SeverityLevel.medium,
                )

    heart_rate = record.vital_signs.get("heart_rate")
    if isinstance(heart_rate, (int, float)):
        if heart_rate <= 0:
            score -= 20
            add_issue(
                issues,
                "vital_signs.heart_rate",
                "Heart rate must be greater than zero.",
                SeverityLevel.high,
            )

    return max(score, 0)


# Scores how recent the record is based on its last-updated date.
def calculate_timeliness_score(
    record: NormalizedPatientRecord,
    issues: list[DataQualityIssue],
) -> int:
    days_old = (date.today() - record.last_updated).days

    if days_old <= 30:
        return 100
    if days_old <= 90:
        return 85
    if days_old <= 180:
        return 70
    if days_old <= 365:
        add_issue(
            issues,
            "last_updated",
            "Data is more than 6 months old.",
            SeverityLevel.medium,
        )
        return 55

    add_issue(
        issues,
        "last_updated",
        "Data is 1+ year old and may be stale.",
        SeverityLevel.medium,
    )
    return 35


# Scores whether values fall within believable physiologic ranges.
def calculate_clinical_plausibility_score(
    record: NormalizedPatientRecord,
    issues: list[DataQualityIssue],
) -> int:
    score = 100

    blood_pressure = record.vital_signs.get("blood_pressure")
    if isinstance(blood_pressure, str) and "/" in blood_pressure:
        try:
            systolic_str, diastolic_str = blood_pressure.split("/")
            systolic = int(systolic_str)
            diastolic = int(diastolic_str)

            if systolic > 300 or diastolic > 200:
                score -= 50
                add_issue(
                    issues,
                    "vital_signs.blood_pressure",
                    f"Blood pressure {blood_pressure} is physiologically implausible.",
                    SeverityLevel.high,
                )
            elif systolic < 60 or diastolic < 30:
                score -= 35
                add_issue(
                    issues,
                    "vital_signs.blood_pressure",
                    f"Blood pressure {blood_pressure} is outside a plausible physiologic range.",
                    SeverityLevel.high,
                )
        except ValueError:
            pass

    heart_rate = record.vital_signs.get("heart_rate")
    if isinstance(heart_rate, (int, float)):
        if heart_rate > 250 or heart_rate < 20:
            score -= 40
            add_issue(
                issues,
                "vital_signs.heart_rate",
                f"Heart rate {heart_rate} is outside a plausible physiologic range.",
                SeverityLevel.high,
            )

    return max(score, 0)


# Builds short explanations for each dimension score.
def build_dimension_explanations(
    completeness: int,
    accuracy: int,
    timeliness: int,
    clinical_plausibility: int,
) -> DimensionExplanations:
    return DimensionExplanations(
        completeness=(
            f"Completeness reflects whether expected record sections were populated. "
            f"Current score: {completeness}."
        ),
        accuracy=(
            f"Accuracy reflects whether values are correctly formed and internally consistent. "
            f"Current score: {accuracy}."
        ),
        timeliness=(
            f"Timeliness reflects how recently the record was updated. "
            f"Current score: {timeliness}."
        ),
        clinical_plausibility=(
            f"Clinical plausibility reflects whether values fall within believable physiologic ranges. "
            f"Current score: {clinical_plausibility}."
        ),
    )


# Builds the final structured response for a normalized patient record.
def validate_patient_record(record: NormalizedPatientRecord) -> DataQualityResponse:
    issues: list[DataQualityIssue] = []

    completeness = calculate_completeness_score(record, issues)
    accuracy = calculate_accuracy_score(record, issues)
    timeliness = calculate_timeliness_score(record, issues)
    clinical_plausibility = calculate_clinical_plausibility_score(record, issues)

    overall_score = round(
        (completeness + accuracy + timeliness + clinical_plausibility) / 4
    )

    breakdown = QualityBreakdown(
        completeness=completeness,
        accuracy=accuracy,
        timeliness=timeliness,
        clinical_plausibility=clinical_plausibility,
    )

    dimension_explanations = build_dimension_explanations(
        completeness,
        accuracy,
        timeliness,
        clinical_plausibility,
    )

    if overall_score >= 85:
        summary = "The record is generally strong with only minor quality concerns."
    elif overall_score >= 65:
        summary = "The record is usable but has several quality issues that should be reviewed."
    else:
        summary = "The record has significant quality concerns that may affect clinical trust."

    return DataQualityResponse(
        overall_score=overall_score,
        breakdown=breakdown,
        issues_detected=issues,
        summary=summary,
        dimension_explanations=dimension_explanations,
    )