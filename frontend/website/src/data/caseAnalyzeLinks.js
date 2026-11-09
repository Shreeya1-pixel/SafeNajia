/**
 * Map historical Threat Case Library IDs → demo samples for Analyze.
 * Ported from safenaija-main case detail “Analyze a similar message” flow.
 */
export const CASE_TO_SAMPLE = {
  "ncc-csirt-2026-032": "historical-free-data",
  "cbn-fraud-messages-2026": "hero-cbn",
  "cbex-2025": "investment",
  "ncc-csirt-whatsapp-2fa-2023": "pidgin-otp",
  "ncc-csirt-2026-010": "hard-gtbank",
  "cbn-official-email-2018": "email-cbn",
};

/** Reverse: demo sample → historical case (when sample is HISTORICAL CASE / basedOn). */
export const SAMPLE_TO_CASE = {
  "historical-free-data": "ncc-csirt-2026-032",
  "hero-cbn": "cbn-fraud-messages-2026",
  investment: "cbex-2025",
  "pidgin-otp": "ncc-csirt-whatsapp-2fa-2023",
  "hard-gtbank": "ncc-csirt-2026-010",
  "email-cbn": "cbn-official-email-2018",
};

export function analyzeHrefForCase(caseId) {
  const sample = CASE_TO_SAMPLE[caseId];
  if (sample) return `/analyze?case=${encodeURIComponent(caseId)}&sample=${encodeURIComponent(sample)}&autorun=1`;
  return `/analyze?case=${encodeURIComponent(caseId)}`;
}

export function analyzeHrefForSample(sampleId) {
  const caseId = SAMPLE_TO_CASE[sampleId];
  const qs = new URLSearchParams({ sample: sampleId, autorun: "1" });
  if (caseId) qs.set("case", caseId);
  return `/analyze?${qs.toString()}`;
}
