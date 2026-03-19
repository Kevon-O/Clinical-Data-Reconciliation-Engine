## Prompt Engineering and AI Enrichment Approach

## Overview

The backend is built around two layers:
1. A **deterministic core** that produces the structured result.
2. An **AI enrichment layer** that attempts to improve the explanation quality before the response is returned by providing richer clinical reasoning, more human-readable explanations, better issue descriptions and support for identifying suspicious or implausible data patterns


The deterministic layer remains the clinical and technical foundation of the system. The AI layer is used to make the output more readable, more context-aware. In the live request flow, the backend first computes the deterministic result and then attempts AI enrichment. If the AI call succeeds, the enriched response is returned. If the AI call fails or no OpenAI key is available, the deterministic response is returned instead.

## What the Deterministic Layer Does

The deterministic layer is responsible for the structured output.

For medication reconciliation, it determines:
- reconciled medication
- confidence score
- clinical safety check
- structured decision factors

For data quality validation, it determines:
- overall score
- score breakdown
- issues detected
- core summary structure

That means the backend has a strong baseline result before AI is ever called, and if the model is unavailable, rate-limited, or misconfigured, the system still returns a usable result.

## What the AI Layer Does

The AI layer attempts to improve the returned response by making it more useful to a reader.

### Medication reconciliation enrichment
The model can improve:
- reasoning
- recommended actions
- clarity of safety explanation

### Data quality enrichment
The model can improve:
- summary wording
- dimension explanations
- issue descriptions
- reviewer-facing explanation of suspicious patterns

The AI layer sees both:
- the normalized input case
- the deterministic output

## What the AI Layer Is Not Allowed to Do

The prompts are designed so that the AI layer does not override the deterministic backbone.

The model should not freely invent or replace:
- the reconciled medication winner
- the confidence score
- the clinical safety check
- the overall data-quality score
- the deterministic score breakdown

Instead, it should work within those boundaries and improve the response quality around them.


## Medication Prompt Strategy

The medication enrichment prompt is designed to help the model explain why one medication record was selected over competing records.

The prompt emphasizes:
- source disagreement
- source recency
- source reliability
- clinical context clues
- reviewer-friendly explanation

The intended model behavior is:
- keep the backend’s selected medication
- explain why that result is reasonable
- produce clearer recommended follow-up steps
- keep the tone concise and clinical, not speculative

## Data Quality Prompt Strategy

The data-quality enrichment prompt is designed to help the model explain why a chart scored the way it did and why certain issues matter.

The prompt emphasizes:
- completeness
- accuracy concerns
- timeliness
- clinical plausibility
- issue explanation quality

The intended model behavior is:
- preserve the backend’s overall score and score breakdown
- improve the summary wording
- explain why the detected issues matter
- provide more useful reviewer-facing dimension explanations

## Caching Strategy

The project includes in-memory caching for AI enrichment results.

This means repeated requests with the same normalized input and deterministic result can reuse a previous enrichment output instead of making a fresh model call every time. The cache is intentionally in-memory because the overall project also uses in-memory storage.

## Failure Handling

The AI layer is designed to fail safely.

If the model call does not succeed, the system should:
- log the issue internally
- skip enrichment
- return the deterministic response instead

This prevents the user-facing workflow from breaking just because the model is unavailable.



