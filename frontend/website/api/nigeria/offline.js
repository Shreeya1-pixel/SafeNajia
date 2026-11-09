import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const { send } = require("../_lib/http.cjs");
const eng = require("../_lib/engine.cjs");
export default async function handler(req, res) {
  if (req.method === "OPTIONS") return send(res, 204, {});
  if (req.method !== "GET") return send(res, 405, { detail: "GET only" });
  return send(res, 200, { phrase_packs: Object.keys(eng.phrases()), mode: "local", deploy: "vercel-node" });
}
