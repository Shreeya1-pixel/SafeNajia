import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const { send, readBody } = require("../../_lib/http.cjs");
const { checkPhone } = require("../../_lib/engine.cjs");
export default async function handler(req, res) {
  if (req.method === "OPTIONS") return send(res, 204, {});
  if (req.method !== "POST") return send(res, 405, { detail: "POST only" });
  const body = await readBody(req);
  return send(res, 200, checkPhone(body.number || ""));
}
