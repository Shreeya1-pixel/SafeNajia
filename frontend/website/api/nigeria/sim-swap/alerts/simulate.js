import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const { send, readBody } = require("../../../_lib/http.cjs");
export default async function handler(req, res) {
  if (req.method === "OPTIONS") return send(res, 204, {});
  if (req.method !== "POST") return send(res, 405, { detail: "POST only" });
  const body = await readBody(req);
  return send(res, 200, { scenario: body.scenario || "sim_swap", alerts: [{ channel: "sms", text: "SIM change detected on your line. If this wasn't you, call your bank." }, { channel: "email", text: "Possible account takeover risk. Freeze cards in the official app." }] });
}
