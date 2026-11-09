/** Trust Chain — WHO → WHAT → WHERE → WHY → HOW → RESULT (feature from SafeNaija Trust Engine). */

const QUESTIONS = {
  WHO: "Who is behind it?",
  WHAT: "What does it want?",
  WHERE: "Where does it lead?",
  WHY: "Why is it suspicious?",
  HOW: "How does it manipulate?",
  RESULT: "Result",
};

function tone(status) {
  if (status === "danger") return "danger";
  if (status === "warn") return "warn";
  if (status === "ok") return "ok";
  return "neutral";
}

/**
 * Build a Trust Chain from any Nigeria scan result shape.
 * Keeps our existing ALLOW/WARN/BLOCK decisions — only adds explainability.
 */
export function buildTrustChain(result, kind = "message") {
  if (!result) return [];
  const decision = (result.decision || "ALLOW").toUpperCase();
  const score = typeof result.risk_score === "number" ? result.risk_score : null;
  const reasons = result.reasons || result.findings?.map((f) => f.label || f.matched || f.category) || [];
  const langs = result.language?.languages_detected || [];

  let who = "Unknown sender / unverified claim";
  let what = "Unclear ask";
  let where = "No destination checked";
  let why = reasons[0] || "No strong rule matched";
  let how = langs.length ? `Language cues: ${langs.join(", ")}` : "Social-engineering cues in the wording";

  if (kind === "message" || kind === "inbox") {
    who = result.channel ? `Channel: ${result.channel}` : "Pasted / forwarded message";
    const cats = (result.findings || []).map((f) => f.category).filter(Boolean);
    what = cats.length ? `Looks like: ${cats.slice(0, 3).join(", ")}` : result.advice || what;
    where = "Message body (no live browse)";
    how =
      (result.findings || []).some((f) => /otp|bvn|nin|pin/i.test(`${f.matched || ""} ${f.category || ""}`))
        ? "Pressure to share OTP / BVN / NIN / PIN"
        : how;
  } else if (kind === "link" || kind === "github") {
    who = result.owner ? `Repo ${result.owner}/${result.repo}` : result.host || result.kind || "Link / page";
    what =
      result.kind === "loan_app"
        ? "Push a loan-app / APK download"
        : result.kind === "github"
          ? "Public code may expose secrets"
          : "Click / invest / verify via this URL";
    where = result.visit?.final_url || result.host || (result.owner ? `github.com/${result.owner}/${result.repo}` : "URL");
    if (result.visit?.apk_links?.length) how = "Page links to APK / loan-app downloads";
    if (result.code_frames?.length) how = "Secrets / unsafe patterns visible in source";
    if (result.sec?.alert_matches?.length) why = `SEC alert match: ${result.sec.alert_matches[0].name}`;
  } else if (kind === "phone") {
    who = result.bank ? `Claimed bank: ${result.bank}` : "Caller / SMS number";
    what = result.match === "scam_list" ? "Reported scam number" : result.match === "bank_helpline" ? "Listed bank helpline" : "Unknown number";
    where = "Number check only — no call audio";
    why = result.note || reasons[0] || why;
    how = "Impersonation via caller ID / SMS sender spoofing";
  }

  const resultStatus = decision === "BLOCK" ? "danger" : decision === "WARN" ? "warn" : "ok";
  const resultValue =
    score != null
      ? `${decision} · risk ${score}${result.advice ? ` — ${result.advice}` : ""}`
      : `${decision}${result.advice ? ` — ${result.advice}` : ""}`;

  const stepStatus = (s) => {
    if (decision === "BLOCK") return s === "RESULT" ? "danger" : s === "WHY" || s === "HOW" ? "danger" : "warn";
    if (decision === "WARN") return s === "RESULT" ? "warn" : "warn";
    return s === "RESULT" ? "ok" : "neutral";
  };

  return [
    { key: "WHO", label: "Who", value: who, status: stepStatus("WHO") },
    { key: "WHAT", label: "What", value: what, status: stepStatus("WHAT") },
    { key: "WHERE", label: "Where", value: where, status: stepStatus("WHERE") },
    { key: "WHY", label: "Why", value: why, status: stepStatus("WHY") },
    { key: "HOW", label: "How", value: how, status: stepStatus("HOW") },
    { key: "RESULT", label: "Result", value: resultValue, status: resultStatus },
  ];
}

export default function TrustChain({ steps }) {
  if (!steps?.length) return null;
  return (
    <ol className="ng-trust-chain" aria-label="Trust Chain">
      {steps.map((s, i) => (
        <li key={s.key} className={`ng-trust-step ${tone(s.status)}`}>
          <div className="ng-trust-rail">
            <span className="ng-trust-dot">{i + 1}</span>
            {i < steps.length - 1 && <span className="ng-trust-line" aria-hidden />}
          </div>
          <div className="ng-trust-body">
            <div className="ng-trust-meta">
              <strong>{s.key}{s.key !== "RESULT" ? "?" : ""}</strong>
              <span className="ng-muted">{QUESTIONS[s.key]}</span>
            </div>
            <p>{s.value}</p>
          </div>
        </li>
      ))}
    </ol>
  );
}
