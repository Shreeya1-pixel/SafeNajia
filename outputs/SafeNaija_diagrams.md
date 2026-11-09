# SafeNaija — flowcharts (ThinkAI ’26)

Open in [mermaid.live](https://mermaid.live).

## 1. Scan engine

```mermaid
flowchart TD
  WA[WhatsApp] --> ENG[SafeNaija engine]
  GM[Gmail] --> ENG
  LK[Link / crypto] --> ENG
  GH[GitHub] --> ENG
  ENG --> PH[Phrase packs\nEN · Pidgin · Hausa · Yoruba · Igbo]
  PH --> VIS[Link visit / SEC / secrets]
  VIS --> SC{Risk score}
  SC -->|low| OK[SAFE]
  SC -->|mid| WR[CAREFUL]
  SC -->|high| BL[DANGER]
  OK --> ADV[Advice EN + Pidgin]
  WR --> ADV
  BL --> ADV
```

## 2. Go-to-market / customers

```mermaid
flowchart LR
  A[Campus awareness] --> B[Chat Demo activation]
  B --> C[Weekly scam digest]
  C --> D[SMB SaaS revenue]
  B --> E[Phrase pack feedback]
  D --> F[Bank / telco API]
  E --> B
```

## 3. Future steps

```mermaid
flowchart LR
  N[Now MVP] --> P[+90d Campus pilot]
  P --> S[+6mo SMB SaaS]
  S --> Y[+12mo Partners API]
```

## 4. Customer segments (table summary)

| Customer | Pain | Buy motion | Need |
|---|---|---|---|
| University students | OTP / loan / GitHub secrets | Free campus | Pidgin chat + GitHub passport |
| WhatsApp SMBs | Fake payment / phishing | Low monthly SaaS | Fast Safe/Careful/Danger |
| Clubs / NGOs | No SOC budget | Pilot / grant | Demo lab + cases |
| Banks / telcos (later) | Consumer education | B2B API | NDPA-safe language packs |
