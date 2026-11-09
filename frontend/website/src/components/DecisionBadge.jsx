export default function DecisionBadge({ decision, score }) {
  const d = (decision || "ALLOW").toUpperCase();
  const cls =
    d === "BLOCK" ? "ng-badge block" : d === "WARN" ? "ng-badge warn" : "ng-badge allow";
  return (
    <div className={cls}>
      <strong>{d}</strong>
      {typeof score === "number" && <span> · risk {score}</span>}
    </div>
  );
}
