import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const { send, readBody } = require("../../_lib/http.cjs");
const { scanLink } = require("../../_lib/engine.cjs");
export default async function handler(req, res) {
  if (req.method === "OPTIONS") return send(res, 204, {});
  if (req.method !== "POST") return send(res, 405, { detail: "POST only" });
  const body = await readBody(req);
  const r = scanLink(body.url || "");
  r.focus = "github_secret";
  return send(res, 200, r);
}
