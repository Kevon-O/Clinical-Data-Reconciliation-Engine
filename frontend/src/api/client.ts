import type {
  DataQualityRequest,
  DataQualityResponse,
  MedicationReconciliationRequest,
  MedicationReconciliationResponse,
} from "../types/api";

const API_BASE_URL = "http://127.0.0.1:8000";
const API_KEY = "dev-secret-key";

async function postJson<TResponse, TRequest>(
  path: string,
  payload: TRequest
): Promise<TResponse> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": API_KEY,
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Request failed (${response.status}): ${text}`);
  }

  return response.json() as Promise<TResponse>;
}

// Sends a medication reconciliation request to the backend.
export function reconcileMedication(payload: MedicationReconciliationRequest) {
  return postJson<MedicationReconciliationResponse, MedicationReconciliationRequest>(
    "/api/reconcile/medication",
    payload
  );
}

// Sends a data-quality validation request to the backend.
export function validateDataQuality(payload: DataQualityRequest) {
  return postJson<DataQualityResponse, DataQualityRequest>(
    "/api/validate/data-quality",
    payload
  );
}