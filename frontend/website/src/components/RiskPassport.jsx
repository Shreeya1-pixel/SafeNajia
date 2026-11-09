/** Student Risk Passport — score + top 3 fixes (from SafeNaija pitch / Trust Engine lab). */

export default function RiskPassport({ passport }) {
  if (!passport) return null;
  const tone = passport.tone || "warn";
  return (
    <div className={`ng-passport passport-${tone}`}>
      <div className="ng-passport-top">
        <div>
          <div className="ng-passport-kicker">{passport.title || "Student Risk Passport"}</div>
          <h3>{passport.repo}</h3>
          <p>{passport.status}</p>
        </div>
        <div className="ng-passport-score">
          <span>{passport.score}</span>
          <small>/100 risk</small>
        </div>
      </div>
      <div className="ng-passport-grid">
        <div>
          <strong>{passport.findings_count ?? 0}</strong>
          <span>findings</span>
        </div>
        <div>
          <strong>{passport.frames_count ?? 0}</strong>
          <span>bad-code frames</span>
        </div>
        <div>
          <strong>{passport.decision || "—"}</strong>
          <span>decision</span>
        </div>
      </div>
      <div className="ng-passport-actions">
        <div className="ng-passport-title">Top 3 fixes</div>
        <ol>
          {(passport.top_fixes || []).map((f) => (
            <li key={f}>{f}</li>
          ))}
        </ol>
      </div>
    </div>
  );
}
