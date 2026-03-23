**Clinical Data Reconciliation Engine**


Video Demo Link : Video Demo link - https://onedrive.live.com/?qt=allmyphotos&photosData=%2Fshare%2F31A4954CD0E4C4F9%21sb5119199ef394f59a35a7ca0e20a6175%3Fithint%3Dvideo%26e%3DdsZEDP%26migratedtospo%3Dtrue&cid=31A4954CD0E4C4F9&id=31A4954CD0E4C4F9%21sb5119199ef394f59a35a7ca0e20a6175&redeem=aHR0cHM6Ly8xZHJ2Lm1zL3YvYy8zMWE0OTU0Y2QwZTRjNGY5L0lRQ1prUkcxT2U5WlQ2TmFmS0RpQ21GMUFjN05QMmZ5Mlhmb1RWM0lqSHdyNlVJP2U9ZHNaRURQ&v=photos



**-Setup \& How to Test \& Run Demos.**



**Option 1: Run with Docker**



**Prerequisites**

• Docker Desktop installed and running



**Setup**

Create a root .env file with:



OPENAI\_API\_KEY="Use your OpenAi key here"

OPENAI\_MODEL=gpt-5.4-mini



**The app will still run without an OpenAI key, but it will use the deterministic fallback instead of AI enrichment.**



**Start**

From the project root, run: 

docker compose up --build



**Open the app**

• Frontend: http://localhost:5173



• Backend API: http://localhost:8000



• FastAPI docs: http://localhost:8000/docs



**Stop**

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



**Activate the virtual environment:**



macOS / Linux

source .venv/bin/activate



Windows

.venv\\Scripts\\activate



**Install dependencies:**



pip install -r requirements.txt



**Create a backend/.env file with:**



OPENAI\_API\_KEY="use your OpenAi key here"

OPENAI\_MODEL=gpt-5.4-mini



**Then start the backend:**



uvicorn app.main:app --reload



The backend will run at:

http://localhost:8000



**Frontend setup**

Open a second terminal in the frontend folder and run:



npm install

npm run dev



The frontend will run at:

http://localhost:5173



**Notes**

• The frontend is configured to call the backend on localhost:8000.

• If no OpenAI API key is used, the backend still works and returns the deterministic result.

• API documentation is available at http://localhost:8000/docs



**Testing and Running Demos**

The runnable demo cases used in the frontend live in 

frontend/src/mock/medicationMock.ts

frontend/src/mock/dataQualityMock.ts



These sample payloads are sent to the live backend, so editing fields like medication text, source dates, source reliability, conditions, labs, allergies, or vitals can produce different results in the app.



**Automated Backend Test Data**



Backend test coverage lives in 

backend/app/tests/test\_medication\_reconciliation.py

backend/app/tests/test\_data\_quality.py 

backend/app/tests/test\_auth.py



These files are used for automated backend testing and are separate from the frontend demo samples.



**Running Backend Tests**



From the backend/ folder, run pytest.







**-Why OpenAI?**



I used the OpenAI API because it was a strong fit for the kind of LLM support this project needed. Since the goal of the AI in this project is not to replace structured logic, but to improve how the result is communicated to a person reading the output. It was also the most practical choice for me because it is the LLM platform I have the most hands-on experience with.



**-What I Would Improve With More Time.**



I would expand the frontend so a anyone could enter or edit more case details directly on the page instead of relying only on the demo samples and editing those case details through the backend. I would also spend more time broadening the clinical logic coverage, improving duplicate record detection, and refining how confidence and data-quality scores respond across a wider range of edge cases. I also would have liked to deploy the project so it could be shared through a live link instead of only being run locally or through Docker.



**-Estimate Time Spent**



I believe I've spent roughly 25-30 hours on this project. Unfortunately I wasn't able to fully utilize all 6 days due to personal circumstances interfering.





