import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import CodeFrame from "../../components/CodeFrame";
import DecisionBadge from "../../components/DecisionBadge";
import RiskPassport from "../../components/RiskPassport";
import TrustChain, { buildTrustChain } from "../../components/TrustChain";
import { scanGithub, scanLink } from "../../nigeriaApi";

export default function LinkScan() {
  const location = useLocation();
  const [url, setUrl] = useState("https://github.com/demo-student/naija-fintech-bot");
  const [extra, setExtra] = useState("Guaranteed 40% weekly returns. Send USDT to start.");
  const [mode, setMode] = useState("github");
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const sampleUrl = location.state?.sampleUrl;
    if (!sampleUrl) return;
    setMode("link");
    setUrl(sampleUrl);
    setExtra(location.state?.sampleTitle || "");
    setResult(null);
  }, [location.state]);

  async function run() {
    setBusy(true);
    setError("");
    try {
      const data = mode === "github" ? await scanGithub(url) : await scanLink(url, extra);
      setResult(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="ng-page">
      <header className="safeo-page-header">
        <h2>Link &amp; Crypto Scam Detection</h2>
        <p>
          Paste websites, GitHub repos, or crypto platforms. For risky repos we show a picture of the
          bad code (highlighted secrets). Language / Pidgin cues in ads are scored inside the same scan.
        </p>
      </header>

      <section className="ng-card">
        <div className="ng-sample-row">
          <button
            type="button"
            className={`ng-chip ${mode === "link" ? "active" : ""}`}
            onClick={() => {
              setMode("link");
              setUrl("https://naijacryptodoubler.xyz/earn");
              setExtra("Guaranteed 40% weekly returns. Send USDT to start.");
            }}
          >
            Website / crypto
          </button>
          <button
            type="button"
            className={`ng-chip ${mode === "github" ? "active" : ""}`}
            onClick={() => {
              setMode("github");
              setUrl("https://github.com/demo-student/naija-fintech-bot");
            }}
          >
            GitHub repo
          </button>
        </div>
        <label className="ng-label">URL</label>
        <input className="ng-input" value={url} onChange={(e) => setUrl(e.target.value)} />
        {mode === "link" && (
          <>
            <label className="ng-label">Accompanying text (ad / DM / email)</label>
            <textarea className="ng-input ng-textarea" rows={3} value={extra} onChange={(e) => setExtra(e.target.value)} />
          </>
        )}
        <button className="sim-run-btn" type="button" disabled={busy} onClick={run}>
          {busy ? "Checking…" : "Check safety"}
        </button>
        {error && <p className="ng-error">{error}</p>}
      </section>

      {result && (
        <section className="ng-card ng-result">
          <DecisionBadge decision={result.decision} score={result.risk_score} />
          <p>{result.advice}</p>
          <p className="ng-muted">
            Kind: {result.kind}
            {result.host ? ` · ${result.host}` : ""}
            {result.owner ? ` · ${result.owner}/${result.repo}` : ""}
            {result.fetch ? ` · ${result.fetch}` : ""}
          </p>
          <ul>
            {(result.reasons || []).map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ul>

          <TrustChain steps={buildTrustChain(result, mode === "github" ? "github" : "link")} />

          {result.risk_passport && <RiskPassport passport={result.risk_passport} />}

          {result.visit && (
            <div className="ng-visit">
              <h4>We visited this website</h4>
              <p className="ng-muted">
                {result.visit.fetched
                  ? `HTTP ${result.visit.status_code} · final URL ${result.visit.final_url}`
                  : `Fetch failed: ${result.visit.error || "unknown"}`}
              </p>
              {result.visit.title && (
                <p>
                  <strong>Title:</strong> {result.visit.title}
                </p>
              )}
              {result.visit.snippet && <pre className="ng-pre small">{result.visit.snippet}</pre>}
              <p className="ng-muted">
                Forms: {result.visit.forms ?? 0} · password fields: {result.visit.password_fields ?? 0}
                {result.visit.apk_links?.length ? ` · APK links: ${result.visit.apk_links.length}` : ""}
              </p>
            </div>
          )}

          {result.language?.languages_detected && (
            <p className="ng-muted">
              Languages on page/ad: {result.language.languages_detected.join(", ")}
            </p>
          )}

          {result.code_frames?.length > 0 && (
            <div className="ng-code-gallery">
              <h3>Picture of the bad code</h3>
              <p className="ng-muted">Highlighted lines are the secrets / unsafe patterns SafeNaija flagged.</p>
              {result.code_frames.map((frame) => (
                <CodeFrame key={frame.filename} frame={frame} />
              ))}
            </div>
          )}

          {result.sec && (
            <div className="ng-sec">
              <h4>Nigerian SEC check (demo pack)</h4>
              {result.sec.alert_matches?.length ? (
                <ul>
                  {result.sec.alert_matches.map((a) => (
                    <li key={a.name}>
                      <strong>{a.name}</strong> — {a.reason}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="ng-muted">No alert-name match in local pack.</p>
              )}
              <a href={result.sec.verify_url} target="_blank" rel="noreferrer">
                Verify on sec.gov.ng →
              </a>
            </div>
          )}
        </section>
      )}
    </div>
  );
}
