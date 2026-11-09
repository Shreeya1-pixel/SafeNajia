import { useState } from "react";
import DecisionBadge from "../../components/DecisionBadge";
import TrustChain, { buildTrustChain } from "../../components/TrustChain";
import { checkPhone } from "../../nigeriaApi";

const SAMPLES = [
  { label: "Reported scam", number: "+2348012345678" },
  { label: "OTP scammer", number: "08098765432" },
  { label: "Unknown", number: "+2348055512345" },
];

export default function FraudCall() {
  const [number, setNumber] = useState(SAMPLES[0].number);
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function run() {
    setBusy(true);
    setError("");
    try {
      setResult(await checkPhone(number));
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="ng-page">
      <header className="safeo-page-header">
        <h2>Fraud Call Detection</h2>
        <p>
          Checks numbers against verified Nigerian bank helplines and reported scam numbers.
          Does <strong>not</strong> listen to or record calls. Nigerian scam-phrase language packs
          still apply if you paste a call script on Messages.
        </p>
      </header>

      <section className="ng-card">
        <label className="ng-label">Phone number</label>
        <input className="ng-input" value={number} onChange={(e) => setNumber(e.target.value)} />
        <div className="ng-sample-row">
          {SAMPLES.map((s) => (
            <button key={s.label} type="button" className="ng-chip" onClick={() => setNumber(s.number)}>
              {s.label}
            </button>
          ))}
        </div>
        <button className="sim-run-btn" type="button" disabled={busy} onClick={run}>
          {busy ? "Checking…" : "Check number"}
        </button>
        {error && <p className="ng-error">{error}</p>}
      </section>

      {result && (
        <section className="ng-card ng-result">
          <DecisionBadge decision={result.decision} score={result.risk_score} />
          <p>{result.advice}</p>
          <p className="ng-muted">
            Match: {result.match}
            {result.bank ? ` · ${result.bank}` : ""}
            {result.reports ? ` · ${result.reports} reports` : ""}
          </p>
          {result.note && <p>{result.note}</p>}
          <TrustChain steps={buildTrustChain(result, "phone")} />
        </section>
      )}
    </div>
  );
}
