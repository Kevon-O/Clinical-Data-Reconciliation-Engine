import { useMemo, useState } from "react";
import { reconcileMedication } from "../api/client";
import {
  medicationMockResult,
  medicationSampleCases,
} from "../mock/medicationMock";
import type { MedicationReconciliationResponse } from "../types/api";

type ReviewStatus = "pending" | "approved" | "rejected";

type MedicationViewModel = {
  reconciledMedication: string;
  confidenceScore: number;
  reasoning: string;
  recommendedActions: string[];
  clinicalSafetyCheck: string;
  decisionFactors: {
    sourceAgreement: number;
    recency: number;
    sourceReliability: number;
    clinicalContextMatch: number;
  };
};

// Maps the backend snake_case response into the frontend display shape.
function mapMedicationResponseToViewModel(
  response: MedicationReconciliationResponse
): MedicationViewModel {
  return {
    reconciledMedication: response.reconciled_medication,
    confidenceScore: response.confidence_score,
    reasoning: response.reasoning,
    recommendedActions: response.recommended_actions,
    clinicalSafetyCheck: response.clinical_safety_check,
    decisionFactors: {
      sourceAgreement: response.decision_factors?.source_agreement ?? 0,
      recency: response.decision_factors?.recency ?? 0,
      sourceReliability: response.decision_factors?.source_reliability ?? 0,
      clinicalContextMatch: response.decision_factors?.clinical_context_match ?? 0,
    },
  };
}

export function MedicationPage() {
  const [result, setResult] = useState<MedicationViewModel>(medicationMockResult);
  const [isLoading, setIsLoading] = useState(false);
  const [statusText, setStatusText] = useState(
    "Select a medication case and run it to load a live backend result."
  );
  const [reviewStatus, setReviewStatus] = useState<ReviewStatus>("pending");
  const [activeSampleId, setActiveSampleId] = useState<string>(
    medicationSampleCases[0].id
  );

  const selectedSample = useMemo(
    () =>
      medicationSampleCases.find((sample) => sample.id === activeSampleId) ??
      medicationSampleCases[0],
    [activeSampleId]
  );

  const confidencePercent = Math.round(result.confidenceScore * 100);

  // Runs the selected medication sample through the live backend.
  async function handleRunSample() {
    try {
      setIsLoading(true);
      setStatusText(`Running sample: ${selectedSample.label}`);
      setReviewStatus("pending");

      const response = await reconcileMedication(selectedSample.payload);

      setResult(mapMedicationResponseToViewModel(response));
      setStatusText(`Live result loaded: ${selectedSample.label}`);
    } catch (error) {
      console.error(error);
      setStatusText("Backend request failed — showing fallback sample result");
      setResult(medicationMockResult);
      setReviewStatus("pending");
    } finally {
      setIsLoading(false);
    }
  }

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
              <p className="panel-eyebrow">Medication Demo Cases</p>
              <h3>Choose a Curated Scenario</h3>
            </div>
          </div>

          <div className="sample-grid">
            {medicationSampleCases.map((sample) => (
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
            <p className="panel-eyebrow">Recommended Outcome</p>
            <h3>Reconciled Medication Decision</h3>
          </div>

          <div className="score-pill">
            <span>Confidence</span>
            <strong>{confidencePercent}%</strong>
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

        <div className="decision-hero">
          <div className="decision-primary">
            <p className="content-label">Selected medication</p>
            <h2>{result.reconciledMedication}</h2>

            <div className="progress-block">
              <div className="progress-row">
                <span>Decision confidence</span>
                <span>{confidencePercent}%</span>
              </div>

              <div className="progress-bar">
                <div className="progress-fill" style={{ width: `${confidencePercent}%` }} />
              </div>
            </div>
          </div>

          <div className="safety-card">
            <p className="content-label">Clinical safety check</p>
            <div className="status-badge success">{result.clinicalSafetyCheck}</div>
            <p className="body-copy">
              This recommendation is generated from the structured backend workflow and,
              when available, enriched by the AI explanation layer before being shown.
            </p>
          </div>
        </div>

        <div className="content-block">
          <p className="content-label">Reasoning</p>
          <p className="body-copy">{result.reasoning}</p>
        </div>
      </div>

      <div className="panel">
        <div className="panel-header">
          <div>
            <p className="panel-eyebrow">Action Plan</p>
            <h3>Recommended Actions</h3>
          </div>
        </div>

        <div className="stack-list">
          {result.recommendedActions.map((action, index) => (
            <div className="list-card" key={`${action}-${index}`}>
              <span className="list-index">{index + 1}</span>
              <p>{action}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="panel">
        <div className="panel-header">
          <div>
            <p className="panel-eyebrow">Decision Breakdown</p>
            <h3>Supporting Factors</h3>
          </div>
        </div>

        <div className="metric-stack">
          <div className="metric-row">
            <div>
              <span className="metric-label">Source Agreement</span>
              <strong>{Math.round(result.decisionFactors.sourceAgreement * 100)}%</strong>
            </div>
            <div className="mini-progress">
              <div
                className="mini-progress-fill"
                style={{ width: `${Math.round(result.decisionFactors.sourceAgreement * 100)}%` }}
              />
            </div>
          </div>

          <div className="metric-row">
            <div>
              <span className="metric-label">Recency</span>
              <strong>{Math.round(result.decisionFactors.recency * 100)}%</strong>
            </div>
            <div className="mini-progress">
              <div
                className="mini-progress-fill"
                style={{ width: `${Math.round(result.decisionFactors.recency * 100)}%` }}
              />
            </div>
          </div>

          <div className="metric-row">
            <div>
              <span className="metric-label">Source Reliability</span>
              <strong>{Math.round(result.decisionFactors.sourceReliability * 100)}%</strong>
            </div>
            <div className="mini-progress">
              <div
                className="mini-progress-fill"
                style={{ width: `${Math.round(result.decisionFactors.sourceReliability * 100)}%` }}
              />
            </div>
          </div>

          <div className="metric-row">
            <div>
              <span className="metric-label">Clinical Context Match</span>
              <strong>{Math.round(result.decisionFactors.clinicalContextMatch * 100)}%</strong>
            </div>
            <div className="mini-progress">
              <div
                className="mini-progress-fill"
                style={{ width: `${Math.round(result.decisionFactors.clinicalContextMatch * 100)}%` }}
              />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}