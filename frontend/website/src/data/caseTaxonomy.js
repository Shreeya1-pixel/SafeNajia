export const CATEGORY_NAMES = {"fake-giveaway": "Fake giveaway / free data & airtime", "government-impersonation": "Government / regulator impersonation", "investment-scam": "Investment / Ponzi scheme", "account-takeover": "WhatsApp / social account takeover", "banking-phishing": "Banking credential phishing"};

export function categoryName(id) {
  return CATEGORY_NAMES[id] || id;
}

export function authorityOf(sourceOrg) {
  const base = String(sourceOrg || "").split(" (")[0].trim();
  if (base.startsWith("Central Bank")) return "CBN";
  if (base.startsWith("Securities and Exchange")) return "SEC Nigeria";
  if (base.startsWith("NCC-CSIRT") || base.includes("Nigerian Communications")) return "NCC-CSIRT";
  return base;
}

export const EXPECTED_SEV = {
  legitimate: "LOW",
  suspicious: "MODERATE",
  "high-risk": "HIGH",
  critical: "CRITICAL",
};
