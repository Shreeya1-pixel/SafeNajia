import { Link } from "react-router-dom";

const FEATURES = [
  {
    to: "/analyze",
    n: "00",
    title: "Analyze a threat",
    desc: "Paste a message, screenshot text, URL or email — get SAFE / CAREFUL / DANGER + Trust Chain.",
  },
  {
    to: "/chat-demo",
    n: "01",
    title: "WhatsApp & Instagram chat demo",
    desc: "Phone UI like NABD — watch a scam land in chat, then SafeNaija BLOCK / WARN in Pidgin.",
  },
  {
    to: "/messages",
    n: "01b",
    title: "Connect real inboxes",
    desc: "Wire WhatsApp Cloud API, Gmail App Password, or Instagram token and scan live messages.",
  },
  {
    to: "/links",
    n: "02",
    title: "Link & Crypto Checks",
    desc: "Websites, GitHub repos, investment links — bad-code pictures + Student Risk Passport (score + top 3 fixes).",
  },
  {
    to: "/calls",
    n: "03",
    title: "Fraud Call Detection",
    desc: "Match numbers to bank helplines and reported scams — no call recording.",
  },
  {
    to: "/sim-swap",
    n: "04",
    title: "SIM Swap Lab",
    desc: "Google-search a person in a live terminal, score SIM-swap risk, simulate alerts & attacks.",
  },
  {
    to: "/cases",
    n: "05",
    title: "Case Library & entities",
    desc: "Documented Nigerian incidents (NCC-CSIRT, CBN, SEC) plus trusted official domains.",
  },
];

export default function Home() {
  return (
    <div className="home-page ng-home">
      <section className="home-hero ng-hero">
        <div className="home-hero-badge">ThinkAI ’26 · Nigeria · Imagine Cup MVP</div>
        <h1 className="home-hero-h1">SafeNaija</h1>
        <p className="home-hero-sub">
          Live WhatsApp / Gmail protection, GitHub Risk Passport, Trust Chain explainability, fraud-call
          checks, and Google OSINT for SIM-swap risk — with Nigerian languages built into every scan.
        </p>
        <div className="home-hero-cta">
          <Link to="/analyze" className="sim-run-btn">
            Analyze a threat →
          </Link>
          <Link to="/cases" className="ng-btn-ghost">
            Case Library
          </Link>
        </div>
      </section>

      <section className="ng-feature-grid">
        {FEATURES.map((f) => (
          <Link key={f.to} to={f.to} className="ng-feature-card">
            <span className="ng-feature-n">{f.n}</span>
            <h3>{f.title}</h3>
            <p>{f.desc}</p>
          </Link>
        ))}
      </section>
    </div>
  );
}
