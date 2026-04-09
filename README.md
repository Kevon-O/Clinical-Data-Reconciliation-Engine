**Clinical Data Reconciliation Engine**

Video Demo Link : Video Demo link - https://onedrive.live.com/?qt=allmyphotos&photosData=%2Fshare%2F31A4954CD0E4C4F9%21sb5119199ef394f59a35a7ca0e20a6175%3Fithint%3Dvideo%26e%3DdsZEDP%26migratedtospo%3Dtrue&cid=31A4954CD0E4C4F9&id=31A4954CD0E4C4F9%21sb5119199ef394f59a35a7ca0e20a6175&redeem=aHR0cHM6Ly8xZHJ2Lm1zL3YvYy8zMWE0OTU0Y2QwZTRjNGY5L0lRQ1prUkcxT2U5WlQ2TmFmS0RpQ21GMUFjN05QMmZ5Mlhmb1RWM0lqSHdyNlVJP2U9ZHNaRURQ&v=photos

**-Overview**

This is a full-stack application for reconciling conflicting medication records and evaluating EHR data quality. The backend produces deterministic structured results, while an optional AI enrichment layer improves reviewer-facing reasoning and explanations. If the model is unavailable, the system falls back to deterministic output.

**-Tech Stack**

-Frontend

• React

• Vite

• TypeScript

-Backend

• Python

• FastAPI

• Pydantic

• Uvicorn

**AI**

• OpenAI API

**Testing**

• pytest

**Containerization**

• Docker

• Docker Compose

**Storage**

• In-memory / sample-driven demo data


**-Setup & How to Test & Run Demos.**

**Option 1: Run with Docker**

Prerequisites

• Docker Desktop installed and running

Setup

Create a root .env file with:

OPENAI_API_KEY="Use your OpenAI key here"

OPENAI_MODEL=gpt-5.4-mini

The app will still run without an OpenAI key, but it will use the deterministic fallback instead of AI enrichment.

- Start

From the project root, run:

docker compose up --build

Open the app

• Frontend: http://localhost:5173

• Backend API: http://localhost:8000

• FastAPI docs: http://localhost:8000/docs

Stop

Press Ctrl + C in the terminal, then run:

docker compose down

**Option 2: Run without Docker**

Prerequisites

• Python 3.11+

• Node.js 20+

• npm installed

Backend setup

Open a terminal in the backend folder and run:

python -m venv .venv

Activate the virtual environment:

-macOS / Linux

source .venv/bin/activate

-Windows

.venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

pip install pytest

Set environment variables:

-macOS / Linux

export OPENAI_API_KEY="Use your OpenAI key here"

export OPENAI_MODEL=gpt-5.4-mini

-Windows

set OPENAI_API_KEY="Use your OpenAI key here"

set OPENAI_MODEL=gpt-5.4-mini

Then start the backend:

uvicorn app.main:app --reload

The backend will run at:

http://localhost:8000

Frontend setup

Open a second terminal in the frontend folder and run:

npm install

npm run dev

The frontend will run at:

http://localhost:5173

**Notes**

• The frontend is configured to call the backend on localhost:8000.

• If no OpenAI API key is used, the backend still works and returns the deterministic result.

• API documentation is available at http://localhost:8000/docs

• For local/demo use, the frontend sends x-api-key: dev-secret-key, and the backend accepts that value by default unless a custom API_KEY is configured.

**Testing and Running Demos**

-The runnable demo cases used in the frontend live in

frontend/src/mock/medicationMock.ts

frontend/src/mock/dataQualityMock.ts

These sample payloads are sent to the live backend, so editing fields like medication text, source dates, source reliability, conditions, labs, allergies, or vitals can produce different results in the app.

-Automated Backend Test Data

Backend test coverage lives in

backend/app/tests/test_medication_reconciliation.py

backend/app/tests/test_data_quality.py

backend/app/tests/test_auth.py

These files are used for automated backend testing and are separate from the frontend demo samples.

-Running Backend Tests

From the backend/ folder, run pytest.

**Architecture Summary**

The backend is organized into request/response schemas, normalized internal models, deterministic service logic, and an optional AI enrichment layer. The system computes the core result deterministically first, then uses AI only to improve explanation quality when available.

The frontend is designed as a reviewer workflow where users select scenarios, run them, and evaluate results rather than interacting directly with raw APIs.

**Key Design Decisions**

• Deterministic backend as the source of truth for reliability

• AI used to enhance explanations, not make core decisions

• Clear separation between API input and backend logic

• Curated demo scenarios for stable and effective demos

• In-memory storage to focus on logic and workflow

• Dockerized setup for easier evaluation
