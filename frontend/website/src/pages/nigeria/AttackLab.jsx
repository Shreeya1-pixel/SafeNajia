import { useEffect, useState } from "react";
import DecisionBadge from "../../components/DecisionBadge";
import { nigeriaAttackCatalog, nigeriaOffline, simulateAttack } from "../../nigeriaApi";

export default function AttackLab() {
  const [catalog, setCatalog] = useState([]);
  const [attack, setAttack] = useState("phishing");
  const [result, setResult] = useState(null);
  const [offline, setOffline] = useState(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    nigeriaAttackCatalog().then((d) => setCatalog(d.attacks || [])).catch(() => {});
    nigeriaOffline().then(setOffline).catch(() => {});
  }, []);

  async function run() {
    setBusy(true);
    try {
      setResult(await simulateAttack(attack));
    } finally {
      setBusy(false);
    }
  }

  const detection = result?.detection;
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
        <h2>Attack Simulation &amp; Offline Mode</h2>
        <p>
          Run phishing, SIM-swap, fake loan, and secret-leak demos on dummy data — then show how local
          patterns keep basic detection working offline.
        </p>
      </header>

      <div className="ng-grid-2">
        <section className="ng-card">
          <h3>7. Attack simulation</h3>
          <select className="ng-input" value={attack} onChange={(e) => setAttack(e.target.value)}>
            {catalog.map((a) => (
              <option key={a.id} value={a.id}>
                {a.label}
              </option>
            ))}
          </select>
          <button className="sim-run-btn" type="button" disabled={busy} onClick={run}>
            {busy ? "Running…" : "Simulate attack"}
          </button>
          {result && (
            <div className="ng-result">
              <h4>{result.name}</h4>
              <DecisionBadge decision={topDecision} score={topScore} />
              <pre className="ng-pre">{result.dummy_payload?.dummy_message || result.dummy_payload?.extra}</pre>
              <ul>
                {(result.explained || []).map((e) => (
                  <li key={e}>{e}</li>
                ))}
              </ul>
            </div>
          )}
        </section>

        <section className="ng-card">
          <h3>8. Offline capability</h3>
          {offline ? (
            <>
              <p>
                Offline ready: <strong>{offline.offline_ready ? "Yes" : "No"}</strong>
              </p>
              <h4>Works without sending messages to external servers</h4>
              <ul>
                {(offline.capabilities_without_network || []).map((c) => (
                  <li key={c}>{c}</li>
                ))}
              </ul>
              <h4>Local assets</h4>
              <ul>
                {(offline.local_assets || []).map((c) => (
                  <li key={c}>
                    <code>{c}</code>
                  </li>
                ))}
              </ul>
              <h4>Optional online upgrades</h4>
              <ul>
                {(offline.needs_network_optional || []).map((c) => (
                  <li key={c}>{c}</li>
                ))}
              </ul>
            </>
          ) : (
            <p className="ng-muted">Load backend to see offline status.</p>
          )}
        </section>
      </div>
    </div>
  );
}
