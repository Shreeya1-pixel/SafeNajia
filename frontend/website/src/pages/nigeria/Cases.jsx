import { useState } from "react";
import { THREAT_CASES, TRUSTED_ENTITIES } from "../../data/threatCases";

export default function Cases() {
  const [tab, setTab] = useState("cases");
  const [open, setOpen] = useState(THREAT_CASES[0]?.id || null);

  return (
    <div className="ng-page">
      <header className="safeo-page-header">
        <h2>Case Library &amp; Trust Intelligence</h2>
        <p>
          Documented Nigerian incidents (with sources) plus official domains SafeNaija checks against.
          Indicators are shown defanged — not as clickable scam links.
        </p>
      </header>

      <div className="ng-sample-row">
        <button type="button" className={`ng-chip ${tab === "cases" ? "active" : ""}`} onClick={() => setTab("cases")}>
          Historical cases
        </button>
        <button type="button" className={`ng-chip ${tab === "entities" ? "active" : ""}`} onClick={() => setTab("entities")}>
          Trusted entities
        </button>
      </div>

      {tab === "cases" && (
        <div className="ng-case-list">
          {THREAT_CASES.map((c) => {
            const isOpen = open === c.id;
            return (
              <article key={c.id} className={`ng-card ng-case ${isOpen ? "open" : ""}`}>
                <button type="button" className="ng-case-head" onClick={() => setOpen(isOpen ? null : c.id)}>
                  <div>
                    <span className="ng-case-label">{c.label}</span>
                    <h3>{c.name}</h3>
                    <p className="ng-muted">
                      {c.date} · {c.sourceOrg} · {c.threatType}
                    </p>
                  </div>
                  <span className="ng-case-chevron">{isOpen ? "−" : "+"}</span>
                </button>
                {isOpen && (
                  <div className="ng-case-body">
                    <p>{c.mechanism}</p>
                    <h4>Indicators (defanged)</h4>
                    <ul>
                      {c.indicators.map((i) => (
                        <li key={i}>
                          <code>{i}</code>
                        </li>
                      ))}
                    </ul>
                    <h4>Why it matters</h4>
                    <p>{c.whyItMatters}</p>
                    <h4>SafeNaija take</h4>
                    <p>{c.safeNaijaTake}</p>
                    <a href={c.sourceUrl} target="_blank" rel="noreferrer">
                      Source →
                    </a>
                  </div>
                )}
              </article>
            );
          })}
        </div>
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
        </div>
      )}
    </div>
  );
}
