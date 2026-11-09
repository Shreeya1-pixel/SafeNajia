#!/usr/bin/env python3
"""ThinkAI ’26 twist pitch — SafeNaija (M8 blue visual system)."""
from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

OUT_DIR = Path(__file__).resolve().parent
DOWNLOADS = Path.home() / "Downloads"
DESKTOP = Path.home() / "Desktop"

BRAND = RGBColor(0x00, 0x5B, 0xB5)
BRAND_DARK = RGBColor(0x00, 0x44, 0x88)
BRAND_LIGHT = RGBColor(0xE6, 0xF0, 0xFA)
GREEN = RGBColor(0x16, 0xA3, 0x4A)
RED = RGBColor(0xDC, 0x26, 0x26)
AMBER = RGBColor(0xD9, 0x77, 0x06)
INK = RGBColor(0x1F, 0x29, 0x37)
MUTED = RGBColor(0x6B, 0x72, 0x80)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
GRAY_BG = RGBColor(0xF7, 0xFB, 0xFF)
CARD = RGBColor(0xFF, 0xFF, 0xFF)
BORDER = RGBColor(0xDB, 0xEA, 0xFE)

FONT = "Calibri"
W = Inches(13.333)
H = Inches(7.5)
M = Inches(0.55)
TOTAL = 14


def fill(shape, color):
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()


def box(slide, l, t, w, h, color=CARD, line=None):
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, l, t, w, h)
    fill(sh, color)
    if line:
        sh.line.color.rgb = line
        sh.line.width = Pt(1)
    else:
        sh.line.fill.background()
    return sh


def tb(slide, l, t, w, h):
    b = slide.shapes.add_textbox(l, t, w, h)
    tf = b.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.04)
    tf.margin_top = tf.margin_bottom = 0
    return tf


def run(p, text, *, size=16, bold=False, color=INK, font=FONT):
    r = p.add_run()
    r.text = text
    r.font.name = font
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color
    return r


def set_p(tf, text, *, size=16, bold=False, color=INK, align=PP_ALIGN.LEFT):
    p = tf.paragraphs[0]
    p.alignment = align
    p.clear()
    run(p, text, size=size, bold=bold, color=color)
    return p


def add_p(tf, text, *, size=15, bold=False, color=INK, space=6):
    p = tf.add_paragraph()
    p.space_before = Pt(space)
    run(p, text, size=size, bold=bold, color=color)
    return p


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def footer(slide, n):
    tf = tb(slide, M, H - Inches(0.38), Inches(8), Inches(0.28))
    set_p(tf, "SafeNaija  ·  ThinkAI ’26  ·  Nigeria  ·  Cybersecurity", size=10, color=MUTED)
    num = tb(slide, W - M - Inches(1.2), H - Inches(0.38), Inches(1.2), Inches(0.28))
    set_p(num, f"{n} / {TOTAL}", size=10, color=MUTED, align=PP_ALIGN.RIGHT)


def bg(slide, dark=False):
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, W, H)
    fill(sh, BRAND_DARK if dark else GRAY_BG)


def kicker(slide, text):
    tf = tb(slide, M, Inches(0.32), Inches(11), Inches(0.32))
    set_p(tf, text.upper(), size=11, bold=True, color=BRAND)
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, M, Inches(0.66), Inches(0.55), Inches(0.05))
    fill(bar, BRAND)


def title(slide, text, top=Inches(0.82), size=26):
    tf = tb(slide, M, top, Inches(12.2), Inches(0.6))
    set_p(tf, text, size=size, bold=True, color=INK)


def bullets(slide, items, l, t, w, h, size=15):
    tf = tb(slide, l, t, w, h)
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(7)
        run(p, "•  ", size=size, bold=True, color=BRAND)
        run(p, item, size=size, color=INK)


def arrow_box(slide, l, t, w, h, text, color=BRAND):
    sh = box(slide, l, t, w, h, color)
    tf = sh.text_frame
    tf.word_wrap = True
    set_p(tf, text, size=12, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    return sh


def build():
    prs = Presentation()
    prs.slide_width = W
    prs.slide_height = H
    blank = prs.slide_layouts[6]

    # ── 1 Title ─────────────────────────────────────────────────────────────
    s = prs.slides.add_slide(blank)
    bg(s, dark=True)
    tf = tb(s, M, Inches(1.5), Inches(12), Inches(0.35))
    set_p(tf, "THINKAI ’26  ·  ASSIGNED COUNTRY: NIGERIA  ·  DOMAIN: CYBERSECURITY", size=13, bold=True, color=RGBColor(0x93, 0xC5, 0xFD))
    tf = tb(s, M, Inches(2.15), Inches(12), Inches(0.9))
    set_p(tf, "SafeNaija", size=52, bold=True, color=WHITE)
    tf = tb(s, M, Inches(3.2), Inches(11.5), Inches(1.3))
    set_p(
        tf,
        "AI that checks WhatsApp, email, links and GitHub — then says Safe / Careful / Danger\nin English and Pidgin, before OTP or money leaves the phone.",
        size=18,
        color=RGBColor(0xDB, 0xEA, 0xFE),
    )
    tf = tb(s, M, Inches(5.0), Inches(11), Inches(0.7))
    set_p(
        tf,
        "5-minute pitch  ·  Failed-product twist: Norton Genie standalone  ·  Feasibility under NDPA / CBN / SEC / NCC-CSIRT",
        size=14,
        color=RGBColor(0x93, 0xC5, 0xFD),
    )
    notes(s, "One sentence: we stop Nigerian scam decisions on the apps people already use.")
    # no footer on dark title

    # ── 2 Country + domain ──────────────────────────────────────────────────
    s = prs.slides.add_slide(blank)
    bg(s)
    kicker(s, "Assigned brief")
    title(s, "Nigeria × Cybersecurity — trust on mobile-first channels")
    cards = [
        ("Country", "Nigeria\nMobile-first users · WhatsApp-heavy commerce · rising digital payments"),
        ("Domain", "Cybersecurity\nConsumer & student trust layer — not another bank SOC dashboard"),
        ("Buyer", "Students & SMBs\nNo security team · refunds are slow · OTP / BVN / NIN are the attack surface"),
        ("Twist", "Failed product\nNorton Genie free standalone AI scam checker — pulled from App Store / paywalled"),
    ]
    for i, (h, body) in enumerate(cards):
        x = M + (i % 4) * Inches(3.15)
        y = Inches(1.85)
        box(s, x, y, Inches(3.0), Inches(4.4), WHITE, BORDER)
        tf = tb(s, x + Inches(0.18), y + Inches(0.25), Inches(2.65), Inches(0.45))
        set_p(tf, h, size=14, bold=True, color=BRAND)
        tf = tb(s, x + Inches(0.18), y + Inches(0.85), Inches(2.65), Inches(3.3))
        set_p(tf, body, size=14, color=INK)
    notes(s, "Judges want country + domain clear in 15 seconds. State the twist early.")
    footer(s, 2)

    # ── 3 Real news hooks ───────────────────────────────────────────────────
    s = prs.slides.add_slide(blank)
    bg(s)
    kicker(s, "Research — real stories")
    title(s, "Three documented Nigerian cases (not invented)")
    stories = [
        (
            "WhatsApp “bank care”",
            "Plateau woman lost ₦102,000 after a WhatsApp number posed as ALAT/Wema care and sent a lookalike login.",
            "FIJ, 20 Feb 2025",
        ),
        (
            "SIM-swap syndicate",
            "Katsina police arrested a 4-person SIM-swap ring used to drain bank accounts; 32 SIMs recovered.",
            "Vanguard / NAN, 16 Jan 2025",
        ),
        (
            "CBEX collapse",
            "Crypto Bridge Exchange promised extreme short-term returns; SEC Nigeria said it was never registered.",
            "TechCabal, 15 Apr 2025 · SEC / Nairametrics follow-ups",
        ),
    ]
    for i, (h, body, src) in enumerate(stories):
        y = Inches(1.75) + i * Inches(1.55)
        box(s, M, y, Inches(12.2), Inches(1.4), WHITE, BORDER)
        tf = tb(s, M + Inches(0.3), y + Inches(0.2), Inches(11.6), Inches(0.35))
        set_p(tf, h, size=18, bold=True, color=BRAND)
        tf = tb(s, M + Inches(0.3), y + Inches(0.55), Inches(11.6), Inches(0.45))
        set_p(tf, body, size=14, color=INK)
        tf = tb(s, M + Inches(0.3), y + Inches(1.0), Inches(11.6), Inches(0.3))
        set_p(tf, f"Source: {src}", size=12, color=MUTED)
    notes(
        s,
        "FIJ: https://fij.ng/article/alat-by-wema-fraudster-steals-plateau-womans-n102000/ · Vanguard Jan 2025 · TechCabal CBEX Apr 2025. Do not embellish.",
    )
    footer(s, 3)

    # ── 4 Problem numbers ───────────────────────────────────────────────────
    s = prs.slides.add_slide(blank)
    bg(s)
    kicker(s, "The problem — with numbers")
    title(s, "Losses fell, but social engineering still wins")
    stats = [
        ("₦25.85bn", "digital-payment fraud losses in 2025\n(NIBSS at NeFF 2026 · Punch)"),
        ("67,518", "reported fraud cases in 2025\n(down from 123,918 in 2021)"),
        ("₦250bn+", "yearly cybercrime loss estimate\n(NITDA / Guardian, Aug 2025)"),
        ("#1 tactic", "Social engineering + SIM-swap\n(CBN / NIBSS NeFF 2026)"),
    ]
    for i, (big, small) in enumerate(stats):
        x = M + (i % 4) * Inches(3.15)
        box(s, x, Inches(1.85), Inches(3.0), Inches(3.0), WHITE, BORDER)
        tf = tb(s, x + Inches(0.15), Inches(2.1), Inches(2.7), Inches(0.7))
        set_p(tf, big, size=22, bold=True, color=BRAND, align=PP_ALIGN.CENTER)
        tf = tb(s, x + Inches(0.15), Inches(2.9), Inches(2.7), Inches(1.6))
        set_p(tf, small, size=13, color=INK, align=PP_ALIGN.CENTER)
    tf = tb(s, M, Inches(5.15), Inches(12.2), Inches(1.2))
    set_p(
        tf,
        "Punch (2026): losses fell 51% vs 2024 — but NIBSS warns social engineering, insider abuse, SIM-swap and phishing keep evolving.\nBusinessDay / Adhere×TechCabal (2026): Nigeria ranks near the bottom globally on fraud protection; ~90% cybersecurity talent gap.",
        size=13,
        color=MUTED,
    )
    notes(
        s,
        "Punch: digital-payment-fraud-losses-drop-51-to-n25-85bn · Guardian NITDA N250bn · Cable/ThisDay NeFF SIM-swap warnings.",
    )
    footer(s, 4)

    # ── 5 Market ────────────────────────────────────────────────────────────
    s = prs.slides.add_slide(blank)
    bg(s)
    kicker(s, "Market opportunity")
    title(s, "A growing security market — empty consumer trust layer")
    box(s, M, Inches(1.8), Inches(6.0), Inches(4.5), WHITE, BORDER)
    tf = tb(s, M + Inches(0.3), Inches(2.05), Inches(5.4), Inches(4.0))
    set_p(tf, "Nigeria cybersecurity market", size=18, bold=True, color=BRAND)
    add_p(tf, "USD 230.03m in 2025 → USD 253.77m in 2026", size=16, bold=True)
    add_p(tf, "→ USD 414.92m by 2031 (CAGR 10.32%)", size=15)
    add_p(tf, "Driver: cashless payments + NDPA + cloud (Mordor Intelligence).", size=14, color=MUTED)
    add_p(tf, "Gap we fill: affordable trust checks for students/SMBs on WhatsApp — not only bank/enterprise suites.", size=14)
    box(s, M + Inches(6.3), Inches(1.8), Inches(6.0), Inches(4.5), WHITE, BORDER)
    tf = tb(s, M + Inches(6.6), Inches(2.05), Inches(5.4), Inches(4.0))
    set_p(tf, "Why the gap is still open", size=18, bold=True, color=BRAND)
    add_p(tf, "Bank controls catch cards; people still hand over OTPs on chat.", size=15)
    add_p(tf, "Global AI checkers are English-first and paste-only.", size=15)
    add_p(tf, "SEC / CBN / NCC advisories exist — citizens rarely check them mid-scam.", size=15)
    add_p(tf, "Student GitHub leaks secrets before first revenue.", size=15)
    notes(s, "Mordor Nigeria cybersecurity market report. Keep market slide short — judges want feasibility next.")
    footer(s, 5)

    # ── 6 Solution ──────────────────────────────────────────────────────────
    s = prs.slides.add_slide(blank)
    bg(s)
    kicker(s, "AI-powered solution")
    title(s, "SafeNaija = one decision on every channel")
    for i, (lab, col, desc) in enumerate(
        [
            ("SAFE", GREEN, "Looks okay\nStill verify big payments"),
            ("CAREFUL", AMBER, "Warning + why\nWhat to check next"),
            ("DANGER", RED, "Stop now\nNo OTP · no transfer"),
        ]
    ):
        x = M + i * Inches(4.15)
        box(s, x, Inches(1.85), Inches(3.95), Inches(2.6), WHITE, BORDER)
        badge = box(s, x + Inches(0.25), Inches(2.15), Inches(3.45), Inches(0.65), col)
        set_p(badge.text_frame, lab, size=22, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        tf = tb(s, x + Inches(0.25), Inches(3.0), Inches(3.45), Inches(1.2))
        set_p(tf, desc, size=15, color=INK, align=PP_ALIGN.CENTER)
    bullets(
        s,
        [
            "Inputs: WhatsApp / Gmail / Instagram / paste · link · phone · GitHub",
            "Outputs: decision + Pidgin/English advice + Trust Chain (WHO→WHAT→WHERE→WHY→HOW→RESULT)",
            "AI role: evidence & language — deterministic rules own the score (cannot be talked into “mark safe”)",
        ],
        M,
        Inches(4.7),
        Inches(12.2),
        Inches(1.8),
        size=15,
    )
    notes(s, "Map SAFE/CAREFUL/DANGER to ALLOW/WARN/BLOCK in the live demo.")
    footer(s, 6)

    # ── 7 Flow diagram ──────────────────────────────────────────────────────
    s = prs.slides.add_slide(blank)
    bg(s)
    kicker(s, "How it works")
    title(s, "Scan engine flow (demo-ready)")
    nodes = [
        (M, "WhatsApp\nEmail\nLink\nGitHub"),
        (M + Inches(3.2), "Phrase packs\nEN · Pidgin\nHausa · Yoruba · Igbo"),
        (M + Inches(6.4), "Link / SEC\nPhone lists\nSecret patterns"),
        (M + Inches(9.6), "SAFE /\nCAREFUL /\nDANGER"),
    ]
    for x, text in nodes:
        arrow_box(s, x, Inches(2.2), Inches(2.9), Inches(1.8), text, BRAND)
    # arrows as chevrons
    for i in range(3):
        x = M + Inches(2.95) + i * Inches(3.2)
        chev = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, x, Inches(2.8), Inches(0.28), Inches(0.45))
        fill(chev, AMBER)
    box(s, M, Inches(4.4), Inches(12.2), Inches(2.1), WHITE, BORDER)
    bullets(
        s,
        [
            "Offline-first phrase packs keep basic OTP/BVN detection on-device when the net drops.",
            "GitHub mode returns a Student Risk Passport: score + top 3 fixes + picture of bad code.",
            "Case Library mirrors NCC-CSIRT / CBN / SEC advisories so advice cites real Nigerian patterns.",
        ],
        M + Inches(0.2),
        Inches(4.55),
        Inches(11.8),
        Inches(1.8),
        size=14,
    )
    notes(s, "Point to Live demo: Messages → OTP Pidgin sample → BLOCK; Links → GitHub → Risk Passport.")
    footer(s, 7)

    # ── 8 Features ──────────────────────────────────────────────────────────
    s = prs.slides.add_slide(blank)
    bg(s)
    kicker(s, "Innovation & AI usage")
    title(s, "What ships in the MVP")
    feats = [
        ("01", "Chat & inbox scan", "WhatsApp / Gmail / Instagram connect + paste; Pidgin OTP/BVN packs"),
        ("02", "Link & crypto", "Live page visit · APK / loan-app cues · SEC demo registry"),
        ("03", "GitHub passport", "Secrets → bad-code frames → top 3 student fixes"),
        ("04", "Fraud calls", "Bank helplines vs scam numbers — no call recording"),
        ("05", "SIM-swap lab", "Exposure score + alert simulation + attack demos"),
        ("06", "Trust Chain", "WHO / WHAT / WHERE / WHY / HOW / RESULT on every verdict"),
    ]
    for i, (n, h, d) in enumerate(feats):
        x = M + (i % 3) * Inches(4.15)
        y = Inches(1.8) + (i // 3) * Inches(2.35)
        box(s, x, y, Inches(3.95), Inches(2.15), WHITE, BORDER)
        tf = tb(s, x + Inches(0.2), y + Inches(0.2), Inches(3.5), Inches(0.35))
        set_p(tf, n, size=12, bold=True, color=BRAND)
        tf = tb(s, x + Inches(0.2), y + Inches(0.55), Inches(3.5), Inches(0.4))
        set_p(tf, h, size=16, bold=True, color=INK)
        tf = tb(s, x + Inches(0.2), y + Inches(1.05), Inches(3.5), Inches(0.9))
        set_p(tf, d, size=13, color=MUTED)
    notes(s, "Judging: Innovation and AI usage — stress hybrid rules+AI, not chatbot-only.")
    footer(s, 8)

    # ── 9 Failed startup ────────────────────────────────────────────────────
    s = prs.slides.add_slide(blank)
    bg(s)
    kicker(s, "Failed product twist")
    title(s, "Norton Genie (standalone free AI scam checker)")
    box(s, M, Inches(1.75), Inches(6.0), Inches(4.7), WHITE, BORDER)
    tf = tb(s, M + Inches(0.25), Inches(1.95), Inches(5.5), Inches(4.3))
    set_p(tf, "What it was", size=16, bold=True, color=BRAND)
    add_p(tf, "2023: Norton launched a free AI app to paste texts / emails / screenshots and ask “is this a scam?”", size=14)
    add_p(tf, "What failed as a standalone product", size=16, bold=True, color=RED, space=12)
    add_p(tf, "• Free Genie app removed from the US App Store; Genie.Norton.com now redirects to paid Norton 360.", size=13)
    add_p(tf, "• English-first; no Nigerian Pidgin / Hausa / Yoruba / Igbo packs.", size=13)
    add_p(tf, "• Manual paste only — not wired to WhatsApp / Gmail inboxes students actually use.", size=13)
    add_p(tf, "• No SEC / CBN / NCC-CSIRT registry context for local investment & regulator scams.", size=13)
    add_p(tf, "Source: Norton product pages · AppGoblin (app removed) · Gen Digital newsroom 2026.", size=11, color=MUTED, space=10)
    box(s, M + Inches(6.3), Inches(1.75), Inches(6.0), Inches(4.7), WHITE, BORDER)
    tf = tb(s, M + Inches(6.55), Inches(1.95), Inches(5.5), Inches(4.3))
    set_p(tf, "Why that matters for Nigeria", size=16, bold=True, color=BRAND)
    add_p(tf, "A global paste-bot dies when it cannot monetise or localise.", size=14)
    add_p(tf, "Nigerian victims need: chat-native checks, local language, regulator lists, offline OTP phrases, student GitHub hygiene.", size=14)
    add_p(tf, "Paywalling into Norton 360 leaves price-sensitive students/SMBs unprotected — the exact ThinkAI users.", size=14)
    add_p(tf, "SafeNaija keeps the free MVP decision layer local-first.", size=14, bold=True, space=12)
    notes(
        s,
        "Be fair: Norton Genie tech continues inside 360/ChatGPT/Claude. Our claim is the standalone free path failed for markets like Nigeria. Cite App Store removal / redirect to 360.",
    )
    footer(s, 9)

    # ── 10 Comparison ───────────────────────────────────────────────────────
    s = prs.slides.add_slide(blank)
    bg(s)
    kicker(s, "Why SafeNaija is better")
    title(s, "We avoid Genie’s failure modes")
    rows = [
        ("Need", "Genie standalone", "SafeNaija"),
        ("Language", "English-centric", "EN + Pidgin + Hausa/Yoruba/Igbo packs"),
        ("Channel", "Copy-paste only", "WhatsApp / Gmail / IG + chat demo"),
        ("Local intel", "Generic web reputation", "SEC pack · bank helplines · NCC-style cases"),
        ("Students", "Not a focus", "GitHub Risk Passport + top 3 fixes"),
        ("Business model", "Pulled into paid suite", "Hackathon MVP free; campus/SMB path"),
        ("Explainability", "Chat answer", "Trust Chain + sourced Case Library"),
        ("Privacy", "Cloud AI path", "Offline phrase packs by default"),
    ]
    for r, row in enumerate(rows):
        y = Inches(1.7) + r * Inches(0.58)
        for c, cell in enumerate(row):
            x = M + c * Inches(4.1)
            col = BRAND_LIGHT if r == 0 else WHITE
            b = box(s, x, y, Inches(4.0), Inches(0.52), col, BORDER)
            tf = b.text_frame
            set_p(tf, cell, size=12, bold=(r == 0 or c == 0), color=INK, align=PP_ALIGN.CENTER)
    notes(s, "Say out loud: we are not claiming Norton is “dead” — the free standalone path failed; we designed against those gaps.")
    footer(s, 10)

    # ── 11 Feasibility ──────────────────────────────────────────────────────
    s = prs.slides.add_slide(blank)
    bg(s)
    kicker(s, "Feasibility in Nigeria")
    title(s, "Fits systems & rules that already exist")
    regs = [
        ("NDPA 2023", "Minimise personal data; scan locally; redact stored evidence; user permission for inbox connect."),
        ("Cybercrimes Act", "Support lawful reporting paths (EFCC / police / NCC-CSIRT) — we advise, we don’t vigilante."),
        ("CBN / NIBSS", "Align advice with bank helplines & NeFF fraud trends (SIM-swap, social engineering)."),
        ("SEC Nigeria", "Point investors to sec.gov.ng verification — never invent “fraudulent company” labels."),
        ("NCC-CSIRT", "Case Library mirrors public advisories (e.g. free-data phishing, rogue SMS networks)."),
        ("NITDA / ngCERT", "Public awareness mission match — consumer education + technical checks."),
    ]
    for i, (h, d) in enumerate(regs):
        x = M + (i % 3) * Inches(4.15)
        y = Inches(1.75) + (i // 3) * Inches(2.35)
        box(s, x, y, Inches(3.95), Inches(2.15), WHITE, BORDER)
        tf = tb(s, x + Inches(0.2), y + Inches(0.25), Inches(3.55), Inches(0.4))
        set_p(tf, h, size=15, bold=True, color=BRAND)
        tf = tb(s, x + Inches(0.2), y + Inches(0.75), Inches(3.55), Inches(1.2))
        set_p(tf, d, size=13, color=INK)
    notes(s, "Judging: feasibility — name real Nigerian regulators. Honest limit: we do not access telco SIM systems.")
    footer(s, 11)

    # ── 12 Demo / research proof ────────────────────────────────────────────
    s = prs.slides.add_slide(blank)
    bg(s)
    kicker(s, "Research & analysis · prototype")
    title(s, "What judges can verify in 60 seconds")
    bullets(
        s,
        [
            "Demo path: Pidgin OTP WhatsApp sample → DANGER · crypto link → SEC cue · GitHub → Risk Passport",
            "Evidence base: FIJ ₦102k WhatsApp theft · Vanguard SIM-swap arrests · TechCabal/SEC on CBEX · NCC-CSIRT advisories",
            "Market math: NIBSS ₦25.85bn (2025) · NITDA ~₦250bn cybercrime · Mordor cyber market ~USD 254m (2026)",
            "Honest limits: no live telco SIM confirmation · SEC pack is demo subset · AI can enrich but rules own the score",
        ],
        M,
        Inches(1.85),
        Inches(12.2),
        Inches(3.2),
        size=16,
    )
    box(s, M, Inches(5.1), Inches(12.2), Inches(1.4), BRAND_LIGHT, BORDER)
    tf = tb(s, M + Inches(0.3), Inches(5.3), Inches(11.6), Inches(1.0))
    set_p(
        tf,
        "Presentation scoring map: Innovation (hybrid AI + local packs) · Feasibility (NDPA/CBN/SEC) · Research (cited news) · 5-min clarity · Q&A readiness.",
        size=15,
        bold=True,
        color=INK,
    )
    notes(s, "Offer to open /cases and /links live if judges ask.")
    footer(s, 12)

    # ── 13 Roadmap ──────────────────────────────────────────────────────────
    s = prs.slides.add_slide(blank)
    bg(s)
    kicker(s, "Roadmap")
    title(s, "From Imagine Cup MVP to campus pilot")
    phases = [
        ("Now", GREEN, "Phrase packs · chat demo · GitHub passport · Case Library · Trust Chain"),
        ("+90 days", BRAND, "Campus pilot (2–3 universities) · WhatsApp Cloud API production · measure blocked OTP shares"),
        ("+6 mo", AMBER, "SMB WhatsApp Business trial · live SEC registry hook · Hausa/Yoruba/Igbo expansion"),
        ("+12 mo", BRAND_DARK, "Offline mobile pack · bank partnership for helpline sync · EFCC/NCC report assist"),
    ]
    for i, (h, col, d) in enumerate(phases):
        x = M + i * Inches(3.15)
        box(s, x, Inches(1.9), Inches(3.0), Inches(4.3), WHITE, BORDER)
        badge = box(s, x + Inches(0.2), Inches(2.15), Inches(2.6), Inches(0.55), col)
        set_p(badge.text_frame, h, size=14, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        tf = tb(s, x + Inches(0.2), Inches(2.95), Inches(2.6), Inches(2.9))
        set_p(tf, d, size=14, color=INK)
    notes(s, "Keep roadmap humble — MVP works today.")
    footer(s, 13)

    # ── 14 Close ────────────────────────────────────────────────────────────
    s = prs.slides.add_slide(blank)
    bg(s, dark=True)
    tf = tb(s, M, Inches(1.8), Inches(12), Inches(0.4))
    set_p(tf, "CLOSING ASK", size=14, bold=True, color=RGBColor(0x93, 0xC5, 0xFD))
    tf = tb(s, M, Inches(2.4), Inches(12), Inches(1.2))
    set_p(tf, "Help us put a Nigerian trust layer\non the chats people already open.", size=28, bold=True, color=WHITE)
    tf = tb(s, M, Inches(4.0), Inches(12), Inches(1.5))
    set_p(
        tf,
        "SafeNaija  ·  Nigeria  ·  Cybersecurity\nGenie standalone failed by going global-generic and paywalled.\nWe win by going local, explainable, and free at the decision layer.",
        size=16,
        color=RGBColor(0xDB, 0xEA, 0xFE),
    )
    tf = tb(s, M, Inches(6.0), Inches(12), Inches(0.5))
    set_p(tf, "Q&A — 3 minutes  ·  Demo ready on localhost / cases / links", size=14, color=RGBColor(0x93, 0xC5, 0xFD))
    notes(s, "End early. Invite questions on privacy, false positives, and telco limits.")

    out_name = "SafeNaija_ThinkAI26_Twist_Pitch.pptx"
    paths = [
        OUT_DIR / out_name,
        DOWNLOADS / out_name,
        DESKTOP / out_name,
    ]
    for p in paths:
        prs.save(p)
        print("saved", p)
    return paths[0]


if __name__ == "__main__":
    build()
