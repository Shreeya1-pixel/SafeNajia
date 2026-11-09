const { readFileSync } = require("node:fs");
const { join } = require("node:path");

const DATA = join(__dirname, "../../safenaija_pkg/nigeria/data");
const SEVERITY = { critical: 0.95, high: 0.8, medium: 0.55, low: 0.35 };

function loadJson(name) {
  return JSON.parse(readFileSync(join(DATA, name), "utf8"));
}

let PHRASES;
function phrases() {
  if (!PHRASES) PHRASES = loadJson("scam_phrases.json");
  return PHRASES;
}

function decision(score) {
  if (score >= 0.8) return "BLOCK";
  if (score >= 0.45) return "WARN";
  return "ALLOW";
}

function advice(category, lang = "english") {
  const map = {
    otp_theft: {
      english: "Do not share OTP/PIN. Hang up and call your bank via the official app.",
      pidgin: "No send OTP/PIN. Call your bank with the official app number.",
    },
    bank_impersonation: {
      english: "Banks will not ask for full details over SMS/WhatsApp. Verify on official channels.",
      pidgin: "Bank no dey ask full details for WhatsApp. Confirm for official channel.",
    },
    phishing: {
      english: "Do not click. Open your bank app yourself instead of following the link.",
      pidgin: "No click the link. Open your bank app yourself.",
    },
    crypto_scam: {
      english: "Guaranteed crypto returns are a scam. Do not send funds or share wallet seeds.",
      pidgin: "Guaranteed crypto return na scam. No send money.",
    },
  };
  const row = map[category] || {
    english: "Be careful — verify before you act.",
    pidgin: "Take care — verify before you act.",
  };
  return row[lang] || row.english;
}

function detectLang(text) {
  const t = (text || "").toLowerCase();
  const hits = [];
  if (/\b(abeg|wetin|dey|naf|una|oga)\b/.test(t)) hits.push("pidgin");
  if (!hits.length) hits.push("english");
  return { primary_language: hits[0], languages_detected: [...new Set(hits)] };
}

function scanMessage(text, channel = "manual", offline = true) {
  const findings = [];
  let score = 0.05;
  const blob = String(text || "");
  const lower = blob.toLowerCase();
  const pack = phrases();

  for (const [lang, rows] of Object.entries(pack)) {
    for (const row of rows || []) {
      const phrase = (row.phrase || "").toLowerCase();
      if (phrase && lower.includes(phrase)) {
        const sev = row.severity || "medium";
        findings.push({
          type: "phrase",
          language: lang,
          category: row.category || "scam",
          severity: sev,
          matched: row.phrase,
        });
        score = Math.max(score, SEVERITY[sev] || 0.5);
      }
    }
  }

  if (
    /\b(hdfc|gtbank|gtb|zenith|access bank|uba|first bank|opay|kuda|palmpay|stanbic|fidelity|ecobank|wema|alat|bank)\b/i.test(
      blob
    ) &&
    /(share|send|provide|confirm|update|submit).{0,40}(bank details|account details|account number|otp|pin|password|bvn|nin|card|cvv|atm)/i.test(
      blob
    )
  ) {
    findings.push({
      type: "bank_detail_request",
      language: "english",
      category: "bank_impersonation",
      severity: "critical",
      matched: "bank name + request for personal/bank details",
    });
    score = Math.max(score, 0.95);
  }

  if (
    /(guaranteed|risk[- ]?free).{0,40}(return|profit|roi)/i.test(blob) ||
    /(double|triple|10x).{0,30}(money|btc|usdt|crypto)/i.test(blob)
  ) {
    findings.push({
      type: "crypto_profit",
      category: "crypto_scam",
      severity: "critical",
      matched: "guaranteed profit / double money pattern",
    });
    score = Math.max(score, 0.95);
  }

  const urls = blob.match(/https?:\/\/[^\s<>"']+|www\.[^\s<>"']+/gi) || [];
  for (const url of urls.slice(0, 5)) {
    const link = scanLink(url, blob);
    if (link.decision !== "ALLOW") {
      findings.push({
        type: "embedded_link",
        category: "phishing",
        severity: link.decision === "BLOCK" ? "high" : "medium",
        matched: url,
        link_decision: link.decision,
      });
      score = Math.max(score, link.decision === "BLOCK" ? 0.85 : 0.55);
    }
  }

  const langInfo = detectLang(blob);
  const categories = [...new Set(findings.map((f) => f.category))];
  const primary = categories[0] || "benign";
  const dec = decision(score);
  const responseLang = langInfo.languages_detected.includes("pidgin") ? "pidgin" : "english";

  return {
    decision: dec,
    risk_score: Math.round(score * 1000) / 1000,
    channel,
    categories,
    findings,
    language: langInfo,
    advice:
      dec === "ALLOW"
        ? responseLang === "pidgin"
          ? "No strong scam signal for this message."
          : "No strong scam signals in this message."
        : advice(primary, responseLang),
    offline,
    privacy: "Message scored locally with phrase packs; not sent to external LLM.",
    deploy: "vercel-node",
  };
}

function scanLink(url, accompanying_text = "") {
  let score = 0.1;
  const reasons = [];
  let host = "";
  try {
    const u = new URL(/^https?:\/\//i.test(url) ? url : `http://${url}`);
    host = u.hostname.toLowerCase();
  } catch {
    reasons.push("Malformed URL");
    score = 0.7;
  }

  const suspicious = [".tk", ".ml", ".ga", ".cf", ".gq", ".xyz", ".top", ".buzz", ".icu"];
  if (suspicious.some((t) => host.endsWith(t))) {
    reasons.push(`Suspicious TLD on ${host}`);
    score = Math.max(score, 0.75);
  }
  const shorteners = ["bit.ly", "tinyurl.com", "t.co", "goo.gl", "cutt.ly", "rb.gy"];
  if (shorteners.includes(host)) {
    reasons.push("URL shortener");
    score = Math.max(score, 0.65);
  }
  if (/(login|verify|secure|update|account|bvn|otp)/i.test(url) && !/\.gov\.ng$|\.com\.ng$/.test(host)) {
    reasons.push("Credential / verify keywords on non-gov domain");
    score = Math.max(score, 0.7);
  }
  const findings = [];
  if (accompanying_text) {
    const msg = scanMessage(accompanying_text, "link", true);
    if (msg.decision !== "ALLOW") {
      score = Math.max(score, msg.risk_score);
      findings.push(...(msg.findings || []).slice(0, 5));
    }
  }

  const dec = decision(score);
  return {
    decision: dec,
    risk_score: Math.round(score * 1000) / 1000,
    url,
    host,
    reasons,
    findings,
    advice: dec === "ALLOW" ? "No strong link risk signals." : "Do not visit — open the official site or app yourself.",
    deploy: "vercel-node",
  };
}

function checkPhone(number) {
  const digits = String(number || "").replace(/\D/g, "");
  let norm = number;
  if (digits.startsWith("234") && digits.length >= 13) norm = "+234" + digits.slice(3, 13);
  else if (digits.startsWith("0") && digits.length === 11) norm = "+234" + digits.slice(1);
  return {
    decision: decision(0.2),
    risk_score: 0.2,
    number: norm,
    listed: false,
    advice: "No strong match in local scam number pack.",
  };
}

function health() {
  return {
    status: "healthy",
    service: "SafeNaija",
    country: "NG",
    deploy: "vercel-node",
    offline: { phrase_packs: Object.keys(phrases()), mode: "local" },
  };
}

module.exports = { scanMessage, scanLink, checkPhone, health, phrases, decision };
