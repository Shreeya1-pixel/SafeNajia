import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import DecisionBadge from "../../components/DecisionBadge";
import TrustChain, { buildTrustChain } from "../../components/TrustChain";
import { DEMO_SAMPLES, DEMO_SCREENSHOT_TRANSCRIPTS } from "../../data/demoSamples";
import { THREAT_CASES } from "../../data/threatCases";
import { EXPECTED_SEV, categoryName } from "../../data/caseTaxonomy";
import { SAMPLE_TO_CASE } from "../../data/caseAnalyzeLinks";
import { scanLink, scanMessage } from "../../nigeriaApi";

const LIMITS = { text: 20000, url: 2048, email: 100000 };
const MAX_BYTES = 3 * 1024 * 1024;
const IMAGE_TYPES = ["image/png", "image/jpeg", "image/webp"];

const MODES = [
  { kind: "text", label: "Message", hint: "SMS, WhatsApp, Telegram or social-media message" },
  { kind: "screenshot", label: "Screenshot", hint: "PNG, JPEG or WEBP · up to 3 MB (paste text if no OCR)" },
  { kind: "url", label: "URL", hint: "A link you were sent — analysed as data" },
  { kind: "email", label: "Email", hint: "Sender, subject, body and links" },
];

const fmtBytes = (n) =>
  n > 1024 * 1024 ? `${(n / 1024 / 1024).toFixed(1)} MB` : `${Math.max(1, Math.round(n / 1024))} KB`;

const defang = (s) => String(s || "").replace(/\./g, "[.]");

async function sha256Hex(buf) {
  const hash = await crypto.subtle.digest("SHA-256", buf);
  return [...new Uint8Array(hash)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

export default function Analyze() {
  const [params] = useSearchParams();
  const [kind, setKind] = useState("text");
  const [value, setValue] = useState("");
  const [sampleId, setSampleId] = useState(undefined);
  const [caseId, setCaseId] = useState(undefined);
  const [image, setImage] = useState(null);
  const [ocrText, setOcrText] = useState("");
  const [dragging, setDragging] = useState(false);
  const [emailMode, setEmailMode] = useState("fields");
  const [mail, setMail] = useState({ from: "", subject: "", body: "", links: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [resultKind, setResultKind] = useState("message");
  const resultRef = useRef(null);
  const fileRef = useRef(null);
  const autorunKey = useRef("");
  const valueRef = useRef("");
  const kindRef = useRef("text");
  const emailModeRef = useRef("fields");
  const mailRef = useRef(mail);
  const ocrRef = useRef("");
  const sampleIdRef = useRef(undefined);

  valueRef.current = value;
  kindRef.current = kind;
  emailModeRef.current = emailMode;
  mailRef.current = mail;
  ocrRef.current = ocrText;
  sampleIdRef.current = sampleId;

  const loadSample = useCallback((id, linkedCaseId) => {
    const s = DEMO_SAMPLES.find((x) => x.id === id);
    if (!s || s.kind === "screenshot") return false;
    setKind(s.kind);
    setValue(s.content);
    setSampleId(s.id);
    setCaseId(linkedCaseId || SAMPLE_TO_CASE[s.id] || undefined);
    setResult(null);
    setError(null);
    setImage(null);
    if (s.kind === "email") setEmailMode("raw");
    return true;
  }, []);

  const runWith = useCallback(async (opts) => {
    const k = opts.kind;
    const v = opts.value;
    const em = opts.emailMode;
    const m = opts.mail;
    const ocr = opts.ocrText;
    const sid = opts.sampleId;

    setError(null);
    let text = "";
    let scanKind = "message";
    try {
      if (k === "screenshot") {
        text = (ocr || "").trim();
        if (!text) {
          setError({
            title: "Need message text",
            message:
              "Localhost has no cloud OCR. Paste the screenshot text below, or use the demo WhatsApp screenshot transcript.",
          });
          return;
        }
        scanKind = "message";
      } else if (k === "url") {
        text = (v || "").trim();
        if (!text) {
          setError({ title: "Nothing to analyse", message: "Paste a link first." });
          return;
        }
        scanKind = "link";
      } else if (k === "email" && em === "fields") {
        if (!m.body.trim() && !m.subject.trim()) {
          setError({ title: "Nothing to analyse", message: "Add the email subject or body first." });
          return;
        }
        text = [
          m.from ? `From: ${m.from}` : "",
          m.subject ? `Subject: ${m.subject}` : "",
          "",
          m.body,
          m.links.trim() ? `\nLinks:\n${m.links.trim()}` : "",
        ]
          .filter(Boolean)
          .join("\n");
        scanKind = "message";
      } else {
        text = (v || "").trim();
        if (!text) {
          setError({ title: "Nothing to analyse", message: "Paste something to analyse first." });
          return;
        }
        scanKind = k === "url" ? "link" : "message";
      }

      setLoading(true);
      setResult(null);
      setTimeout(() => resultRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 30);

      let data;
      if (scanKind === "link") {
        data = await scanLink(text.startsWith("http") ? text : `https://${text}`, "");
        setResultKind("link");
      } else {
        data = await scanMessage(text, k === "email" ? "gmail" : sid ? "manual" : "manual");
        setResultKind("message");
      }
      setResult(data);
      setTimeout(() => resultRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 50);
    } catch (e) {
      setError({ title: "Analysis failed", message: e.message || String(e) });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const requestedSample = params.get("sample");
    const requestedCase = params.get("case") || undefined;
    const shouldAutorun = params.get("autorun") === "1";
    const key = `${requestedCase || ""}|${requestedSample || ""}|${shouldAutorun ? "1" : "0"}`;

    if (requestedCase && !requestedSample) {
      setCaseId(requestedCase);
    }

    if (requestedSample && DEMO_SAMPLES.some((s) => s.id === requestedSample && s.kind !== "screenshot")) {
      const s = DEMO_SAMPLES.find((x) => x.id === requestedSample);
      loadSample(requestedSample, requestedCase);
      if (shouldAutorun && autorunKey.current !== key && s) {
        autorunKey.current = key;
        // Defer so state from loadSample is applied via refs/content
        const content = s.content;
        const k = s.kind;
        setTimeout(() => {
          runWith({
            kind: k,
            value: content,
            emailMode: k === "email" ? "raw" : "fields",
            mail: { from: "", subject: "", body: "", links: "" },
            ocrText: "",
            sampleId: s.id,
          });
        }, 40);
      }
    } else if (requestedCase) {
      setCaseId(requestedCase);
    }
  }, [params, loadSample, runWith]);

  function switchKind(k) {
    if (k === kind) return;
    setKind(k);
    setResult(null);
    setError(null);
    setSampleId(undefined);
    setCaseId(undefined);
    setValue("");
    setImage(null);
    setOcrText("");
  }

  async function onFile(file) {
    setError(null);
    if (!file) return;
    if (!IMAGE_TYPES.includes(file.type)) {
      setError({ title: "Unsupported file", message: `“${file.name}” is not PNG, JPEG or WEBP.` });
      return;
    }
    if (file.size > MAX_BYTES) {
      setError({ title: "File too large", message: `Limit is 3 MB (got ${fmtBytes(file.size)}).` });
      return;
    }
    const buf = await file.arrayBuffer();
    const digest = await sha256Hex(buf);
    const cached = DEMO_SCREENSHOT_TRANSCRIPTS[digest];
    const reader = new FileReader();
    reader.onload = () => {
      const dataUrl = String(reader.result);
      const img = new window.Image();
      img.onload = () => {
        setImage({ dataUrl, name: file.name, size: file.size, w: img.naturalWidth, h: img.naturalHeight, digest });
        if (cached) {
          setOcrText(cached.text);
          setError(null);
        } else {
          setOcrText("");
        }
      };
      img.src = dataUrl;
    };
    reader.readAsDataURL(file);
    setResult(null);
  }

  async function useDemoScreenshot() {
    const first = Object.values(DEMO_SCREENSHOT_TRANSCRIPTS)[0];
    if (!first) return;
    setKind("screenshot");
    setImage({
      dataUrl: "",
      name: "demo-whatsapp-cbn.png",
      size: 0,
      demo: true,
      title: first.sampleTitle,
    });
    setOcrText(first.text);
    setSampleId(undefined);
    setCaseId(undefined);
    setResult(null);
    setError(null);
  }

  function run() {
    if (loading) return;
    runWith({
      kind: kindRef.current,
      value: valueRef.current,
      emailMode: emailModeRef.current,
      mail: mailRef.current,
      ocrText: ocrRef.current,
      sampleId: sampleIdRef.current,
    });
  }

  const samples = useMemo(() => DEMO_SAMPLES.filter((s) => s.showInPicker), []);
  const active = MODES.find((m) => m.kind === kind);
  const limit = kind === "url" ? LIMITS.url : kind === "email" ? LIMITS.email : LIMITS.text;
  const count =
    kind === "email" && emailMode === "fields" ? mail.body.length + mail.links.length : value.length;
  let urlHost = null;
  if (kind === "url" && value.trim()) {
    try {
      urlHost = new URL(/^[a-z][a-z0-9+.-]*:/i.test(value.trim()) ? value.trim() : `http://${value.trim()}`)
        .hostname;
    } catch {
      urlHost = null;
    }
  }
  const sample = sampleId ? DEMO_SAMPLES.find((s) => s.id === sampleId) : undefined;
  const linkedCase = caseId ? THREAT_CASES.find((c) => c.id === caseId) : undefined;
  const chain = result ? buildTrustChain(result, resultKind) : [];

  return (
    <div className="ng-page ng-analyze">
      <header className="safeo-page-header">
        <p className="ng-eyebrow">Investigation workspace</p>
        <h2>Analyze a threat</h2>
        <p>
          Paste a message, upload a screenshot, check a link or inspect an email. SafeNaija checks who is
          behind it, what it wants, where it leads — and tells you what to do next.
        </p>
      </header>

      {linkedCase && (
        <section className="ng-card ng-case-context" aria-label="Related case">
          <div className="ng-case-meta-row">
            <span className="ng-case-label">{linkedCase.label}</span>
            <span className="ng-case-cat">{categoryName(linkedCase.threatType)}</span>
            {sample && (
              <span className={`ng-sev ng-sev-${EXPECTED_SEV[sample.expected]}`}>
                Expected {EXPECTED_SEV[sample.expected]}
              </span>
            )}
          </div>
          <h3>From Case Library: {linkedCase.name}</h3>
          <p className="ng-muted">{linkedCase.mechanism}</p>
          {sample?.basedOn && <p className="ng-muted">Sample based on: {sample.basedOn}</p>}
          <div className="ng-btn-row" style={{ marginTop: 10 }}>
            <Link to={`/cases/${linkedCase.id}`} className="ng-btn-ghost">
              Open full case report →
            </Link>
            <Link to="/cases" className="ng-linkish" style={{ marginTop: 0 }}>
              All cases
            </Link>
          </div>
        </section>
      )}

      {!linkedCase && sample && (
        <section className="ng-card ng-case-context" aria-label="Loaded sample">
          <div className="ng-case-meta-row">
            <span className={`ng-case-label ${sample.label === "SYNTHETIC DEMO" ? "ng-case-label-demo" : ""}`}>
              {sample.label}
            </span>
            <span className={`ng-sev ng-sev-${EXPECTED_SEV[sample.expected]}`}>
              Expected {EXPECTED_SEV[sample.expected]}
            </span>
          </div>
          <h3>{sample.title}</h3>
          <p className="ng-muted">{sample.note}</p>
          {sample.basedOn && <p className="ng-muted">Based on: {sample.basedOn}</p>}
          <Link to="/cases" className="ng-linkish">
            Browse Case Library →
          </Link>
        </section>
      )}

      <div className="ng-analyze-grid">
        <section className="ng-card ng-analyze-main" aria-label="Input">
          <div className="ng-analyze-tabs" role="tablist" aria-label="Input type">
            {MODES.map((m) => (
              <button
                key={m.kind}
                type="button"
                role="tab"
                aria-selected={kind === m.kind}
                className={`ng-analyze-tab ${kind === m.kind ? "active" : ""}`}
                onClick={() => switchKind(m.kind)}
              >
                {m.label}
              </button>
            ))}
          </div>

          <p className="ng-muted" style={{ marginTop: 12 }}>
            {active.hint}
            {sample && (
              <span>
                {" "}
                · Example loaded: <strong>{sample.label}</strong>
              </span>
            )}
          </p>

          {kind === "screenshot" ? (
            <div className="ng-analyze-shot">
              <input
                ref={fileRef}
                type="file"
                accept={IMAGE_TYPES.join(",")}
                hidden
                onChange={(e) => {
                  onFile(e.target.files?.[0]);
                  e.target.value = "";
                }}
              />
              {image ? (
                <div className="ng-shot-preview">
                  {image.dataUrl ? (
                    <img src={image.dataUrl} alt="Screenshot preview" />
                  ) : (
                    <div className="ng-shot-placeholder">Demo transcript loaded (no PNG required)</div>
                  )}
                  <div>
                    <strong>{image.name || image.title}</strong>
                    <p className="ng-muted">
                      {image.size ? fmtBytes(image.size) : "demo"}
                      {image.w ? ` · ${image.w}×${image.h}px` : ""}
                    </p>
                    <div className="ng-btn-row" style={{ marginTop: 8 }}>
                      <button type="button" className="ng-btn-ghost" onClick={() => fileRef.current?.click()}>
                        Replace
                      </button>
                      <button
                        type="button"
                        className="ng-btn-ghost"
                        onClick={() => {
                          setImage(null);
                          setOcrText("");
                        }}
                      >
                        Remove
                      </button>
                    </div>
                  </div>
                </div>
              ) : (
                <label
                  className={`ng-dropzone ${dragging ? "dragging" : ""}`}
                  onDragOver={(e) => {
                    e.preventDefault();
                    setDragging(true);
                  }}
                  onDragLeave={() => setDragging(false)}
                  onDrop={(e) => {
                    e.preventDefault();
                    setDragging(false);
                    onFile(e.dataTransfer.files?.[0]);
                  }}
                >
                  <span>{dragging ? "Drop to add the screenshot" : "Drag & drop a screenshot, or click to browse"}</span>
                  <small>PNG, JPEG or WEBP · max 3 MB · analysed in memory</small>
                  <button type="button" className="sim-run-btn" onClick={() => fileRef.current?.click()}>
                    Browse…
                  </button>
                </label>
              )}
              <button type="button" className="ng-linkish" onClick={useDemoScreenshot}>
                Use the demo WhatsApp screenshot transcript (SYNTHETIC DEMO)
              </button>
              <label className="ng-label" style={{ marginTop: 12 }}>
                Text from screenshot (required on localhost)
              </label>
              <textarea
                className="ng-input ng-textarea"
                rows={6}
                value={ocrText}
                onChange={(e) => setOcrText(e.target.value)}
                placeholder="Paste or type the message text visible in the screenshot…"
              />
            </div>
          ) : kind === "url" ? (
            <div>
              <label className="ng-label">Suspicious link</label>
              <input
                className="ng-input"
                value={value}
                onChange={(e) => {
                  setValue(e.target.value);
                  setSampleId(undefined);
                  setCaseId(undefined);
                }}
                placeholder="https://…"
                maxLength={LIMITS.url}
              />
              {urlHost && (
                <p className="ng-muted" style={{ marginTop: 6 }}>
                  Host to inspect: <code>{defang(urlHost)}</code>
                </p>
              )}
              <p className="ng-callout">Analysed as data — SafeNaija inspects structure &amp; scam cues without you visiting the site.</p>
            </div>
          ) : kind === "email" && emailMode === "fields" ? (
            <div className="ng-email-fields">
              <div className="ng-grid-2">
                <div>
                  <label className="ng-label">Sender</label>
                  <input
                    className="ng-input"
                    value={mail.from}
                    onChange={(e) => setMail({ ...mail, from: e.target.value })}
                    placeholder="Access Bank &lt;alerts@example.com&gt;"
                  />
                </div>
                <div>
                  <label className="ng-label">Subject</label>
                  <input
                    className="ng-input"
                    value={mail.subject}
                    onChange={(e) => setMail({ ...mail, subject: e.target.value })}
                    placeholder="Urgent: verify your BVN"
                  />
                </div>
              </div>
              <label className="ng-label">Body</label>
              <textarea
                className="ng-input ng-textarea"
                rows={7}
                value={mail.body}
                onChange={(e) => setMail({ ...mail, body: e.target.value })}
                placeholder="Paste the email text…"
              />
              <label className="ng-label">Links in the email (optional)</label>
              <textarea
                className="ng-input ng-textarea"
                rows={2}
                value={mail.links}
                onChange={(e) => setMail({ ...mail, links: e.target.value })}
                placeholder="https://…"
              />
              <button
                type="button"
                className="ng-linkish"
                onClick={() => {
                  setEmailMode("raw");
                  setValue("");
                  setSampleId(undefined);
                  setCaseId(undefined);
                }}
              >
                Advanced: paste full email source
              </button>
            </div>
          ) : (
            <div>
              <label className="ng-label">{kind === "email" ? "Full email source" : "Message"}</label>
              <textarea
                className="ng-input ng-textarea"
                rows={kind === "email" ? 11 : 8}
                maxLength={limit}
                value={value}
                onChange={(e) => {
                  setValue(e.target.value);
                  setSampleId(undefined);
                  setCaseId(undefined);
                }}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
                    e.preventDefault();
                    run();
                  }
                }}
                placeholder={
                  kind === "email"
                    ? "From: …\nSubject: …\n\nEmail body…"
                    : "e.g. “Your account will be RESTRICTED. Re-validate your BVN now: …”"
                }
              />
              {kind === "email" && (
                <button type="button" className="ng-linkish" onClick={() => setEmailMode("fields")}>
                  Use sender / subject / body fields instead
                </button>
              )}
            </div>
          )}

          {error && (
            <div className="ng-error-box" role="alert">
              <strong>{error.title}</strong>
              <p>{error.message}</p>
            </div>
          )}

          <div className="ng-analyze-actions">
            <button type="button" className="sim-run-btn" disabled={loading} onClick={run}>
              {loading ? "Analyzing…" : `Analyze ${active.label.toLowerCase()} →`}
            </button>
            {kind !== "screenshot" && (
              <span className="ng-muted">
                {count.toLocaleString()} / {limit.toLocaleString()} characters
              </span>
            )}
          </div>
        </section>

        <aside className="ng-analyze-side">
          <section className="ng-card">
            <h3 className="ng-eyebrow">Try an example</h3>
            <p className="ng-muted">Every example is labelled. Synthetic ones use fictional domains and numbers.</p>
            <ul className="ng-example-list">
              {samples.map((s) => (
                <li key={s.id}>
                  <button
                    type="button"
                    className={`ng-example-btn ${sampleId === s.id ? "active" : ""}`}
                    onClick={() => loadSample(s.id)}
                  >
                    <span>{s.title}</span>
                    {s.label === "HISTORICAL CASE" && <em className="ng-hist">HIST</em>}
                  </button>
                </li>
              ))}
            </ul>
          </section>
          <section className="ng-card">
            <h3>Privacy by design</h3>
            <ul className="ng-privacy-list">
              <li>Your full message is scored locally with phrase packs by default — not sent to an external LLM.</li>
              <li>Links are analysed as text; live fetch only happens for website mode when you ask.</li>
              <li>Screenshots stay in browser memory; localhost needs pasted text (or the demo transcript).</li>
            </ul>
            <Link to="/cases" className="ng-linkish">
              Open Threat Case Library →
            </Link>
          </section>
        </aside>
      </div>

      <div ref={resultRef} className="ng-analyze-report">
        {loading ? (
          <section className="ng-card">
            <h3>Investigation report</h3>
            <p className="ng-muted">Running SafeNaija engine…</p>
          </section>
        ) : result ? (
          <section className="ng-card ng-result">
            <h3>Investigation report</h3>
            {sample && (
              <p className="ng-muted" style={{ marginBottom: 8 }}>
                Sample: <strong>{sample.title}</strong>
                {linkedCase ? ` · Case: ${linkedCase.name}` : ""}
                {" · "}Expected {EXPECTED_SEV[sample.expected]}
              </p>
            )}
            <DecisionBadge decision={result.decision} score={result.risk_score} />
            <p>{result.advice}</p>
            {result.language && (
              <p className="ng-muted">
                Languages: {(result.language.languages_detected || []).join(", ") || "english"}
                {result.offline ? " · offline packs" : ""}
              </p>
            )}
            {result.findings?.length > 0 && (
              <>
                <h4>Evidence</h4>
                <ul>
                  {result.findings.map((f, i) => (
                    <li key={i}>
                      <strong>{f.category || f.type || "finding"}</strong>
                      {f.matched ? ` — ${f.matched}` : ""}
                      {f.label ? ` — ${f.label}` : ""}
                      {f.severity ? ` · ${f.severity}` : ""}
                    </li>
                  ))}
                </ul>
              </>
            )}
            {result.reasons?.length > 0 && (
              <>
                <h4>Reasons</h4>
                <ul>
                  {result.reasons.map((r, i) => (
                    <li key={i}>{r}</li>
                  ))}
                </ul>
              </>
            )}
            <TrustChain steps={chain} />
            <p className="ng-muted" style={{ marginTop: 12 }}>
              Recommended action:{" "}
              {result.decision === "BLOCK"
                ? "Stop — do not share OTP / PIN / BVN or click. Call your bank via the official app."
                : result.decision === "WARN"
                  ? "Be careful — verify on official .gov.ng / bank channels before acting."
                  : "Looks comparatively safe — still verify big payments independently."}
            </p>
            {linkedCase && (
              <Link to={`/cases/${linkedCase.id}`} className="ng-linkish">
                Back to case report →
              </Link>
            )}
          </section>
        ) : (
          <section className="ng-card ng-report-placeholder">
            <h3>Your report will appear here</h3>
            <p className="ng-muted">Investigation report</p>
            <ul>
              <li>SAFE / CAREFUL / DANGER with a risk score</li>
              <li>Who is behind it and where it leads</li>
              <li>Trust Chain: WHO → WHAT → WHERE → WHY → HOW → RESULT</li>
              <li>Evidence from Nigerian phrase packs / link visit / secrets</li>
              <li>A clear recommended action</li>
            </ul>
          </section>
        )}
      </div>
    </div>
  );
}
