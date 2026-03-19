import type { DataQualityRequest } from "../types/api";

export type DataQualitySampleCase = {
  id: string;
  label: string;
  summary: string;
  payload: DataQualityRequest;
};

export const dataQualityMockResult = {
  overallScore: 62,
  summary: "The record is usable but has several quality issues that should be reviewed.",
  breakdown: {
    completeness: 60,
    accuracy: 50,
    timeliness: 70,
    clinicalPlausibility: 40,
  },
  issues: [
    {
      field: "allergies",
      issue: "No allergies documented - likely incomplete.",
      severity: "medium" as const,
    },
    {
      field: "vital_signs.blood_pressure",
      issue: "Blood pressure 340/180 is physiologically implausible.",
      severity: "high" as const,
    },
    {
      field: "last_updated",
      issue: "Data is more than 6 months old.",
      severity: "medium" as const,
    },
  ],
  dimensionExplanations: {
    completeness:
      "Several expected sections are present, but allergies are undocumented.",
    accuracy:
      "Some values are formatted correctly, but not all recorded values appear reliable.",
    timeliness:
      "The record appears stale based on its last update date.",
    clinicalPlausibility:
      "At least one value is outside a believable physiologic range.",
  },
};

// Curated data-quality cases used for the live demo.
export const dataQualitySampleCases: DataQualitySampleCase[] = [
  {
    id: "clean-thyroid-record",
    label: "Mostly Clean Endocrine Record",
    summary:
      "A recent hypothyroidism chart with complete demographics, allergy data, recent labs, and plausible vitals. Designed to score well.",
    payload: {
      demographics: {
        name: "Maria Chen",
        dob: "1988-11-08",
        gender: "F",
      },
      medications: ["Levothyroxine 75mcg daily"],
      allergies: ["Penicillin"],
      conditions: ["Hypothyroidism"],
      vital_signs: {
        blood_pressure: "118/74",
        heart_rate: 68,
        temperature: 98.4,
      },
      last_updated: "2026-02-20",
      recent_labs: {
        tsh: 2.1,
      },
    },
  },
  {
    id: "stale-diabetes-record",
    label: "Stale Diabetes / Hypertension Record",
    summary:
      "A plausible but stale chronic-disease record with missing allergies and older updates. Designed to land in the middle range.",
    payload: {
      demographics: {
        name: "John Doe",
        dob: "1955-03-15",
        gender: "M",
      },
      medications: ["Metformin 500mg", "Lisinopril 10mg"],
      allergies: [],
      conditions: ["Type 2 Diabetes", "Hypertension"],
      vital_signs: {
        blood_pressure: "154/94",
        heart_rate: 72,
      },
      last_updated: "2024-06-15",
      recent_labs: {},
    },
  },
  {
    id: "sparse-copd-record",
    label: "Sparse Pulmonary Record With Implausible Data",
    summary:
      "A weak COPD-related chart with missing sections, stale updates, and implausible vitals. Designed to score poorly.",
    payload: {
      demographics: {
        name: "Unknown",
        gender: "M",
      },
      medications: [],
      allergies: [],
      conditions: ["COPD"],
      vital_signs: {
        blood_pressure: "360/180",
        heart_rate: 280,
      },
      last_updated: "2024-01-10",
      recent_labs: {},
    },
  },
];