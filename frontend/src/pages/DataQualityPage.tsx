import { useMemo, useState } from "react";
import { validateDataQuality } from "../api/client";
import {
  dataQualityMockResult,
  dataQualitySampleCases,
} from "../mock/dataQualityMock";
import type { DataQualityResponse } from "../types/api";

type ReviewStatus = "pending" | "approved" | "rejected";

type DataQualityViewModel = {
  overallScore: number;
  summary: string;
  breakdown: {
    completeness: number;
    accuracy: number;
    timeliness: number;
    clinicalPlausibility: number;
  };
  issues: Array<{
    field: string;
    issue: string;
    severity: "low" | "medium" | "high";
  }>;
  dimensionExplanations: {
    completeness: string;
    accuracy: string;
    timeliness: string;
    clinicalPlausibility: string;
  };
};

// Maps the backend snake_case response into the frontend display shape.
function mapDataQualityResponseToViewModel(
  response: DataQualityResponse
): DataQualityViewModel {
  return {
    overallScore: response.overall_score,
    summary: response.summary ?? "",
    breakdown: {
      completeness: response.breakdown.completeness,
      accuracy: response.breakdown.accuracy,
      timeliness: response.breakdown.timeliness,
      clinicalPlausibility: response.breakdown.clinical_plausibility,
    },
    issues: response.issues_detected.map((issue) => ({
      field: issue.field,
      issue: issue.issue,
      severity: issue.severity,
    })),
    dimensionExplanations: {
      completeness: response.dimension_explanations?.completeness ?? "",
      accuracy: response.dimension_explanations?.accuracy ?? "",
      timeliness: response.dimension_explanations?.timeliness ?? "",
      clinicalPlausibility:
        response.dimension_explanations?.clinical_plausibility ?? "",
    },
  };
}

// Returns a simple traffic-light class based on score strength.
function getScoreTone(score: number): "good" | "warning" | "danger" {
  if (score >= 80) {
    return "good";
  }

  if (score >= 60) {
    return "warning";
  }

  return "danger";
}

export function DataQualityPage() {
  const [result, setResult] = useState<DataQualityViewModel>(dataQualityMockResult);
  const [isLoading, setIsLoading] = useState(false);
  const [statusText, setStatusText] = useState(
    "Select a data-quality case and run it to load a live backend result."
  );
  const [reviewStatus, setReviewStatus] = useState<ReviewStatus>("pending");
  const [activeSampleId, setActiveSampleId] = useState<string>(
    dataQualitySampleCases[0].id
  );

  const selectedSample = useMemo(
    () =>
      dataQualitySampleCases.find((sample) => sample.id === activeSampleId) ??
      dataQualitySampleCases[0],
    [activeSampleId]
  );

  // Runs the selected data-quality sample through the live backend.
  async function handleRunSample() {
    try {
      setIsLoading(true);
      setStatusText(`Running sample: ${selectedSample.label}`);
      setReviewStatus("pending");

      const response = await validateDataQuality(selectedSample.payload);

      setResult(mapDataQualityResponseToViewModel(response));
      setStatusText(`Live result loaded: ${selectedSample.label}`);
    } catch (error) {
      console.error(error);
      setStatusText("Backend request failed — showing fallback sample result");
      setResult(dataQualityMockResult);
      setReviewStatus("pending");
    } finally {
      setIsLoading(false);
    }
  }

  const completenessTone = getScoreTone(result.breakdown.completeness);
  const accuracyTone = getScoreTone(result.breakdown.accuracy);
  const timelinessTone = getScoreTone(result.breakdown.timeliness);
  const plausibilityTone = getScoreTone(result.breakdown.clinicalPlausibility);

  return (
    <section className="dashboard-grid">
      <div className="panel panel-large">
        <div className="panel-toolbar">
          <div className="toolbar-status">{statusText}</div>

          <div className="toolbar-actions">
            <button className="run-button" onClick={handleRunSample} disabled={isLoading}>
              {isLoading ? "Running..." : "Run Selected Case"}
            </button>
          </div>
        </div>

        <div className="sample-section">
          <div className="panel-header">
            <div>
              <p className="panel-eyebrow">Data Quality Demo Cases</p>
              <h3>Choose a Curated Scenario</h3>
            </div>
          </div>

          <div className="sample-grid">
            {dataQualitySampleCases.map((sample) => (
              <button
                key={sample.id}
                className={
                  sample.id === activeSampleId ? "sample-card active" : "sample-card"
                }
                onClick={() => setActiveSampleId(sample.id)}
              >
                <span className="sample-title">{sample.label}</span>
                <span className="sample-description">{sample.summary}</span>
              </button>
            ))}
          </div>

          <div className="sample-summary">
            <p className="content-label">Selected case</p>
            <p className="body-copy">{selectedSample.summary}</p>
          </div>
        </div>

        <div className="panel-header">
          <div>
            <p className="panel-eyebrow">Record Health</p>
            <h3>Overall Data Quality Score</h3>
          </div>

          <div className="score-orb">
            <span>Score</span>
            <strong>{result.overallScore}</strong>
          </div>
        </div>

        <div className="review-toolbar">
          <div className={`review-state review-state-${reviewStatus}`}>
            {reviewStatus === "pending" && "Pending review"}
            {reviewStatus === "approved" && "Suggestion approved"}
            {reviewStatus === "rejected" && "Suggestion rejected"}
          </div>

          <div className="review-actions">
            <button
              className={`review-button approve ${reviewStatus === "approved" ? "active" : ""}`}
              onClick={() => setReviewStatus("approved")}
            >
              Approve
            </button>

            <button
              className={`review-button reject ${reviewStatus === "rejected" ? "active" : ""}`}
              onClick={() => setReviewStatus("rejected")}
            >
              Reject
            </button>
          </div>
        </div>

        <div className="content-block">
          <p className="content-label">Summary</p>
          <p className="body-copy">{result.summary}</p>
        </div>

        <div className="metrics-grid">
          <div className={`metric-card metric-tone-${completenessTone}`}>
            <span>Completeness</span>
            <strong>{result.breakdown.completeness}</strong>
          </div>

          <div className={`metric-card metric-tone-${accuracyTone}`}>
            <span>Accuracy</span>
            <strong>{result.breakdown.accuracy}</strong>
          </div>

          <div className={`metric-card metric-tone-${timelinessTone}`}>
            <span>Timeliness</span>
            <strong>{result.breakdown.timeliness}</strong>
          </div>

          <div className={`metric-card metric-tone-${plausibilityTone}`}>
            <span>Clinical Plausibility</span>
            <strong>{result.breakdown.clinicalPlausibility}</strong>
          </div>
        </div>
      </div>

      <div className="panel">
        <div className="panel-header">
          <div>
            <p className="panel-eyebrow">Detected Issues</p>
            <h3>Issues Found</h3>
          </div>
        </div>

        <div className="stack-list">
          {result.issues.map((issue, index) => (
            <div className="list-card severity-card" key={`${issue.field}-${issue.issue}-${index}`}>
              <span className="list-index">{index + 1}</span>

              <div className="issue-copy">
                <p className="issue-title">{issue.field}</p>
                <p className="issue-text">{issue.issue}</p>
                <span className={`severity-pill ${issue.severity}`}>
                  {issue.severity} severity
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="panel">
        <div className="panel-header">
          <div>
            <p className="panel-eyebrow">Dimension Notes</p>
            <h3>Score Explanations</h3>
          </div>
        </div>

        <div className="explanation-grid">
          <div className="explanation-card">
            <span>Completeness</span>
            <p>{result.dimensionExplanations.completeness}</p>
          </div>

          <div className="explanation-card">
            <span>Accuracy</span>
            <p>{result.dimensionExplanations.accuracy}</p>
          </div>

          <div className="explanation-card">
            <span>Timeliness</span>
            <p>{result.dimensionExplanations.timeliness}</p>
          </div>

          <div className="explanation-card">
            <span>Clinical Plausibility</span>
            <p>{result.dimensionExplanations.clinicalPlausibility}</p>
          </div>
        </div>
      </div>
    </section>
  );
}