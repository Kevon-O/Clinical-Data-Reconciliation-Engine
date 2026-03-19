export type SourceReliability = "low" | "medium" | "high";
export type ClinicalSafetyCheck = "PASSED" | "REVIEW" | "FAILED";
export type SeverityLevel = "low" | "medium" | "high";

export interface MedicationReconciliationRequest {
  patient_context?: {
    age?: number;
    conditions?: string[];
    recent_labs?: Record<string, number>;
  };
  sources: Array<{
    system: string;
    medication: string;
    last_updated?: string;
    last_filled?: string;
    source_reliability?: SourceReliability;
  }>;
}

export interface MedicationReconciliationResponse {
  reconciled_medication: string;
  confidence_score: number;
  reasoning: string;
  recommended_actions: string[];
  clinical_safety_check: ClinicalSafetyCheck;
  decision_factors?: {
    source_agreement?: number;
    recency?: number;
    source_reliability?: number;
    clinical_context_match?: number;
  };
}

export interface DataQualityRequest {
  demographics: {
    name?: string;
    dob?: string;
    gender?: string;
  };
  medications: string[];
  allergies: string[];
  conditions: string[];
  vital_signs: Record<string, string | number>;
  last_updated: string;
  recent_labs?: Record<string, string | number>;
}

export interface DataQualityIssue {
  field: string;
  issue: string;
  severity: SeverityLevel;
}

export interface DataQualityResponse {
  overall_score: number;
  breakdown: {
    completeness: number;
    accuracy: number;
    timeliness: number;
    clinical_plausibility: number;
  };
  issues_detected: DataQualityIssue[];
  summary?: string;
  dimension_explanations?: {
    completeness?: string;
    accuracy?: string;
    timeliness?: string;
    clinical_plausibility?: string;
  };
}