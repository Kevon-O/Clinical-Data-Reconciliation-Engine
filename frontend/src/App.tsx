import { useMemo, useState } from "react";
import "./styles/app.css";
import { DataQualityPage } from "./pages/DataQualityPage";
import { MedicationPage } from "./pages/MedicationPage";

type View = "medication" | "data-quality";

function App() {
  const [view, setView] = useState<View>("medication");

  const pageMeta = useMemo(() => {
    if (view === "medication") {
      return {
        eyebrow: "Clinical Reconciliation",
        title: "Medication Reconciliation Engine",
        description:
          "Compare conflicting medication records, surface confidence, and present a reviewer-friendly decision with clear supporting signals.",
      };
    }

    return {
      eyebrow: "Patient Record Validation",
      title: "EHR Data Quality Review",
      description:
        "Inspect completeness, accuracy, timeliness, and plausibility across a patient record in one polished review workspace.",
    };
  }, [view]);

  return (
    <div className="app-shell">
      <div className="app-background" />
      <div className="app-grid-overlay" />

      <header className="topbar">
        <div className="brand-block">
          <div className="brand-mark">ER</div>

          <div>
            <p className="brand-eyebrow">EHR Reconciliation Engine</p>
            <h1 className="brand-title">Clinical Data Review Workspace</h1>
          </div>
        </div>

        <div className="topbar-pill">FastAPI + React Demo</div>
      </header>

      <main className="page-frame">
        <section className="hero-panel">
          <div className="hero-copy">
            <p className="section-eyebrow">{pageMeta.eyebrow}</p>
            <h2>{pageMeta.title}</h2>
            <p className="hero-description">{pageMeta.description}</p>
          </div>

          <div className="view-switcher" role="tablist" aria-label="Workflow Switcher">
            <button
              className={view === "medication" ? "view-tab active" : "view-tab"}
              onClick={() => setView("medication")}
            >
              <span className="view-tab-label">Medication Reconciliation</span>
              <span className="view-tab-subtitle">
                Resolve conflicting medication records
              </span>
            </button>

            <button
              className={view === "data-quality" ? "view-tab active" : "view-tab"}
              onClick={() => setView("data-quality")}
            >
              <span className="view-tab-label">Data Quality Validation</span>
              <span className="view-tab-subtitle">
                Review record quality and major issues
              </span>
            </button>
          </div>
        </section>

        <section className="workspace-panel">
          {view === "medication" ? <MedicationPage /> : <DataQualityPage />}
        </section>
      </main>
    </div>
  );
}

export default App;