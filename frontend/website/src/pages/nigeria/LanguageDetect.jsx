import { useState } from "react";
import { detectLanguage, scanMessage } from "../../nigeriaApi";

const SAMPLES = [
  "Abeg send the OTP sharp sharp",
  "Aika otp don tabbatar da bvn",
  "Fi otp ranse ki account re ma tipa",
  "Zipu koodu ahu — akauntu gi ga-emechi",
  "Guaranteed 300% returns this week",
];

export default function LanguageDetect() {
  const [text, setText] = useState(SAMPLES[0]);
  const [lang, setLang] = useState(null);
  const [scan, setScan] = useState(null);
  const [busy, setBusy] = useState(false);

  async function run() {
    setBusy(true);
    try {
      const [l, s] = await Promise.all([detectLanguage(text), scanMessage(text, "manual")]);
      setLang(l);
      setScan(s);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="ng-page">
      <header className="safeo-page-header">
        <h2>Nigerian Language Detection</h2>
        <p>
          Recognises scam phrasing in English, Pidgin, Hausa, Yoruba, and Igbo — including local
          expressions scammers actually use.
        </p>
      </header>

      <section className="ng-card">
        <textarea className="ng-input ng-textarea" rows={4} value={text} onChange={(e) => setText(e.target.value)} />
        <div className="ng-sample-row">
          {SAMPLES.map((s) => (
            <button key={s} type="button" className="ng-chip" onClick={() => setText(s)}>
              {s.slice(0, 28)}…
            </button>
          ))}
        </div>
        <button className="sim-run-btn" type="button" disabled={busy} onClick={run}>
          {busy ? "Detecting…" : "Detect language + scam risk"}
        </button>
      </section>

      {lang && (
        <section className="ng-card ng-result">
          <h3>Primary: {lang.primary_language}</h3>
          <p className="ng-muted">Detected: {(lang.languages_detected || []).join(", ")}</p>
          {Object.entries(lang.matched_phrases_by_language || {}).map(([k, phrases]) => (
            <div key={k}>
              <strong>{k}</strong>
              <ul>
                {phrases.map((p) => (
                  <li key={p}>{p}</li>
                ))}
              </ul>
            </div>
          ))}
          {scan && (
            <p>
              Linked scan decision: <strong>{scan.decision}</strong> — {scan.advice}
            </p>
          )}
        </section>
      )}
    </div>
  );
}
