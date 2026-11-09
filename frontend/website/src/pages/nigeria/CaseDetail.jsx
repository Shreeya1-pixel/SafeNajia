import { Link, useNavigate, useParams } from "react-router-dom";
import { THREAT_CASES } from "../../data/threatCases";
import { DEMO_SAMPLES } from "../../data/demoSamples";
import { authorityOf, categoryName } from "../../data/caseTaxonomy";
import { analyzeHrefForCase, CASE_TO_SAMPLE } from "../../data/caseAnalyzeLinks";

export default function CaseDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const c = THREAT_CASES.find((x) => x.id === id);
  const idx = THREAT_CASES.findIndex((x) => x.id === id);
  const next = THREAT_CASES[(idx + 1) % THREAT_CASES.length];
  const sampleId = CASE_TO_SAMPLE[id];
  const sample = sampleId ? DEMO_SAMPLES.find((s) => s.id === sampleId) : null;

  if (!c) {
    return (
      <div className="ng-page">
        <header className="safeo-page-header">
          <h2>Case not found</h2>
          <p className="ng-muted">That report is not in the Nigerian Threat Case Library.</p>
          <Link to="/cases" className="sim-run-btn">
            ← Case library
          </Link>
        </header>
      </div>
    );
  }

  return (
    <div className="ng-page ng-case-detail">
      <nav className="ng-breadcrumb">
        <Link to="/cases">Case library</Link>
        <span aria-hidden> / </span>
        <span className="ng-muted">Report</span>
      </nav>

      <header className="ng-card ng-case-detail-hero">
        <div className="ng-case-meta-row">
          <span className="ng-case-label">{c.label}</span>
          <span className="ng-case-cat">{categoryName(c.threatType)}</span>
          <time className="ng-muted">{c.date}</time>
        </div>
        <p className="ng-eyebrow">Threat intelligence report</p>
        <h2>{c.name}</h2>
        <div className="ng-case-detail-meta">
          <div>
            <div className="ng-eyebrow">Reporting authority</div>
            <strong>{authorityOf(c.sourceOrg)}</strong>
            <p className="ng-muted">{c.sourceOrg}</p>
          </div>
          <div>
            <div className="ng-eyebrow">Affected</div>
            <p>{c.target}</p>
          </div>
          <div>
            <div className="ng-eyebrow">Evidence</div>
            <p>
              {c.indicators.length} indicators · {1 + (c.supportingUrls?.length || 0)} source
              {(1 + (c.supportingUrls?.length || 0)) === 1 ? "" : "s"}
            </p>
          </div>
        </div>
      </header>

      <div className="ng-case-detail-grid">
        <div>
          <section className="ng-card">
            <h3 className="ng-eyebrow">Why it matters</h3>
            <p className="ng-case-lead">{c.whyItMatters}</p>
          </section>

          <section className="ng-card">
            <h3 className="ng-eyebrow">Mechanism</h3>
            <p>{c.mechanism}</p>
          </section>

          <section className="ng-card">
            <h3>Victim journey</h3>
            <ol className="ng-journey">
              {(c.victimJourney || []).map((step, i) => (
                <li key={step}>
                  <span className="ng-journey-n">{i + 1}</span>
                  <span>{step}</span>
                </li>
              ))}
            </ol>
          </section>

          <section className="ng-card">
            <h3 className="ng-eyebrow">Official response</h3>
            <p>{c.response}</p>
          </section>

          <section className="ng-card ng-analyze-cta-card">
            <h3 className="ng-eyebrow">How SafeNaija analyses it</h3>
            <p>{c.safeNaijaAnalysis}</p>
            {sample && (
              <p className="ng-muted" style={{ marginTop: 8 }}>
                Linked demo sample: <strong>{sample.title}</strong> ({sample.label})
              </p>
            )}
            <button
              type="button"
              className="sim-run-btn"
              style={{ marginTop: 12 }}
              onClick={() => navigate(analyzeHrefForCase(c.id))}
            >
              Analyze a similar message →
            </button>
          </section>
        </div>

        <aside>
          <section className="ng-card">
            <h3 className="ng-eyebrow">Indicators</h3>
            <p className="ng-muted">Defanged — shown as text, never as links.</p>
            <ul>
              {c.indicators.map((v) => (
                <li key={v}>
                  <code>{v}</code>
                </li>
              ))}
            </ul>
          </section>

          <section className="ng-card">
            <h3 className="ng-eyebrow">Sources</h3>
            <ul className="ng-source-list">
              <li>
                <a href={c.sourceUrl} target="_blank" rel="noreferrer">
                  {c.sourceOrg} →
                </a>
              </li>
              {(c.supportingUrls || []).map((u, i) => (
                <li key={u}>
                  <a href={u} target="_blank" rel="noreferrer">
                    Supporting source {i + 1} →
                  </a>
                </li>
              ))}
            </ul>
          </section>

          {c.sourceAudit && (
            <section className="ng-card">
              <h3 className="ng-eyebrow">Source audit · {c.sourceAudit.checkedOn}</h3>
              <p className="ng-muted">{c.sourceAudit.notes}</p>
            </section>
          )}

          <section className="ng-card">
            <h3 className="ng-eyebrow">Category: {categoryName(c.threatType)}</h3>
            <Link to="/analyze" className="ng-linkish">
              Open blank Analyze workspace →
            </Link>
          </section>
        </aside>
      </div>

      <div className="ng-case-detail-nav">
        <Link to="/cases" className="ng-btn-ghost">
          ← All cases
        </Link>
        {next && (
          <Link to={`/cases/${next.id}`} className="sim-run-btn">
            Next: {next.name.slice(0, 48)}
            {next.name.length > 48 ? "…" : ""} →
          </Link>
        )}
      </div>
    </div>
  );
}
