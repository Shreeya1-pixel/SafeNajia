# SafeNaija — Mermaid diagrams

Open in [mermaid.live](https://mermaid.live), GitHub, or Notion. Labels stay short for slides.

---

## 1. System architecture

WhatsApp / email / GitHub / paste → scan engine → decision

```mermaid
flowchart LR
  WA[WhatsApp]
  EM[Email / Gmail]
  GH[GitHub URL]
  PS[Paste message]
  ENG[SafeNaija<br/>scan engine]
  DEC{Safe / Careful / Danger}
  ADV[Plain advice<br/>EN + Pidgin]

  WA --> ENG
  EM --> ENG
  GH --> ENG
  PS --> ENG
  ENG --> DEC
  DEC --> ADV
```

---

## 2. Decision flow

Message in → checks → Safe / Careful / Danger → advice

```mermaid
flowchart TD
  IN[Message / link in] --> PH[Phrase pack<br/>EN · Pidgin · Hausa · Yoruba · Igbo]
  PH --> LK[Link / page visit]
  LK --> SD[Sender / number lists]
  SD --> SC{Risk score}
  SC -->|low| OK[Safe]
  SC -->|medium| WR[Careful]
  SC -->|high| BL[Danger]
  OK --> ADV[What to do next]
  WR --> ADV
  BL --> ADV
```

---

## 3. User journey

Victim receives scam → SafeNaija → outcome

```mermaid
flowchart LR
  A[Scam lands on<br/>WhatsApp / email] --> B[User opens<br/>SafeNaija]
  B --> C[Scan message<br/>or link]
  C --> D{Decision}
  D -->|Danger| E[Stop: no OTP<br/>no money sent]
  D -->|Careful| F[Verify on<br/>official app]
  D -->|Safe| G[Continue<br/>with caution]
```

---

## 4. GitHub scan flow

Repo URL → secret checks → Risk Passport

```mermaid
flowchart TD
  U[Student pastes<br/>repo URL] --> F[Fetch README<br/>.env · config]
  F --> S[Secret patterns<br/>API keys · AWS · DB]
  S --> D[Dependency / loan-app<br/>risk hints]
  D --> P[Student Risk Passport]
  P --> R1[Score]
  P --> R2[Top 3 fixes]
  P --> R3[Picture of bad code]
```

---

## 5. Build roadmap

```mermaid
gantt
  title SafeNaija roadmap
  dateFormat  YYYY-MM
  axisFormat  %b %Y

  section MVP
  Phrase packs + paste scan     :done, m1, 2026-10, 2026-11
  WhatsApp / Gmail / chat demo  :done, m2, 2026-11, 2026-11
  GitHub bad-code frames        :done, m3, 2026-11, 2026-11

  section Pilot
  Campus student pilot          :p1, 2026-12, 2027-01
  SMB WhatsApp Business trial   :p2, 2027-01, 2027-02
  Live SEC registry hook        :p3, 2027-02, 2027-03

  section Scale
  Offline mobile pack           :s1, 2027-03, 2027-05
  Hausa / Yoruba / Igbo expand  :s2, 2027-04, 2027-06
```
