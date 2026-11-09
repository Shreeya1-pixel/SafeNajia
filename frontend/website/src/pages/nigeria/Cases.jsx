import { useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { THREAT_CASES, SOURCE_REGISTRY, TRUSTED_ENTITIES } from "../../data/threatCases";
import { DEMO_SAMPLES } from "../../data/demoSamples";
import { CATEGORY_NAMES, authorityOf, categoryName, EXPECTED_SEV } from "../../data/caseTaxonomy";

const KIND_LABEL = { text: "Message", url: "URL", email: "Email", screenshot: "Screenshot" };

export default function Cases() {
  const navigate = useNavigate();
  const [tab, setTab] = useState("cases"); // cases | samples | sources | entities
  const [open, setOpen] = useState(null);
  const [q, setQ] = useState("");
  const [cat, setCat] = useState("all");
  const [auth, setAuth] = useState("all");
  const [sort, setSort] = useState("newest");
  const [sev, setSev] = useState("all");
  const [kind, setKind] = useState("all");

  const caseList = useMemo(() => {
    const needle = q.trim().toLowerCase();
    return THREAT_CASES.filter((c) => {
      if (cat !== "all" && c.threatType !== cat) return false;
      if (auth !== "all" && authorityOf(c.sourceOrg) !== auth) return false;
      if (!needle) return true;
      const blob = `${c.name} ${c.mechanism} ${c.target} ${c.sourceOrg}`.toLowerCase();
      return blob.includes(needle);
    }).sort((a, b) => (sort === "newest" ? b.date.localeCompare(a.date) : a.date.localeCompare(b.date)));
  }, [q, cat, auth, sort]);

  const sampleList = useMemo(() => {
    return DEMO_SAMPLES.filter((s) => {
      if (sev !== "all" && EXPECTED_SEV[s.expected] !== sev) return false;
      if (kind !== "all" && s.kind !== kind) return false;
      return true;
    });
  }, [sev, kind]);

  const authorities = useMemo(
    () => [...new Set(THREAT_CASES.map((c) => authorityOf(c.sourceOrg)))],
    []
  );

  function analyzeSample(s) {
    if (s.kind === "url") {
      navigate("/links", { state: { sampleUrl: s.content, sampleTitle: s.title } });
      return;
    }
    navigate("/messages", {
      state: {
        sampleText: s.content,
        sampleTitle: s.title,
        sampleChannel: s.kind === "email" ? "gmail" : "manual",
      },
    });
  }

  return (
    <div className="ng-page">
      <header className="safeo-page-header">
        <h2>Nigerian Threat Case Library</h2>
        <p>
          Documented incidents and advisories that shaped SafeNaija’s rules. Every historical case links to
          its public source; indicators are defanged and never clickable.
        </p>
        <p className="ng-muted" style={{ marginTop: 6 }}>
          <span className="ng-case-label">HISTORICAL CASE</span>{" "}
          <span className="ng-case-label ng-case-label-real">REAL, SOURCED</span>
        </p>
      </header>

      <div className="ng-sample-row">
        {[
          ["cases", "Historical cases"],
          ["samples", "Demo & evaluation samples"],
          ["sources", "Research source registry"],
          ["entities", "Trusted entities"],
        ].map(([id, label]) => (
          <button
            key={id}
            type="button"
            className={`ng-chip ${tab === id ? "active" : ""}`}
            onClick={() => setTab(id)}
          >
            {label}
          </button>
        ))}
      </div>

      {tab === "cases" && (
        <>
          <section className="ng-card ng-case-filters">
            <label className="ng-label">Search cases</label>
            <input
              className="ng-input"
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Search cases, targets, mechanisms…"
            />
            <div className="ng-sample-row" style={{ marginTop: 10 }}>
              <span className="ng-muted">Sort</span>
              <button type="button" className={`ng-chip ${sort === "newest" ? "active" : ""}`} onClick={() => setSort("newest")}>
                Newest first
              </button>
              <button type="button" className={`ng-chip ${sort === "oldest" ? "active" : ""}`} onClick={() => setSort("oldest")}>
                Oldest first
              </button>
            </div>
            <div className="ng-sample-row" style={{ marginTop: 8 }}>
              <span className="ng-muted">Category</span>
              <button type="button" className={`ng-chip ${cat === "all" ? "active" : ""}`} onClick={() => setCat("all")}>
                All
              </button>
              {Object.entries(CATEGORY_NAMES).map(([id, name]) => (
                <button key={id} type="button" className={`ng-chip ${cat === id ? "active" : ""}`} onClick={() => setCat(id)}>
                  {name}
                </button>
              ))}
            </div>
            <div className="ng-sample-row" style={{ marginTop: 8 }}>
              <span className="ng-muted">Authority</span>
              <button type="button" className={`ng-chip ${auth === "all" ? "active" : ""}`} onClick={() => setAuth("all")}>
                All
              </button>
              {authorities.map((a) => (
                <button key={a} type="button" className={`ng-chip ${auth === a ? "active" : ""}`} onClick={() => setAuth(a)}>
                  {a}
                </button>
              ))}
            </div>
          </section>

          <p className="ng-muted" style={{ margin: "12px 0" }}>
            {caseList.length} of {THREAT_CASES.length} historical cases
          </p>

          <div className="ng-case-grid">
            {caseList.map((c) => {
              const isOpen = open === c.id;
              const authority = authorityOf(c.sourceOrg);
              return (
                <article key={c.id} className={`ng-card ng-case ${isOpen ? "open" : ""}`}>
                  <button type="button" className="ng-case-head" onClick={() => setOpen(isOpen ? null : c.id)}>
                    <div>
                      <div className="ng-case-meta-row">
                        <span className="ng-case-label">{c.label}</span>
                        <span className="ng-case-cat">{categoryName(c.threatType)}</span>
                        <time className="ng-muted">{c.date}</time>
                      </div>
                      <h3>{c.name}</h3>
                      <p className="ng-muted">Affected: {c.target}</p>
                    </div>
                    <span className="ng-case-chevron">{isOpen ? "−" : "+"}</span>
                  </button>
                  <p className="ng-case-preview">{c.mechanism}</p>
                  <div className="ng-case-foot">
                    <span>{authority}</span>
                    <span>{c.indicators.length} indicators</span>
                    <span>{1 + (c.supportingUrls?.length || 0)} source{(1 + (c.supportingUrls?.length || 0)) === 1 ? "" : "s"}</span>
                    <span>re-checked {c.sourceAudit?.checkedOn}</span>
                  </div>
                  {isOpen && (
                    <div className="ng-case-body">
                      <h4>Indicators (defanged — not clickable)</h4>
                      <ul>
                        {c.indicators.map((i) => (
                          <li key={i}>
                            <code>{i}</code>
                          </li>
                        ))}
                      </ul>
                      <h4>Victim journey</h4>
                      <ol>
                        {(c.victimJourney || []).map((step) => (
                          <li key={step}>{step}</li>
                        ))}
                      </ol>
                      <h4>Why it matters</h4>
                      <p>{c.whyItMatters}</p>
                      <h4>SafeNaija analysis</h4>
                      <p>{c.safeNaijaAnalysis}</p>
                      <h4>Official response</h4>
                      <p>{c.response}</p>
                      {c.sourceAudit?.notes && (
                        <>
                          <h4>Source audit</h4>
                          <p className="ng-muted">{c.sourceAudit.notes}</p>
                        </>
                      )}
                      <div className="ng-btn-row" style={{ marginTop: 10 }}>
                        <a className="sim-run-btn" href={c.sourceUrl} target="_blank" rel="noreferrer">
                          Primary source →
                        </a>
                        {(c.supportingUrls || []).map((u) => (
                          <a key={u} className="ng-btn-ghost" href={u} target="_blank" rel="noreferrer">
                            Supporting →
                          </a>
                        ))}
                      </div>
                    </div>
                  )}
                </article>
              );
            })}
          </div>
        </>
      )}

      {tab === "samples" && (
        <>
          <header className="safeo-page-header" style={{ marginBottom: 8 }}>
            <h3>Demo &amp; evaluation samples</h3>
            <p className="ng-muted">
              Samples labelled <strong>SYNTHETIC DEMO</strong> are not real incidents (phones use +234000…).{" "}
              <strong>HISTORICAL CASE</strong> reconstructs a documented case — indicator real, wording illustrative.
            </p>
          </header>
          <div className="ng-sample-row">
            <span className="ng-muted">Expected verdict</span>
            {["all", "CRITICAL", "HIGH", "MODERATE", "LOW"].map((s) => (
              <button key={s} type="button" className={`ng-chip ${sev === s ? "active" : ""}`} onClick={() => setSev(s)}>
                {s === "all" ? "All" : s}
              </button>
            ))}
          </div>
          <div className="ng-sample-row">
            <span className="ng-muted">Input</span>
            {["all", "text", "url", "email"].map((k) => (
              <button key={k} type="button" className={`ng-chip ${kind === k ? "active" : ""}`} onClick={() => setKind(k)}>
                {k === "all" ? "All" : KIND_LABEL[k] || k}
              </button>
            ))}
          </div>
          <p className="ng-muted" style={{ margin: "12px 0" }}>
            {sampleList.length} of {DEMO_SAMPLES.length} samples
          </p>
          <div className="ng-case-grid">
            {sampleList.map((s) => (
              <article key={s.id} className="ng-card ng-sample-card">
                <div className="ng-case-meta-row">
                  <span className={`ng-case-label ${s.label === "SYNTHETIC DEMO" ? "ng-case-label-demo" : ""}`}>
                    {s.label}
                  </span>
                  <span className="ng-case-cat">{KIND_LABEL[s.kind] || s.kind}</span>
                  <span className={`ng-sev ng-sev-${EXPECTED_SEV[s.expected]}`}>{EXPECTED_SEV[s.expected]}</span>
                </div>
                <h3>{s.title}</h3>
                <p className="ng-muted">{s.note}</p>
                {s.basedOn && <p className="ng-muted">Based on: {s.basedOn}</p>}
                {s.kind !== "screenshot" && (
                  <button type="button" className="sim-run-btn" style={{ marginTop: 10 }} onClick={() => analyzeSample(s)}>
                    Analyze this sample →
                  </button>
                )}
              </article>
            ))}
          </div>
        </>
      )}

      {tab === "sources" && (
        <>
          <header className="safeo-page-header" style={{ marginBottom: 8 }}>
            <h3>Research source registry</h3>
            <p className="ng-muted">Every external source used to build rules, cases and constraints.</p>
          </header>
          <div className="ng-table-wrap">
            <table className="ng-table">
              <thead>
                <tr>
                  <th>Organisation</th>
                  <th>Title</th>
                  <th>Date</th>
                  <th>Used for</th>
                  <th>Link</th>
                </tr>
              </thead>
              <tbody>
                {SOURCE_REGISTRY.map((r) => (
                  <tr key={`${r.org}-${r.title}`}>
                    <td>{r.org}</td>
                    <td>{r.title}</td>
                    <td>{r.date}</td>
                    <td>{r.usedFor}</td>
                    <td>
                      <a href={r.url} target="_blank" rel="noreferrer">
                        Open →
                      </a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {tab === "entities" && (
        <div className="ng-grid-2">
          {TRUSTED_ENTITIES.map((e) => (
            <section key={e.short} className="ng-card">
              <h3>
                {e.short} — {e.name}
              </h3>
              <p className="ng-muted">{e.note}</p>
              <ul>
                {e.domains.map((d) => (
                  <li key={d}>
                    <code>{d}</code>
                  </li>
                ))}
              </ul>
            </section>
          ))}
          <p className="ng-muted" style={{ gridColumn: "1 / -1" }}>
            Hackathon prototype — risk assessment, not a guarantee. Not endorsed by NCC, CBN, SEC or any agency named
            in the registry.{" "}
            <Link to="/messages">Analyze a message →</Link>
          </p>
        </div>
      )}
    </div>
  );
}
