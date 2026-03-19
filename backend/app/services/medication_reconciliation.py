import re
from datetime import date
from typing import Optional

from app.models.internal import NormalizedMedicationCase, NormalizedMedicationRecord
from app.schemas.common import ClinicalSafetyCheck, SourceReliability
from app.schemas.medication import DecisionFactors, MedicationReconciliationResponse


# Maps source reliability levels to simple number weights for scoring.
RELIABILITY_SCORES = {
    SourceReliability.low: 0.4,
    SourceReliability.medium: 0.7,
    SourceReliability.high: 1.0,
    None: 0.7,
}


# Maps common frequency phrases to a standard daily multiplier.
FREQUENCY_MULTIPLIERS = {
    "once daily": 1,
    "daily": 1,
    "twice daily": 2,
    "bid": 2,
    "three times daily": 3,
    "tid": 3,
}


# Extracts simple comparable medication facts from raw medication text.
def parse_medication_text(text: str) -> dict:
    cleaned_text = " ".join(text.strip().split())
    lower_text = cleaned_text.lower()

    dose_match = re.search(r"(\d+(?:\.\d+)?)\s*mg", lower_text)
    dose_mg = float(dose_match.group(1)) if dose_match else None

    name = lower_text
    if dose_match:
        name = lower_text[: dose_match.start()].strip()

    frequency = None
    for phrase in ["three times daily", "twice daily", "once daily", "daily", "bid", "tid"]:
        if phrase in lower_text:
            frequency = phrase
            break

    return {
        "original_text": cleaned_text,
        "name": name,
        "dose_mg": dose_mg,
        "frequency": frequency,
    }


# Converts parsed medication information into an estimated total daily dose.
def estimate_total_daily_dose(parsed_medication: dict) -> Optional[float]:
    dose_mg = parsed_medication.get("dose_mg")
    frequency = parsed_medication.get("frequency")

    if dose_mg is None or frequency is None:
        return None

    multiplier = FREQUENCY_MULTIPLIERS.get(frequency)
    if multiplier is None:
        return None

    return dose_mg * multiplier


# Builds a comparable signature so similar medication records can be grouped together.
def build_medication_signature(record: NormalizedMedicationRecord) -> str:
    parsed = parse_medication_text(record.raw_medication_text)

    name = parsed.get("name") or ""
    dose = parsed.get("dose_mg")
    frequency = parsed.get("frequency") or ""

    dose_text = f"{dose}mg" if dose is not None else "unknown-dose"
    frequency_text = frequency if frequency else "unknown-frequency"

    return f"{name}|{dose_text}|{frequency_text}"


# Scores how recent a record is compared with the newest dated record.
def calculate_recency_score(
    record: NormalizedMedicationRecord,
    latest_date: Optional[date],
) -> float:
    if record.event_date is None or latest_date is None:
        return 0.5

    days_old = (latest_date - record.event_date).days

    if days_old <= 7:
        base_score = 1.0
    elif days_old <= 30:
        base_score = 0.9
    elif days_old <= 90:
        base_score = 0.75
    elif days_old <= 180:
        base_score = 0.6
    else:
        base_score = 0.4

    # A clinical update is slightly stronger than a pharmacy fill when dates are similar.
    if record.event_date_type == "last_updated":
        return base_score
    if record.event_date_type == "last_filled":
        return max(base_score - 0.05, 0.0)

    return base_score


# Scores how well a record fits the available patient context.
def calculate_clinical_context_score(
    record: NormalizedMedicationRecord,
    case: NormalizedMedicationCase,
) -> float:
    parsed = parse_medication_text(record.raw_medication_text)
    medication_name = parsed.get("name", "")
    total_daily_dose = estimate_total_daily_dose(parsed)

    # Neutral if no usable patient context exists.
    if not case.patient_context.recent_labs:
        return 0.7

    egfr = case.patient_context.recent_labs.get("eGFR")

    # Keep rule support intentionally narrow and explicit.
    if "metformin" in medication_name and egfr is not None and total_daily_dose is not None:
        if egfr <= 45:
            if total_daily_dose <= 1000:
                return 1.0
            if total_daily_dose <= 2000:
                return 0.65
            return 0.3

        return 0.8

    # Neutral if context exists but we do not have a supported rule for it.
    return 0.7


# Calculates how much source agreement supports a given record.
def calculate_agreement_score(
    record: NormalizedMedicationRecord,
    case: NormalizedMedicationCase,
) -> float:
    signatures = [build_medication_signature(item) for item in case.records]
    current_signature = build_medication_signature(record)

    return signatures.count(current_signature) / len(signatures)


# Builds the structured decision factors used in the response.
def build_decision_factors(
    winning_record: NormalizedMedicationRecord,
    case: NormalizedMedicationCase,
) -> DecisionFactors:
    dated_records = [record.event_date for record in case.records if record.event_date is not None]
    latest_date = max(dated_records) if dated_records else None

    return DecisionFactors(
        source_agreement=round(calculate_agreement_score(winning_record, case), 2),
        recency=round(calculate_recency_score(winning_record, latest_date), 2),
        source_reliability=round(RELIABILITY_SCORES.get(winning_record.source_reliability, 0.7), 2),
        clinical_context_match=round(calculate_clinical_context_score(winning_record, case), 2),
    )


# Combines the decision factors into one calibrated confidence score.
def calculate_confidence_score(decision_factors: DecisionFactors) -> float:
    weighted_score = (
        (decision_factors.source_agreement or 0.0) * 0.25
        + (decision_factors.recency or 0.0) * 0.30
        + (decision_factors.source_reliability or 0.0) * 0.20
        + (decision_factors.clinical_context_match or 0.0) * 0.25
    )

    return round(min(max(weighted_score, 0.0), 0.98), 2)


# Builds a deterministic explanation for why the selected record won.
def build_reasoning(
    winning_record: NormalizedMedicationRecord,
    case: NormalizedMedicationCase,
    decision_factors: DecisionFactors,
) -> str:
    parts = []

    if winning_record.event_date_type == "last_updated":
        parts.append(
            f"{winning_record.source_system} provides the strongest recent clinical medication record."
        )
    elif winning_record.event_date_type == "last_filled":
        parts.append(
            f"{winning_record.source_system} provides the strongest recent fill-based medication record."
        )
    else:
        parts.append(
            f"{winning_record.source_system} provides the strongest available medication record."
        )

    if (decision_factors.source_agreement or 0.0) < 0.5:
        parts.append(
            "Source systems do not fully agree, so recency and reliability had a larger effect on the decision."
        )
    else:
        parts.append(
            "Multiple records support the same medication details, which increases confidence in the result."
        )

    if (decision_factors.clinical_context_match or 0.0) >= 0.9:
        parts.append(
            "The selected record is also the best fit for the available patient context."
        )

    return " ".join(parts)


# Suggests practical follow-up actions after reconciliation.
def build_recommended_actions(
    winning_record: NormalizedMedicationRecord,
    case: NormalizedMedicationCase,
) -> list[str]:
    actions = []

    for record in case.records:
        if record.source_system != winning_record.source_system:
            actions.append(
                f"Review and update {record.source_system} if it does not match the selected medication."
            )

    if calculate_agreement_score(winning_record, case) < 0.5:
        actions.append("Confirm the medication list directly with the patient because source disagreement remains.")
    else:
        actions.append("Confirm the final reconciled medication list during the next clinical review.")

    return actions[:3]


# Applies simple deterministic safety rules to the selected record.
def determine_clinical_safety_check(
    winning_record: NormalizedMedicationRecord,
    case: NormalizedMedicationCase,
) -> ClinicalSafetyCheck:
    parsed = parse_medication_text(winning_record.raw_medication_text)
    medication_name = parsed.get("name", "")
    total_daily_dose = estimate_total_daily_dose(parsed)

    egfr = case.patient_context.recent_labs.get("eGFR")

    if "metformin" in medication_name and egfr is not None and total_daily_dose is not None:
        if egfr <= 45 and total_daily_dose > 2000:
            return ClinicalSafetyCheck.FAILED
        if egfr <= 45 and total_daily_dose > 1000:
            return ClinicalSafetyCheck.REVIEW

    return ClinicalSafetyCheck.PASSED


# Cleans the final medication string for output.
def build_reconciled_medication_text(record: NormalizedMedicationRecord) -> str:
    return " ".join(record.raw_medication_text.strip().split())


# Chooses the highest-scoring medication record and returns the full response object.
def reconcile_medication_case(case: NormalizedMedicationCase) -> MedicationReconciliationResponse:
    dated_records = [record.event_date for record in case.records if record.event_date is not None]
    latest_date = max(dated_records) if dated_records else None

    best_record = None
    best_score = -1.0

    for record in case.records:
        agreement_score = calculate_agreement_score(record, case)
        recency_score = calculate_recency_score(record, latest_date)
        reliability_score = RELIABILITY_SCORES.get(record.source_reliability, 0.7)
        clinical_context_score = calculate_clinical_context_score(record, case)

        total_score = (
            agreement_score * 0.25
            + recency_score * 0.30
            + reliability_score * 0.20
            + clinical_context_score * 0.25
        )

        if total_score > best_score:
            best_score = total_score
            best_record = record

    decision_factors = build_decision_factors(best_record, case)
    confidence_score = calculate_confidence_score(decision_factors)
    reasoning = build_reasoning(best_record, case, decision_factors)
    recommended_actions = build_recommended_actions(best_record, case)
    safety_check = determine_clinical_safety_check(best_record, case)

    return MedicationReconciliationResponse(
        reconciled_medication=build_reconciled_medication_text(best_record),
        confidence_score=confidence_score,
        reasoning=reasoning,
        recommended_actions=recommended_actions,
        clinical_safety_check=safety_check,
        decision_factors=decision_factors,
    )