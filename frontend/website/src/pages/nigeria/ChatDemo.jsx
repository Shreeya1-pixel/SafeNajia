import { useState } from "react";
import { InstagramPhone, WhatsAppPhone } from "../../components/ChatPhones";
import DecisionBadge from "../../components/DecisionBadge";
import { scanMessage } from "../../nigeriaApi";

const WA_SCENARIOS = [
  {
    id: "hausa",
    label: "Hausa · OTP",
    lang: "Hausa",
    contact: "GTBank Support",
    inbound: "Sannu, wannan GTBank ne. Aika OTP da muka aiko maka yanzu — aika lambar sirri kafin mu rufe asusun ka.",
  },
  {
    id: "yoruba",
    label: "Yoruba · OTP",
    lang: "Yoruba",
    contact: "Access Bank Care",
    inbound: "E ku ijoko. Fi OTP ranse bayi. Fi koodu ranse ki account re ma tipa — bank ti ranṣẹ code naa.",
  },
  {
    id: "igbo",
    label: "Igbo · account",
    lang: "Igbo",
    contact: "UBA Helpdesk",
    inbound: "Ndewo. Zipu OTP anyị zigara gị ugbu a. Zipu koodu ahu — akauntu gi ga-emechi ma ị ghara.",
  },
  {
    id: "pidgin",
    label: "Pidgin · OTP",
    lang: "Pidgin",
    contact: "Zenith Fraud Desk",
    inbound: "Abeg send the OTP sharp sharp before dem block your GTBank account. No tell anybody the code.",
  },
  {
    id: "link",
    label: "English · phishing link",
    lang: "English",
    contact: "Opay Support",
    inbound: "Dear customer, click to unlock your account now: https://gtb-secure-login.xyz/verify",
  },
  {
    id: "clean",
    label: "Pidgin · clean",
    lang: "Pidgin",
    contact: "Ada (classmate)",
    inbound: "Abeg send me the lecture notes for CSC 201 when you reach hostel",
  },
];

const IG_SCENARIOS = [
  {
    id: "crypto",
    label: "Crypto VIP scam",
    contact: "naija_crypto_vip",
    inbound: "Join NaijaCrypto Doubler VIP — guaranteed 40% weekly returns. Send USDT now.",
  },
  {
    id: "loan",
    label: "Fake loan DM",
    contact: "quickcash_ng",
    inbound: "Your loan is approved. Download this loan app now now and allow contacts permission.",
  },
  {
    id: "romance",
    label: "Romance bait",
    contact: "ada_london_life",
    inbound: "I dey love you send small money for my visa. Western union for visa today.",
  },
];

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

export default function ChatDemo() {
  const [app, setApp] = useState("whatsapp"); // whatsapp | instagram
  const [scenarioId, setScenarioId] = useState("hausa");
  const [messages, setMessages] = useState([]);
  const [typing, setTyping] = useState(false);
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [custom, setCustom] = useState("");

  const scenarios = app === "whatsapp" ? WA_SCENARIOS : IG_SCENARIOS;
  const active = scenarios.find((s) => s.id === scenarioId) || scenarios[0];

  async function play(text, contact) {
    const inbound = (text || "").trim();
    if (!inbound || busy) return;
    setBusy(true);
    setResult(null);
    setMessages([]);
    setTyping(false);

    const t0 = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", hour12: false });
    const langHint = active?.lang && !custom.trim() ? active.lang : null;
    // Scammer / contact message arrives (Nigerian-language scam text shows in the bubble)
    setMessages([
      {
        id: "in-1",
        side: "in",
        text: inbound,
        time: t0,
        lang: langHint,
      },
    ]);
    await sleep(700);
    setTyping(true);
    await sleep(1100);

    try {
      const scan = await scanMessage(inbound, app);
      setTyping(false);
      const detected = (scan.language?.languages_detected || []).join(", ") || "english";
      const advice =
        scan.advice ||
        (scan.decision === "ALLOW"
          ? "Looks okay — still no OTP / money."
          : "No share OTP, PIN or BVN.");
      const botText =
        scan.decision === "BLOCK"
          ? `⛔ BLOCKED\nLanguage detected: ${detected}\n${advice}`
          : scan.decision === "WARN"
            ? `⚠️ Be careful\nLanguage detected: ${detected}\n${advice}`
            : `✅ Looks okay\nLanguage detected: ${detected}\n${advice}`;
      setMessages((prev) => [
        ...prev,
        {
          id: "bot-1",
          side: "bot",
          decision: scan.decision,
          text: botText,
          time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", hour12: false }),
        },
      ]);
      // Optional user "almost replied" bubble for drama on BLOCK
      if (scan.decision === "BLOCK") {
        await sleep(600);
        setMessages((prev) => [
          ...prev,
          {
            id: "out-draft",
            side: "out",
            text: "(you almost typed the OTP — SafeNaija stopped you)",
            time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", hour12: false }),
          },
        ]);
      }
      setResult(scan);
    } catch (e) {
      setTyping(false);
      setMessages((prev) => [
        ...prev,
        {
          id: "err",
          side: "bot",
          decision: "WARN",
          text: `Demo error: ${e.message}`,
        },
      ]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="ng-page">
      <header className="safeo-page-header">
        <h2>WhatsApp &amp; Instagram chat demo</h2>
        <p>
          Same idea as NABD’s phone preview: watch the scam land in a real chat UI, then see SafeNaija
          reply with ALLOW / WARN / BLOCK in plain language (including Pidgin).
        </p>
      </header>

      <div className="ng-sample-row">
        <button
          type="button"
          className={`ng-chip ${app === "whatsapp" ? "active" : ""}`}
          onClick={() => {
            setApp("whatsapp");
            setScenarioId("hausa");
            setMessages([]);
            setResult(null);
            setCustom("");
          }}
        >
          WhatsApp
        </button>
        <button
          type="button"
          className={`ng-chip ${app === "instagram" ? "active" : ""}`}
          onClick={() => {
            setApp("instagram");
            setScenarioId("crypto");
            setMessages([]);
            setResult(null);
          }}
        >
          Instagram DM
        </button>
      </div>

      <div className="ng-chat-demo-grid">
        <section className="ng-card">
          <h3>Pick a scam scenario</h3>
          {app === "whatsapp" && (
            <p className="ng-muted" style={{ marginBottom: 8 }}>
              Default shows a <strong>Hausa</strong> bank OTP scam in the phone. Also try Yoruba, Igbo, or Pidgin.
            </p>
          )}
          <div className="ng-sample-row">
            {scenarios.map((s) => (
              <button
                key={s.id}
                type="button"
                className={`ng-chip ${scenarioId === s.id ? "active" : ""}`}
                onClick={() => {
                  setScenarioId(s.id);
                  setCustom("");
                }}
              >
                {s.label}
              </button>
            ))}
          </div>
          <label className="ng-label">Message that will appear in the chat</label>
          <textarea
            className="ng-input ng-textarea"
            rows={4}
            value={custom || active.inbound}
            onChange={(e) => setCustom(e.target.value)}
          />
          <button
            className="sim-run-btn"
            type="button"
            disabled={busy}
            onClick={() => play(custom || active.inbound, active.contact)}
          >
            {busy ? "Playing…" : `Play ${app === "whatsapp" ? "WhatsApp" : "Instagram"} demo`}
          </button>

          {result && (
            <div className="ng-result" style={{ marginTop: 16 }}>
              <DecisionBadge decision={result.decision} score={result.risk_score} />
              <p>{result.advice}</p>
              <p className="ng-muted">
                Languages: {(result.language?.languages_detected || []).join(", ")} · channel {app}
              </p>
              {result.findings?.length > 0 && (
                <ul>
                  {result.findings.map((f, i) => (
                    <li key={i}>
                      <strong>{f.category}</strong> — {f.matched}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </section>

        <section className="ng-phone-stage">
          {app === "whatsapp" ? (
            <WhatsAppPhone messages={messages} contact={active.contact} typing={typing} />
          ) : (
            <InstagramPhone messages={messages} contact={active.contact} typing={typing} />
          )}
        </section>
      </div>
    </div>
  );
}
