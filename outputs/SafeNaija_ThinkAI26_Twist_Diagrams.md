# SafeNaija — ThinkAI ’26 Twist · Mermaid diagrams

Open in [mermaid.live](https://mermaid.live), GitHub, or Notion. Short labels for slides.

Country: **Nigeria** · Domain: **Cybersecurity** · Failed product contrast: **Norton Genie standalone**

---

## 1. System architecture

WhatsApp / email / GitHub / paste → SafeNaija engine → Safe / Careful / Danger

```mermaid
flowchart LR
  WA[WhatsApp]
  EM[Email / Gmail]
  LK[Link / crypto]
  GH[GitHub]
  PS[Paste / screenshot text]
  ENG[SafeNaija<br/>rules + AI evidence]
  DEC{Safe / Careful / Danger}
  ADV[Advice EN + Pidgin<br/>Trust Chain]

  WA --> ENG
  EM --> ENG
  LK --> ENG
  GH --> ENG
  PS --> ENG
  ENG --> DEC
  DEC --> ADV
```

---

## 2. Decision flow

```mermaid
flowchart TD
  IN[Message / link / number in] --> PH[Phrase packs<br/>EN · Pidgin · Hausa · Yoruba · Igbo]
  PH --> LK[Link visit / SEC pack]
  LK --> SD[Sender / phone lists]
  SD --> SC{Risk score}
  SC -->|low| OK[Safe]
  SC -->|medium| WR[Careful]
  SC -->|high| BL[Danger]
  OK --> TC[Trust Chain<br/>WHO → WHAT → WHERE → WHY → HOW → RESULT]
  WR --> TC
  BL --> TC
```

---

## 3. Why Genie standalone failed vs SafeNaija

```mermaid
flowchart TB
  subgraph Genie["Norton Genie standalone"]
    G1[English-first paste app]
    G2[No NG regulator packs]
    G3[Not chat-native]
    G4[Pulled → Norton 360 paywall]
    G1 --> G2 --> G3 --> G4
  end

  subgraph SN["SafeNaija"]
    S1[Pidgin + local languages]
    S2[SEC / CBN / NCC cases]
    S3[WhatsApp · Gmail · GitHub]
    S4[Free MVP decision layer]
    S1 --> S2 --> S3 --> S4
  end

  G4 -.->|avoid these gaps| S1
```

---

## 4. User journey (victim → outcome)

```mermaid
flowchart LR
  A[Scam lands on<br/>WhatsApp / email] --> B[Open SafeNaija]
  B --> C[Scan message / link]
  C --> D{Decision}
  D -->|Danger| E[Stop: no OTP<br/>no money sent]
  D -->|Careful| F[Verify on<br/>cbn.gov.ng / sec.gov.ng]
  D -->|Safe| G[Continue<br/>with caution]
```

---

## 5. GitHub Student Risk Passport

```mermaid
flowchart TD
  U[Paste repo URL] --> F[Fetch README · .env · config]
  F --> S[Secret patterns<br/>API keys · AWS · DB]
  S --> D[Loan-app / APK hints]
  D --> P[Student Risk Passport]
  P --> R1[Score 0–100]
  P --> R2[Top 3 fixes]
  P --> R3[Picture of bad code]
```

---

## 6. Nigeria feasibility map

```mermaid
flowchart TB
  SN[SafeNaija MVP]
  SN --> NDPA[NDPA 2023<br/>minimise / local scan]
  SN --> CBN[CBN / NIBSS<br/>helplines · NeFF trends]
  SN --> SEC[SEC Nigeria<br/>verify operators]
  SN --> NCC[NCC-CSIRT<br/>public advisories]
  SN --> CYB[Cybercrimes Act<br/>report · don’t vigilante]
```

---

## 7. Build roadmap

```mermaid
gantt
  title SafeNaija ThinkAI roadmap
  dateFormat  YYYY-MM
  axisFormat  %b %Y

  section MVP
  Phrase packs + Trust Chain     :done, m1, 2026-10, 2026-11
  Chat demo + Case Library       :done, m2, 2026-11, 2026-11
  GitHub Risk Passport           :done, m3, 2026-11, 2026-11

  section Pilot
  Campus student pilot           :p1, 2026-12, 2027-01
  SMB WhatsApp Business trial    :p2, 2027-01, 2027-02
  Live SEC registry hook         :p3, 2027-02, 2027-03

  section Scale
  Offline mobile pack            :s1, 2027-03, 2027-05
  Hausa / Yoruba / Igbo expand   :s2, 2027-04, 2027-06
```

---

## 8. Market & loss snapshot (cite on slides)

| Figure | Meaning | Source |
|---|---|---|
| ₦25.85bn | Digital-payment fraud losses 2025 | NIBSS / Punch (NeFF 2026) |
| 67,518 | Reported fraud cases 2025 | NIBSS |
| ~₦250bn | Yearly cybercrime loss estimate | NITDA / Guardian Aug 2025 |
| USD 230m → 254m | NG cybersecurity market 2025→2026 | Mordor Intelligence |
| ₦102,000 | WhatsApp bank-impersonation loss | FIJ, 20 Feb 2025 |
| CBEX | Unregistered investment collapse | TechCabal Apr 2025 · SEC |

---

## Sources (speaker notes)

- Punch — fraud losses drop 51% to ₦25.85bn (2026 NeFF data)
- The Cable / ThisDay — CBN & NIBSS on SIM-swap / social engineering
- Guardian — NITDA ₦250bn cybercrime estimate (26 Aug 2025)
- FIJ — ALAT/Wema WhatsApp theft ₦102k (20 Feb 2025)
- Vanguard / NAN — Katsina SIM-swap arrests (16 Jan 2025)
- TechCabal — CBEX collapse (15 Apr 2025)
- Mordor — Nigeria cybersecurity market outlook
- Norton / AppGoblin / Gen Digital — Genie standalone removed; folded into Norton 360 / ChatGPT / Claude
