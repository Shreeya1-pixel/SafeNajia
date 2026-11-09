import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const { send, readBody } = require("../../_lib/http.cjs");
const { decision } = require("../../_lib/engine.cjs");
export default async function handler(req, res) {
  if (req.method === "OPTIONS") return send(res, 204, {});
  if (req.method !== "POST") return send(res, 405, { detail: "POST only" });
  const body = await readBody(req);
  const flags = [body.phone_public_on_social, body.nin_or_bvn_shared_before, body.email_breached_known, body.reused_passwords, body.no_bank_transaction_alerts, body.dual_sim_unknown_apps, body.recent_sim_issues, body.public_home_address].filter(Boolean).length;
  const score = Math.min(0.95, 0.15 + flags * 0.1);
  return send(res, 200, { decision: decision(score), risk_score: score, factors: flags, advice: score >= 0.45 ? "Elevate SIM-swap hygiene: PIN lock SIM, alert bank, reduce public PII." : "Baseline risk looks manageable — keep alerts on." });
}
