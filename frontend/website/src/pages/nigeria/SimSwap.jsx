import { useEffect, useState } from "react";
import DecisionBadge from "../../components/DecisionBadge";
import {
  nigeriaAttackCatalog,
  nigeriaOffline,
  simSwapOsint,
  simSwapRisk,
  simulateAlerts,
  simulateAttack,
} from "../../nigeriaApi";

const FLAGS = [
  ["phone_public_on_social", "Phone number public on social media"],
  ["nin_or_bvn_shared_before", "Shared NIN/BVN outside official channels before"],
  ["email_breached_known", "Email known from a breach (self-reported)"],
  ["reused_passwords", "Reuse passwords across bank / email / social"],
  ["no_bank_transaction_alerts", "No bank transaction alerts"],
  ["dual_sim_unknown_apps", "Unknown apps with SMS permission"],
  ["recent_sim_issues", "Recent unexpected SIM / network loss"],
  ["public_home_address", "Home address easy to find publicly"],
];

/**
 * SIM Swap lab = risk OSINT + alert simulation + attack demos.
 * (Attack simulation is the same threat-lab surface, not a separate product.)
 */
export default function SimSwap() {
  const [tab, setTab] = useState("osint"); // osint | alerts | attacks
  const [name, setName] = useState("Adaobi Okonkwo");
  const [phone, setPhone] = useState("+2348012345678");
  const [city, setCity] = useState("Lagos");
  const [flags, setFlags] = useState({
    phone_public_on_social: true,
    nin_or_bvn_shared_before: false,
    reused_passwords: true,
    no_bank_transaction_alerts: true,
  });
  const [risk, setRisk] = useState(null);
  const [osint, setOsint] = useState(null);
  const [alert, setAlert] = useState(null);
  const [scenario, setScenario] = useState("sim_swap");
  const [catalog, setCatalog] = useState([]);
  const [attack, setAttack] = useState("sim_swap");
  const [attackResult, setAttackResult] = useState(null);
  const [offline, setOffline] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [termLines, setTermLines] = useState([]);

  useEffect(() => {
    nigeriaAttackCatalog().then((d) => setCatalog(d.attacks || [])).catch(() => {});
    nigeriaOffline().then(setOffline).catch(() => {});
  }, []);

  function toggle(key) {
    setFlags((f) => ({ ...f, [key]: !f[key] }));
  }

  async function runOsintAndRisk() {
    setBusy(true);
    setError("");
    setTermLines([{ t: "…", line: "$ starting Google OSINT…" }]);
    try {
      const live = await simSwapOsint({ full_name: name, phone, city });
      setOsint(live);
      // animate terminal lines
      const lines = live.terminal || [];
      setTermLines([]);
      for (let i = 0; i < lines.length; i++) {
        await new Promise((r) => setTimeout(r, 120));
        setTermLines((prev) => [...prev, lines[i]]);
      }
      const full = await simSwapRisk({
        ...flags,
        full_name: name,
        phone,
        city,
        run_google_search: true,
      });
      setRisk(full);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  async function runAlert() {
    setAlert(await simulateAlerts(scenario));
  }

  async function runAttack() {
    setBusy(true);
    try {
      setAttackResult(await simulateAttack(attack));
    } finally {
      setBusy(false);
    }
  }

  const detection = attackResult?.detection;
  const topDecision =
    detection?.decision ||
    detection?.message?.decision ||
    detection?.github?.decision ||
    detection?.secret_snippet?.decision;
  const topScore =
    detection?.risk_score ||
    detection?.message?.risk_score ||
    detection?.github?.risk_score ||
    detection?.secret_snippet?.risk_score;

  return (
    <div className="ng-page">
      <header className="safeo-page-header">
        <h2>SIM Swap Risk, Alerts &amp; Attack Lab</h2>
        <p>
          Same lab: Google-search a person, evaluate SIM-swap exposure in a live terminal, simulate
          takeover alerts, and replay common attacks (phishing / SIM swap / fake loan) on dummy data.
        </p>
      </header>

      <div className="ng-sample-row">
        <button type="button" className={`ng-chip ${tab === "osint" ? "active" : ""}`} onClick={() => setTab("osint")}>
          Google OSINT + risk
        </button>
        <button type="button" className={`ng-chip ${tab === "alerts" ? "active" : ""}`} onClick={() => setTab("alerts")}>
          Alert simulation
        </button>
        <button type="button" className={`ng-chip ${tab === "attacks" ? "active" : ""}`} onClick={() => setTab("attacks")}>
          Attack simulation
        </button>
      </div>

      {tab === "osint" && (
        <div className="ng-grid-2">
          <section className="ng-card">
            <h3>Search this person on Google</h3>
            <label className="ng-label">Full name</label>
            <input className="ng-input" value={name} onChange={(e) => setName(e.target.value)} />
            <label className="ng-label">Phone</label>
            <input className="ng-input" value={phone} onChange={(e) => setPhone(e.target.value)} />
            <label className="ng-label">City</label>
            <input className="ng-input" value={city} onChange={(e) => setCity(e.target.value)} />
            <h4 style={{ marginTop: 14 }}>Extra self-reported signals</h4>
            {FLAGS.map(([key, label]) => (
              <label key={key} className="ng-check">
                <input type="checkbox" checked={!!flags[key]} onChange={() => toggle(key)} />
                {label}
              </label>
            ))}
            <button className="sim-run-btn" type="button" disabled={busy} onClick={runOsintAndRisk}>
              {busy ? "Searching Google…" : "Run Google search + evaluate"}
            </button>
            {error && <p className="ng-error">{error}</p>}
            {osint?.google_url && (
              <p style={{ marginTop: 10 }}>
                <a className="ng-ext" href={osint.google_url} target="_blank" rel="noreferrer">
                  Open the same query on Google →
                </a>
              </p>
            )}
          </section>

          <section className="ng-card">
            <h3>Terminal</h3>
            <div className="ng-terminal">
              <div className="ng-terminal-bar">safenaija — osint@nigeria</div>
              <div className="ng-terminal-body">
                {termLines.length === 0 && <div className="dim">Waiting to search…</div>}
                {termLines.map((row, i) => (
                  <div key={i} className="ng-term-line">
                    <span className="ts">{row.t}</span> {row.line}
                  </div>
                ))}
              </div>
            </div>

            {osint?.results?.length > 0 && (
              <div className="ng-search-hits">
                <h4>Public search hits</h4>
                {osint.results.map((r, i) => (
                  <a key={i} className="ng-hit" href={r.url} target="_blank" rel="noreferrer">
                    <strong>{r.title}</strong>
                    <span>{r.snippet}</span>
                  </a>
                ))}
              </div>
            )}

            {risk && (
              <div className="ng-result">
                <DecisionBadge decision={risk.decision} score={risk.risk_score} />
                <p>{risk.advice}</p>
                <ul>
                  {(risk.factors || []).map((f) => (
                    <li key={f.label}>
                      {f.label} <span className="ng-muted">(+{f.weight} · {f.group})</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </section>
        </div>
      )}

      {tab === "alerts" && (
        <section className="ng-card">
          <h3>SIM / bank account alert simulation</h3>
          <select className="ng-input" value={scenario} onChange={(e) => setScenario(e.target.value)}>
            <option value="sim_swap">Suspicious SIM change</option>
            <option value="bank_account_change">Bank account detail change</option>
          </select>
          <button className="sim-run-btn" type="button" onClick={runAlert}>
            Simulate alert flow
          </button>
          {alert && (
            <div className="ng-result">
              <h4>{alert.title}</h4>
              <div className="ng-alert-banner">{alert.user_alert}</div>
              <div className="ng-terminal">
                <div className="ng-terminal-bar">alert timeline</div>
                <div className="ng-terminal-body">
                  {(alert.timeline || []).map((t) => (
                    <div key={t.t} className="ng-term-line">
                      <span className="ts">{t.t}</span> {t.event}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </section>
      )}

      {tab === "attacks" && (
        <div className="ng-grid-2">
          <section className="ng-card">
            <h3>Attack simulation (dummy data)</h3>
            <p className="ng-muted">Same engine as SIM-swap demos — phishing, loan apps, secret leaks.</p>
            <select className="ng-input" value={attack} onChange={(e) => setAttack(e.target.value)}>
              {catalog.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.label}
                </option>
              ))}
            </select>
            <button className="sim-run-btn" type="button" disabled={busy} onClick={runAttack}>
              {busy ? "Running…" : "Simulate attack"}
            </button>
            {attackResult && (
              <div className="ng-result">
                <h4>{attackResult.name}</h4>
                <DecisionBadge decision={topDecision} score={topScore} />
                <pre className="ng-pre">{attackResult.dummy_payload?.dummy_message || attackResult.dummy_payload?.extra}</pre>
                <ul>
                  {(attackResult.explained || []).map((e) => (
                    <li key={e}>{e}</li>
                  ))}
                </ul>
              </div>
            )}
          </section>
          <section className="ng-card">
            <h3>Offline capability</h3>
            {offline ? (
              <>
                <p>
                  Offline ready: <strong>{offline.offline_ready ? "Yes" : "No"}</strong>
                </p>
                <ul>
                  {(offline.capabilities_without_network || []).map((c) => (
                    <li key={c}>{c}</li>
                  ))}
                </ul>
              </>
            ) : (
              <p className="ng-muted">Load backend to see offline status.</p>
            )}
          </section>
        </div>
      )}
    </div>
  );
}
