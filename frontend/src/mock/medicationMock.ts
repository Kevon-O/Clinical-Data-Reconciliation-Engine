import type { MedicationReconciliationRequest } from "../types/api";

export type MedicationSampleCase = {
  id: string;
  label: string;
  summary: string;
  payload: MedicationReconciliationRequest;
};

export const medicationMockResult = {
  reconciledMedication: "Metformin 500mg twice daily",
  confidenceScore: 0.88,
  reasoning:
    "Primary care is the strongest recent clinical source, and the selected dose fits the available kidney function context better than the competing records.",
  recommendedActions: [
    "Review and update Hospital EHR if it does not match the selected medication.",
    "Review and update Pharmacy if it does not match the selected medication.",
    "Confirm the final reconciled medication list during the next clinical review.",
  ],
  clinicalSafetyCheck: "PASSED",
  decisionFactors: {
    sourceAgreement: 0.45,
    recency: 0.9,
    sourceReliability: 0.8,
    clinicalContextMatch: 0.9,
  },
};

// Curated medication reconciliation cases used for the live demo.
export const medicationSampleCases: MedicationSampleCase[] = [
  {
    id: "metformin-ckd-conflict",
    label: "Diabetes + CKD Dose Conflict",
    summary:
      "Metformin records disagree across hospital, nephrology, and pharmacy sources. Designed to show a safer lower-dose choice with relatively strong confidence.",
    payload: {
      patient_context: {
        age: 67,
        conditions: ["Type 2 Diabetes", "Chronic Kidney Disease"],
        recent_labs: {
          eGFR: 42,
        },
      },
      sources: [
        {
          system: "Hospital EHR",
          medication: "Metformin 1000mg twice daily",
          last_updated: "2025-12-10",
          source_reliability: "high",
        },
        {
          system: "Nephrology Clinic",
          medication: "Metformin 500mg twice daily",
          last_updated: "2026-02-18",
          source_reliability: "high",
        },
        {
          system: "Pharmacy",
          medication: "Metformin 1000mg daily",
          last_filled: "2026-02-20",
          source_reliability: "medium",
        },
      ],
    },
  },
  {
    id: "aspirin-dose-disagreement",
    label: "Cardiology Aspirin Disagreement",
    summary:
      "Aspirin dose conflicts across discharge, cardiology follow-up, and retail pharmacy sources. Designed to produce a middling confidence result.",
    payload: {
      patient_context: {
        age: 74,
        conditions: ["Coronary Artery Disease", "Prior TIA"],
        recent_labs: {},
      },
      sources: [
        {
          system: "Hospital Discharge",
          medication: "Aspirin 81mg daily",
          last_updated: "2026-01-08",
          source_reliability: "high",
        },
        {
          system: "Cardiology Clinic",
          medication: "Aspirin 325mg daily",
          last_updated: "2026-01-11",
          source_reliability: "high",
        },
        {
          system: "Retail Pharmacy",
          medication: "Aspirin 81mg daily",
          last_filled: "2026-01-09",
          source_reliability: "medium",
        },
      ],
    },
  },
  {
    id: "furosemide-frequency-conflict",
    label: "Heart Failure Diuretic Conflict",
    summary:
      "Furosemide frequency varies across inpatient, outpatient, and pharmacy records. Designed to show a more disagreement-heavy, lower-confidence reconciliation.",
    payload: {
      patient_context: {
        age: 71,
        conditions: ["Heart Failure", "Peripheral Edema"],
        recent_labs: {},
      },
      sources: [
        {
          system: "Hospital EHR",
          medication: "Furosemide 1000mg twice daily",
          last_updated: "2023-11-02",
          source_reliability: "high",
        },
        {
          system: "Cardiology Clinic",
          medication: "Furosemide 1000mg daily",
          last_updated: "2022-02-03",
          source_reliability: "high",
        },
        {
          system: "Pharmacy",
          medication: "Furosemide 40mg daily",
          last_filled: "2026-02-05",
          source_reliability: "medium",
        },
      ],
    },
  },
];