const API = "/api";
const TIMEOUT_MS = 20000;

async function post(path, body) {
  const res = await fetch(`${API}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body ?? {}),
    signal: AbortSignal.timeout(TIMEOUT_MS),
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || `Request failed: ${res.status}`);
  }
  return res.json();
}

async function get(path) {
  const res = await fetch(`${API}${path}`, { signal: AbortSignal.timeout(TIMEOUT_MS) });
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json();
}

export const nigeriaHealth = () => get("/nigeria/health");
export const nigeriaFeatures = () => get("/nigeria/features");
export const nigeriaChannels = () => get("/nigeria/channels");
export const nigeriaOffline = () => get("/nigeria/offline");
export const nigeriaAttackCatalog = () => get("/nigeria/attacks/catalog");

export const connectWhatsApp = (phone_number_id, access_token, verify_token = "safenaija") =>
  post("/nigeria/channels/whatsapp/connect", { phone_number_id, access_token, verify_token });

export const gmailOauthStart = () => get("/nigeria/channels/gmail/oauth/start");

export const connectGmailImap = (email, app_password) =>
  post("/nigeria/channels/gmail/imap", { email, app_password });

export const connectInstagram = (access_token, user_id = "me") =>
  post("/nigeria/channels/instagram/connect", { access_token, user_id });

export const disconnectChannel = (channel) => post(`/nigeria/channels/${channel}/disconnect`);

export const fetchInbox = (channel) => get(`/nigeria/channels/${channel}/inbox`);

export const scanInbox = (channel) => post(`/nigeria/channels/${channel}/inbox/scan`);

export const scanMessage = (text, channel = "manual") =>
  post("/nigeria/scan/message", { text, channel, offline: true });

export const scanLink = (url, accompanying_text = "") =>
  post("/nigeria/scan/link", { url, accompanying_text });

export const scanGithub = (url) => post("/nigeria/scan/github", { url });

export const checkPhone = (number) => post("/nigeria/phone/check", { number });

export const simSwapRisk = (payload) => post("/nigeria/sim-swap/risk", payload);

export const simSwapOsint = (payload) => post("/nigeria/sim-swap/osint", payload);

export const simulateAlerts = (scenario = "sim_swap") =>
  post("/nigeria/sim-swap/alerts/simulate", { scenario });

export const simulateAttack = (attack_type = "phishing") =>
  post("/nigeria/attacks/simulate", { attack_type });
