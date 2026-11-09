import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import DecisionBadge from "../../components/DecisionBadge";
import TrustChain, { buildTrustChain } from "../../components/TrustChain";
import {
  connectGmailImap,
  connectInstagram,
  connectWhatsApp,
  disconnectChannel,
  gmailOauthStart,
  nigeriaChannels,
  scanInbox,
  scanMessage,
} from "../../nigeriaApi";

const SAMPLES = [
  {
    label: "OTP theft (Pidgin)",
    channel: "whatsapp",
    text: "Abeg send the OTP sharp sharp before dem block your GTBank account",
  },
  {
    label: "Investment scam",
    channel: "instagram",
    text: "Join NaijaCrypto Doubler VIP — guaranteed 40% weekly returns. Send USDT now.",
  },
  {
    label: "Fake loan SMS",
    channel: "gmail",
    text: "Your loan is approved. Download this loan app and allow contacts permission.",
  },
];

export default function MessageScan() {
  const location = useLocation();
  const [text, setText] = useState(SAMPLES[0].text);
  const [channel, setChannel] = useState("manual");
  const [channels, setChannels] = useState([]);
  const [result, setResult] = useState(null);
  const [inboxScans, setInboxScans] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [panel, setPanel] = useState(null); // whatsapp | gmail | instagram
  const [waId, setWaId] = useState("");
  const [waToken, setWaToken] = useState("");
  const [gmailEmail, setGmailEmail] = useState("giamatteo69@gmail.com");
  const [gmailPass, setGmailPass] = useState("");
  const [igToken, setIgToken] = useState("");
  const [statusMsg, setStatusMsg] = useState("");
  const [emailMode, setEmailMode] = useState(false);
  const [emailFrom, setEmailFrom] = useState("");
  const [emailSubject, setEmailSubject] = useState("");

  async function refreshChannels() {
    const d = await nigeriaChannels();
    setChannels(d.supported || []);
  }

  useEffect(() => {
    refreshChannels().catch(() => {});
  }, []);

  // Case Library → Analyze this sample
  useEffect(() => {
    const sample = location.state?.sampleText;
    if (!sample) return;
    setText(sample);
    if (location.state?.sampleChannel) setChannel(location.state.sampleChannel);
    setStatusMsg(`Loaded case-library sample: ${location.state?.sampleTitle || "demo"}`);
    setResult(null);
  }, [location.state]);

  async function runScan() {
    setBusy(true);
    setError("");
    try {
      const payload =
        emailMode || channel === "gmail"
          ? [
              emailFrom ? `From: ${emailFrom}` : "",
              emailSubject ? `Subject: ${emailSubject}` : "",
              "",
              text,
            ]
              .filter((line, i, arr) => !(line === "" && arr[i - 1] === ""))
              .join("\n")
              .trim()
          : text;
      setResult(await scanMessage(payload, emailMode ? "gmail" : channel));
      setInboxScans(null);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  async function connectWA() {
    setBusy(true);
    setError("");
    try {
      const r = await connectWhatsApp(waId, waToken);
      if (!r.ok) throw new Error(r.error || "WhatsApp connect failed");
      setStatusMsg(`WhatsApp connected: ${r.account_hint}. Webhook path ${r.webhook_path}`);
      setPanel(null);
      await refreshChannels();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  async function connectGmailOAuth() {
    setBusy(true);
    setError("");
    try {
      const r = await gmailOauthStart();
      if (r.auth_url) {
        window.location.href = r.auth_url;
        return;
      }
      throw new Error(r.error || "OAuth not configured — use App Password below");
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  async function connectGmailApp() {
    setBusy(true);
    setError("");
    try {
      const r = await connectGmailImap(gmailEmail, gmailPass);
      if (!r.ok) throw new Error(r.error || "Gmail IMAP failed");
      setStatusMsg(`Gmail connected: ${r.account_hint} · ${r.count || 0} recent messages synced`);
      setPanel(null);
      await refreshChannels();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  async function connectIG() {
    setBusy(true);
    setError("");
    try {
      const r = await connectInstagram(igToken);
      if (!r.ok) throw new Error(r.error || "Instagram connect failed");
      setStatusMsg(`Instagram connected: ${r.account_hint}`);
      setPanel(null);
      await refreshChannels();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  async function scanConnected(id) {
    setBusy(true);
    setError("");
    try {
      const r = await scanInbox(id);
      setInboxScans(r);
      setResult(null);
      setStatusMsg(`Scanned ${r.count || 0} messages from ${id}`);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="ng-page">
      <header className="safeo-page-header">
        <h2>Message Scam Detection</h2>
        <p>
          Really connect WhatsApp (Meta Cloud API), Gmail (OAuth or App Password), or Instagram
          (Graph token). Nigerian language / Pidgin detection runs inside every scan — not a separate page.{" "}
          <Link to="/chat-demo">Open the WhatsApp / Instagram phone demo →</Link>
        </p>
      </header>

      <div className="ng-grid-2">
        <section className="ng-card">
          <h3>Live channels</h3>
          <div className="ng-channel-list">
            {channels
              .filter((c) => c.id !== "manual")
              .map((c) => (
                <div key={c.id} className="ng-channel-row">
                  <div>
                    <strong>{c.label}</strong>
                    <div className="ng-muted">
                      {c.connected
                        ? `Connected · ${c.account_hint}${c.message_count != null ? ` · ${c.message_count} msgs` : ""}`
                        : c.note}
                    </div>
                  </div>
                  <div className="ng-btn-row">
                    {c.connected ? (
                      <>
                        <button className="sim-run-btn" type="button" disabled={busy} onClick={() => scanConnected(c.id)}>
                          Scan inbox
                        </button>
                        <button
                          className="ng-btn-ghost"
                          type="button"
                          onClick={async () => {
                            await disconnectChannel(c.id);
                            await refreshChannels();
                          }}
                        >
                          Disconnect
                        </button>
                      </>
                    ) : (
                      <button className="sim-run-btn" type="button" onClick={() => setPanel(c.id)}>
                        Connect
                      </button>
                    )}
                  </div>
                </div>
              ))}
          </div>
          {statusMsg && <p className="ng-ok">{statusMsg}</p>}
          {error && <p className="ng-error">{error}</p>}

          {panel === "whatsapp" && (
            <div className="ng-connect-form">
              <h4>Connect WhatsApp Cloud API</h4>
              <p className="ng-muted">From Meta Developer → WhatsApp → API Setup. Webhook URL must end with <code>/webhooks/whatsapp</code>.</p>
              <label className="ng-label">Phone number ID</label>
              <input className="ng-input" value={waId} onChange={(e) => setWaId(e.target.value)} placeholder="e.g. 1098…" />
              <label className="ng-label">Access token</label>
              <input className="ng-input" value={waToken} onChange={(e) => setWaToken(e.target.value)} placeholder="EAAG…" />
              <button className="sim-run-btn" type="button" disabled={busy} onClick={connectWA}>
                Verify &amp; connect
              </button>
            </div>
          )}

          {panel === "gmail" && (
            <div className="ng-connect-form">
              <h4>Connect Gmail</h4>
              <button className="sim-run-btn" type="button" disabled={busy} onClick={connectGmailOAuth}>
                Continue with Google OAuth
              </button>
              <p className="ng-muted" style={{ marginTop: 12 }}>
                Google rejects your normal login password for IMAP. Create an{" "}
                <strong>App Password</strong>: Google Account → Security → 2-Step Verification → App passwords
                → Mail / Mac → copy the 16-character code (spaces optional).
              </p>
              <label className="ng-label">Gmail address</label>
              <input className="ng-input" value={gmailEmail} onChange={(e) => setGmailEmail(e.target.value)} placeholder="you@gmail.com" />
              <label className="ng-label">App password (not your normal Gmail password)</label>
              <input className="ng-input" type="password" value={gmailPass} onChange={(e) => setGmailPass(e.target.value)} placeholder="xxxx xxxx xxxx xxxx" />
              <button className="sim-run-btn" type="button" disabled={busy} onClick={connectGmailApp}>
                Connect via IMAP
              </button>
            </div>
          )}

          {panel === "instagram" && (
            <div className="ng-connect-form">
              <h4>Connect Instagram</h4>
              <p className="ng-muted">Requires a Meta Graph access token for a professional IG account.</p>
              <label className="ng-label">Access token</label>
              <input className="ng-input" value={igToken} onChange={(e) => setIgToken(e.target.value)} />
              <button className="sim-run-btn" type="button" disabled={busy} onClick={connectIG}>
                Verify &amp; connect
              </button>
            </div>
          )}
        </section>

        <section className="ng-card">
          <h3>Manual / forward a message</h3>
          <label className="ng-label">Channel tag</label>
          <select
            value={channel}
            onChange={(e) => {
              setChannel(e.target.value);
              setEmailMode(e.target.value === "gmail");
            }}
            className="ng-input"
          >
            <option value="manual">Manual share</option>
            <option value="whatsapp">WhatsApp</option>
            <option value="gmail">Gmail / email</option>
            <option value="instagram">Instagram</option>
          </select>
          <label className="ng-check" style={{ marginTop: 10 }}>
            <input type="checkbox" checked={emailMode} onChange={(e) => setEmailMode(e.target.checked)} />
            Email fields (From / Subject / Body) — Trust Engine-style structured email check
          </label>
          {emailMode && (
            <>
              <label className="ng-label">From</label>
              <input
                className="ng-input"
                placeholder="Godwin Emefiele &lt;verify@cbn-secure.top&gt;"
                value={emailFrom}
                onChange={(e) => setEmailFrom(e.target.value)}
              />
              <label className="ng-label">Subject</label>
              <input
                className="ng-input"
                placeholder="Urgent: re-validate your BVN"
                value={emailSubject}
                onChange={(e) => setEmailSubject(e.target.value)}
              />
            </>
          )}
          <label className="ng-label">{emailMode ? "Body" : "Message"}</label>
          <textarea className="ng-input ng-textarea" rows={6} value={text} onChange={(e) => setText(e.target.value)} />
          <div className="ng-sample-row">
            {SAMPLES.map((s) => (
              <button
                key={s.label}
                type="button"
                className="ng-chip"
                onClick={() => {
                  setText(s.text);
                  setChannel(s.channel);
                  setEmailMode(s.channel === "gmail");
                  if (s.channel === "gmail") {
                    setEmailFrom("Loan Desk <approve@quickcash-ng.xyz>");
                    setEmailSubject("Your loan is approved");
                  }
                }}
              >
                {s.label}
              </button>
            ))}
            <button
              type="button"
              className="ng-chip"
              onClick={() => {
                setEmailMode(true);
                setChannel("gmail");
                setEmailFrom("CBN Alert <support@cbn-verify.top>");
                setEmailSubject("Re-validate BVN within 24 hours");
                setText(
                  "Dear customer, click https://cbn-verify.top/bvn to re-validate your BVN and OTP or your account will be restricted."
                );
              }}
            >
              CBN impersonation email
            </button>
          </div>
          <button className="sim-run-btn" type="button" disabled={busy} onClick={runScan}>
            {busy ? "Scanning…" : "Scan message"}
          </button>
        </section>
      </div>

      {result && (
        <section className="ng-card ng-result">
          <DecisionBadge decision={result.decision} score={result.risk_score} />
          <p>{result.advice}</p>
          <p className="ng-muted">
            Languages detected: {(result.language?.languages_detected || []).join(", ")} · primary{" "}
            <strong>{result.language?.primary_language}</strong> · channel {result.channel}
          </p>
          {result.findings?.length > 0 && (
            <ul>
              {result.findings.map((f, i) => (
                <li key={i}>
                  <strong>{f.category}</strong> ({f.severity}
                  {f.language ? ` · ${f.language}` : ""}) — {f.matched}
                </li>
              ))}
            </ul>
          )}
          <TrustChain steps={buildTrustChain(result, "message")} />
        </section>
      )}

      {inboxScans?.results?.length > 0 && (
        <section className="ng-card ng-result">
          <h3>Inbox scan results</h3>
          {inboxScans.results.map((row, i) => (
            <div key={i} className="ng-inbox-row">
              <DecisionBadge decision={row.scan.decision} score={row.scan.risk_score} />
              <div className="ng-muted">{row.message.from || row.message.subject}</div>
              <pre className="ng-pre small">{(row.message.text || "").slice(0, 280)}</pre>
              <p>{row.scan.advice}</p>
              <p className="ng-muted">Languages: {(row.scan.language?.languages_detected || []).join(", ")}</p>
            </div>
          ))}
        </section>
      )}
    </div>
  );
}
