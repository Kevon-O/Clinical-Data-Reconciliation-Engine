from typing import Any

from app.cache.memory import build_cache_key, get_cached_response, set_cached_response
from app.llm.client import request_json_response
from app.llm.prompts import (
    build_data_quality_system_prompt,
    build_data_quality_user_prompt,
    build_medication_system_prompt,
    build_medication_user_prompt,
)
from app.models.internal import NormalizedMedicationCase, NormalizedPatientRecord
from app.schemas.common import SeverityLevel
from app.schemas.data_quality import (
    DataQualityIssue,
    DataQualityResponse,
    DimensionExplanations,
)
from app.schemas.medication import MedicationReconciliationResponse


# Returns only valid string actions from a model response.
def _clean_actions(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


# Maps model severity text into the app's shared severity enum.
def _coerce_severity(value: Any) -> SeverityLevel:
    if isinstance(value, str):
        lowered = value.lower().strip()
        if lowered == "high":
            return SeverityLevel.high
        if lowered == "medium":
            return SeverityLevel.medium
    return SeverityLevel.low


# Builds a stable normalized payload used to cache medication enrichment results.
def _build_medication_cache_payload(
    case: NormalizedMedicationCase,
    deterministic_result: MedicationReconciliationResponse,
) -> dict[str, Any]:
    return {
        "patient_context": case.patient_context.model_dump(mode="json"),
        "records": [record.model_dump(mode="json") for record in case.records],
        "deterministic_result": deterministic_result.model_dump(mode="json"),
    }


# Builds a stable normalized payload used to cache data-quality enrichment results.
def _build_data_quality_cache_payload(
    record: NormalizedPatientRecord,
    deterministic_result: DataQualityResponse,
) -> dict[str, Any]:
    return {
        "normalized_record": record.model_dump(mode="json"),
        "deterministic_result": deterministic_result.model_dump(mode="json"),
    }


# Uses the LLM to enrich medication reasoning while preserving deterministic core outputs.
def enrich_medication_response(
    case: NormalizedMedicationCase,
    deterministic_result: MedicationReconciliationResponse,
) -> MedicationReconciliationResponse:
    cache_payload = _build_medication_cache_payload(case, deterministic_result)
    cache_key = build_cache_key("medication_enrichment", cache_payload)

    llm_json = get_cached_response(cache_key)
    if llm_json is None:
        llm_json = request_json_response(
            build_medication_system_prompt(),
            build_medication_user_prompt(case, deterministic_result),
        )
        if llm_json:
            set_cached_response(cache_key, llm_json)

    if not llm_json:
        return deterministic_result

    new_reasoning = deterministic_result.reasoning
    if isinstance(llm_json.get("reasoning"), str) and llm_json["reasoning"].strip():
        new_reasoning = llm_json["reasoning"].strip()

    plausibility_notes = _clean_actions(llm_json.get("plausibility_notes"))
    if plausibility_notes:
        joined_notes = " ".join(plausibility_notes)
        new_reasoning = f"{new_reasoning} {joined_notes}".strip()

    new_actions = deterministic_result.recommended_actions
    llm_actions = _clean_actions(llm_json.get("recommended_actions"))
    if llm_actions:
        new_actions = llm_actions[:3]

    return deterministic_result.model_copy(
        update={
            "reasoning": new_reasoning,
            "recommended_actions": new_actions,
        }
    )


# Uses the LLM to enrich data-quality explanations while preserving deterministic scores.
def enrich_data_quality_response(
    record: NormalizedPatientRecord,
    deterministic_result: DataQualityResponse,
) -> DataQualityResponse:
    cache_payload = _build_data_quality_cache_payload(record, deterministic_result)
    cache_key = build_cache_key("data_quality_enrichment", cache_payload)

    llm_json = get_cached_response(cache_key)
    if llm_json is None:
        llm_json = request_json_response(
            build_data_quality_system_prompt(),
            build_data_quality_user_prompt(record, deterministic_result),
        )
        if llm_json:
            set_cached_response(cache_key, llm_json)

    if not llm_json:
        return deterministic_result

    new_summary = deterministic_result.summary
    if isinstance(llm_json.get("summary"), str) and llm_json["summary"].strip():
        new_summary = llm_json["summary"].strip()

    existing_dimension_explanations = deterministic_result.dimension_explanations
    new_dimension_explanations = existing_dimension_explanations

    raw_dimension_explanations = llm_json.get("dimension_explanations")
    if isinstance(raw_dimension_explanations, dict):
        new_dimension_explanations = DimensionExplanations(
            completeness=raw_dimension_explanations.get("completeness")
            or getattr(existing_dimension_explanations, "completeness", None),
            accuracy=raw_dimension_explanations.get("accuracy")
            or getattr(existing_dimension_explanations, "accuracy", None),
            timeliness=raw_dimension_explanations.get("timeliness")
            or getattr(existing_dimension_explanations, "timeliness", None),
            clinical_plausibility=raw_dimension_explanations.get("clinical_plausibility")
            or getattr(existing_dimension_explanations, "clinical_plausibility", None),
        )

    merged_issues = list(deterministic_result.issues_detected)
    seen_issue_keys = {(issue.field, issue.issue) for issue in merged_issues}

    raw_additional_issues = llm_json.get("additional_issues")
    if isinstance(raw_additional_issues, list):
        for item in raw_additional_issues:
            if not isinstance(item, dict):
                continue

            field = item.get("field")
            issue = item.get("issue")
            severity = _coerce_severity(item.get("severity"))

            if not isinstance(field, str) or not field.strip():
                continue
            if not isinstance(issue, str) or not issue.strip():
                continue

            issue_key = (field.strip(), issue.strip())
            if issue_key in seen_issue_keys:
                continue

            merged_issues.append(
                DataQualityIssue(
                    field=field.strip(),
                    issue=issue.strip(),
                    severity=severity,
                )
            )
            seen_issue_keys.add(issue_key)

    return deterministic_result.model_copy(
        update={
            "summary": new_summary,
            "dimension_explanations": new_dimension_explanations,
            "issues_detected": merged_issues,
        }
    )