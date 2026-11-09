/** Nigerian Threat Case Library — HISTORICAL CASES ONLY (sourced). Ported from SafeNaija Trust Engine KB. */

export const THREAT_CASES = [
  {
    id: "ncc-csirt-2026-032",
    label: "HISTORICAL CASE",
    name: "“Free data and airtime” WhatsApp phishing (NCC-CSIRT-2026-032)",
    date: "2026-08-18",
    sourceOrg: "NCC-CSIRT",
    sourceUrl:
      "https://csirt.ncc.gov.ng/index.php/resources/security-advisories/431-fraudulent-free-data-and-airtime-phishing-campaign-hosted-on-ibaidad-com",
    threatType: "fake-giveaway",
    mechanism:
      "Fake promo offered 10GB data + ₦5,000 airtime; visitors entered a phone number then shared the link on WhatsApp to ‘qualify’.",
    indicators: ["ibaidad[.]com", "10GB + ₦5,000 airtime", "Share to WhatsApp groups"],
    whyItMatters: "Spreads through trusted contacts — the sender looks safe, the destination is not.",
    safeNaijaTake: "Unrealistic reward + forced sharing + phone harvest → BLOCK; domain is not a telco/NCC site.",
  },
  {
    id: "cbn-fraud-messages-2026",
    label: "HISTORICAL CASE",
    name: "Fraudulent messages impersonating the Central Bank of Nigeria",
    date: "2026-04-21",
    sourceOrg: "CBN (Premium Times / BusinessDay)",
    sourceUrl:
      "https://www.premiumtimesng.com/business/business-news/873799-cbn-alerts-public-to-fraudulent-messages-cybersecurity-hack-attempts.html",
    threatType: "government-impersonation",
    mechanism:
      "Emails/SMS/posts falsely attributed to CBN, using leadership or licensing pretext to push malicious links.",
    indicators: ["Claims to be from CBN", "Links not on cbn.gov.ng", "‘Verify’ credential ask"],
    whyItMatters: "Regulator authority is borrowed to bypass scepticism.",
    safeNaijaTake: "Claimed CBN + destination ≠ cbn.gov.ng → impersonation; never share OTP/BVN via the link.",
  },
  {
    id: "cbex-2025",
    label: "HISTORICAL CASE",
    name: "CBEX investment platform collapse",
    date: "2025-04-15",
    sourceOrg: "SEC Nigeria (TechCabal / Nairametrics)",
    sourceUrl: "https://techcabal.com/2025/04/15/cbex-ponzi-collapse-nigeria/",
    threatType: "investment-scam",
    mechanism:
      "Platform promising ~100% returns in 30 days collapsed; SEC stated it was never registered; later ‘withdrawal fees’ reported.",
    indicators: ["Guaranteed high short-term returns", "Not on SEC register", "Withdrawal fee to unlock funds"],
    whyItMatters: "Social proof replaces verification; a second scam often follows the freeze.",
    safeNaijaTake: "Unrealistic returns + unverified operator → WARN/BLOCK; verify on sec.gov.ng.",
  },
  {
    id: "ncc-csirt-whatsapp-2fa-2023",
    label: "HISTORICAL CASE",
    name: "WhatsApp account takeover — enable two-step verification",
    date: "2023-04-04",
    sourceOrg: "NCC-CSIRT (Nairametrics)",
    sourceUrl: "https://nairametrics.com/2023/04/05/whatsapp-is-now-a-primary-target-for-hackers-ncc-warns",
    threatType: "account-takeover",
    mechanism: "Attackers target WhatsApp; a stolen SMS code alone can hijack the account without two-step verification.",
    indicators: ["Unsolicited WhatsApp registration code", "Friend asks you to forward the 6-digit code"],
    whyItMatters: "A hijacked friend’s account turns every contact into a target.",
    safeNaijaTake: "OTP/code-forward ask → BLOCK; enable WhatsApp Two-Step Verification.",
  },
  {
    id: "ncc-csirt-2026-010",
    label: "HISTORICAL CASE",
    name: "Rogue cellular network / SMS banking fraud (NCC-CSIRT-2026-010)",
    date: "2026-03-30",
    sourceOrg: "NCC-CSIRT",
    sourceUrl:
      "https://csirt.ncc.gov.ng/index.php/resources/security-advisories/411-ncc-csirt-cybersecurity-advisory-on-rogue-cellular-network-attacks-and-mobile-signal-hijacking-used-for-banking-fraud",
    threatType: "banking-phishing",
    mechanism: "Rogue networks / SMS banking fraud — sender labels on SMS can be spoofed at the network layer.",
    indicators: ["SMS appearing to come from a bank", "Links delivered over SMS"],
    whyItMatters: "SafeNaija never treats a sender name alone as proof of identity.",
    safeNaijaTake: "Check WHERE the link goes and bank helpline lists — not just the SMS label.",
  },
  {
    id: "cbn-official-email-2018",
    label: "HISTORICAL CASE",
    name: "Fraudsters impersonating CBN officers by email",
    date: "2018-07-26",
    sourceOrg: "Central Bank of Nigeria",
    sourceUrl: "https://www.cbn.gov.ng/Out/2018/CCD/FakeEmailDisclaimer%20260718.pdf",
    threatType: "government-impersonation",
    mechanism: "Emails/social accounts in names of CBN officers used to defraud the public.",
    indicators: ["CBN official name on a non-@cbn.gov.ng email"],
    whyItMatters: "Gives a deterministic rule: CBN claims must come from @cbn.gov.ng.",
    safeNaijaTake: "Email analysis: claimed CBN + wrong sender domain → identity mismatch.",
  },
];

export const TRUSTED_ENTITIES = [
  { name: "Central Bank of Nigeria", short: "CBN", domains: ["cbn.gov.ng"], note: "Official emails use @cbn.gov.ng" },
  { name: "Securities and Exchange Commission Nigeria", short: "SEC", domains: ["sec.gov.ng"], note: "Verify operators on sec.gov.ng" },
  { name: "Nigerian Communications Commission CSIRT", short: "NCC-CSIRT", domains: ["csirt.ncc.gov.ng", "ncc.gov.ng"], note: "Security advisories" },
  { name: "Nigeria Inter-Bank Settlement System", short: "NIBSS", domains: ["nibss-plc.com.ng"], note: "BVN / payment rails" },
];
