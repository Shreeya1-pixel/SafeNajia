import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const { send, readBody } = require("../../_lib/http.cjs");
const { scanMessage } = require("../../_lib/engine.cjs");
export default async function handler(req, res) {
  if (req.method === "OPTIONS") return send(res, 204, {});
  if (req.method !== "POST") return send(res, 405, { detail: "POST only" });
  const body = await readBody(req);
  return send(res, 200, { attack_type: body.attack_type || "phishing", sample: "Your GTBank account will be RESTRICTED.", scan: scanMessage("Your GTBank account will be RESTRICTED. Re-validate BVN now and send OTP to continue.", "sim", true) });
}
