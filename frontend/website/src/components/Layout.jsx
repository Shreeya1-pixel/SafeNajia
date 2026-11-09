import { Link, useLocation } from "react-router-dom";
import { useEffect, useState } from "react";
import { nigeriaHealth } from "../nigeriaApi";

export default function Layout({ children }) {
  const location = useLocation();
  const [backendOk, setBackendOk] = useState(false);

  useEffect(() => {
    const check = () => {
      nigeriaHealth()
        .then(() => setBackendOk(true))
        .catch(() => setBackendOk(false));
    };
    check();
    const t = setInterval(check, 12000);
    return () => clearInterval(t);
  }, []);

  const navLink = (to, label) => (
    <Link to={to} className={location.pathname === to ? "safeo-nav-link active" : "safeo-nav-link"}>
      {label}
    </Link>
  );

  return (
    <div className="safeo-app ng-app">
      <header className="safeo-header">
        <div className="safeo-brand">
          <div className="safeo-brand-mark ng-mark">SN</div>
          <div className="safeo-brand-text">
            <h1>SafeNaija</h1>
            <span>Nigeria cyber-safety · ThinkAI ’26</span>
          </div>
        </div>
        <nav className="safeo-nav">
          {navLink("/", "Home")}
          {navLink("/analyze", "Analyze")}
          {navLink("/messages", "Messages")}
          {navLink("/chat-demo", "Chat Demo")}
          {navLink("/links", "Links")}
          {navLink("/calls", "Calls")}
          {navLink("/sim-swap", "SIM Swap Lab")}
          {navLink("/cases", "Cases")}
        </nav>
        <div className="safeo-header-right">
          <span className={`safeo-engine-dot ${backendOk ? "ok" : "off"}`} title={backendOk ? "Engine online" : "Engine offline"} />
          <span className="safeo-engine-label">{backendOk ? "Engine online" : "Engine offline"}</span>
          <Link to="/analyze" className="sim-run-btn safeo-nav-cta">
            Analyze a threat →
          </Link>
        </div>
      </header>
      <main className="safeo-main">{children}</main>
    </div>
  );
}
