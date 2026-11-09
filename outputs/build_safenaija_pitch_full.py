#!/usr/bin/env python3
"""SafeNaija ThinkAI ’26 pitch — prototype pics, market table, roadmap, flowcharts."""
from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt

OUT_DIR = Path(__file__).resolve().parent
IMG = OUT_DIR / "img"
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
HEADER_BG = RGBColor(0x00, 0x5B, 0xB5)
ROW_ALT = RGBColor(0xF0, 0xF7, 0xFF)

FONT = "Arial"
W = Inches(13.333)
H = Inches(7.5)
M = Inches(0.5)
TOTAL = 16


def fill(shape, color):
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()


def box(slide, l, t, w, h, color=CARD, line=None):
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, l, t, w, h)
    fill(sh, color)
    try:
        sh.adjustments[0] = 0.08
    except Exception:
        pass
    if line:
        sh.line.color.rgb = line
        sh.line.width = Pt(1)
    else:
        sh.line.fill.background()
    return sh


def rect(slide, l, t, w, h, color):
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, l, t, w, h)
    fill(sh, color)
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


def add_p(tf, text, *, size=14, bold=False, color=INK, space=4):
    p = tf.add_paragraph()
    p.space_before = Pt(space)
    run(p, text, size=size, bold=bold, color=color)
    return p


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def footer(slide, n):
    tf = tb(slide, M, H - Inches(0.35), Inches(9), Inches(0.25))
    set_p(tf, "SafeNaija  ·  ThinkAI ’26  ·  Nigeria  ·  Cybersecurity", size=10, color=MUTED)
    num = tb(slide, W - M - Inches(1.1), H - Inches(0.35), Inches(1.1), Inches(0.25))
    set_p(num, f"{n} / {TOTAL}", size=10, color=MUTED, align=PP_ALIGN.RIGHT)


def bg(slide, dark=False):
    rect(slide, 0, 0, W, H, BRAND_DARK if dark else GRAY_BG)


def kicker(slide, text):
    tf = tb(slide, M, Inches(0.28), Inches(12), Inches(0.28))
    set_p(tf, text.upper(), size=11, bold=True, color=BRAND)
    bar = rect(slide, M, Inches(0.58), Inches(0.5), Inches(0.045), BRAND)


def title(slide, text, top=Inches(0.72), size=26):
    tf = tb(slide, M, top, Inches(12.3), Inches(0.5))
    set_p(tf, text, size=size, bold=True, color=INK)


def add_img(slide, path: Path, l, t, w, h=None):
    if not path.exists():
        return None
    if h is None:
        return slide.shapes.add_picture(str(path), l, t, width=w)
    return slide.shapes.add_picture(str(path), l, t, width=w, height=h)


def draw_table(slide, left, top, col_w, row_h, headers, rows):
    """Simple clear table from rectangles + text."""
    cols = len(headers)
    # header
    x = left
    for i, h in enumerate(headers):
        cell = rect(slide, x, top, col_w[i], row_h, HEADER_BG)
        tf = tb(slide, x + Inches(0.08), top + Inches(0.08), col_w[i] - Inches(0.12), row_h - Inches(0.1))
        set_p(tf, h, size=12, bold=True, color=WHITE)
        x += col_w[i]
    # rows
    for r_i, row in enumerate(rows):
        y = top + row_h * (r_i + 1)
        color = WHITE if r_i % 2 == 0 else ROW_ALT
        x = left
        for c_i, val in enumerate(row):
            rect(slide, x, y, col_w[c_i], row_h, color)
            # left border line
            border = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, Pt(0.75), row_h)
            fill(border, BORDER)
            tf = tb(slide, x + Inches(0.08), y + Inches(0.08), col_w[c_i] - Inches(0.12), row_h - Inches(0.1))
            set_p(tf, val, size=11, bold=(c_i == 0), color=INK)
            x += col_w[c_i]
    # outer bottom line
    total_w = sum(col_w)
    total_h = row_h * (len(rows) + 1)
    outline = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, total_w, total_h)
    outline.fill.background()
    outline.line.color.rgb = BORDER
    outline.line.width = Pt(1.25)


def flow_node(slide, l, t, w, h, text, color=BRAND, text_color=WHITE, size=11):
    sh = box(slide, l, t, w, h, color, None)
    tf = sh.text_frame
    tf.word_wrap = True
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    set_p(tf, text, size=size, bold=True, color=text_color, align=PP_ALIGN.CENTER)
    return sh


def arrow_right(slide, l, t):
    sh = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, l, t, Inches(0.35), Inches(0.22))
    fill(sh, BRAND)
    return sh


def arrow_down(slide, l, t):
    sh = slide.shapes.add_shape(MSO_SHAPE.DOWN_ARROW, l, t, Inches(0.22), Inches(0.28))
    fill(sh, BRAND)
    return sh


def build():
    prs = Presentation()
    prs.slide_width = W
    prs.slide_height = H
    blank = prs.slide_layouts[6]

    # 1 Title
    s = prs.slides.add_slide(blank)
    bg(s, dark=True)
    tf = tb(s, M, Inches(1.55), Inches(12), Inches(0.35))
    set_p(tf, "THINKAI ’26  ·  NIGERIA  ·  CYBERSECURITY", size=13, bold=True, color=RGBColor(0x93, 0xC5, 0xFD))
    tf = tb(s, M, Inches(2.15), Inches(12), Inches(0.85))
    set_p(tf, "SafeNaija", size=52, bold=True, color=WHITE)
    tf = tb(s, M, Inches(3.15), Inches(11.5), Inches(1.2))
    set_p(
        tf,
        "Prototype live: WhatsApp · Gmail · links · GitHub → Safe / Careful / Danger\nin English + Pidgin (and Hausa / Yoruba / Igbo packs).",
        size=18,
        color=RGBColor(0xDB, 0xEA, 0xFE),
    )
    tf = tb(s, M, Inches(4.7), Inches(11), Inches(0.8))
    set_p(
        tf,
        "Customers → students & SMBs  ·  Market strategy → campus then WhatsApp commerce  ·  Twist: Norton Genie standalone",
        size=14,
        color=RGBColor(0x93, 0xC5, 0xFD),
    )
    notes(s, "Open with demo promise; point to prototype slides mid-pitch.")

    # 2 Brief
    s = prs.slides.add_slide(blank)
    bg(s)
    kicker(s, "Assigned brief")
    title(s, "Nigeria × Cybersecurity — trust where people already chat")
    cards = [
        ("Country", "Nigeria\nMobile-first · WhatsApp commerce · digital payments"),
        ("Domain", "Cybersecurity\nConsumer trust layer — not a bank SOC"),
        ("Customers", "Students & SMBs\nNo security team · OTP / BVN / NIN risk"),
        ("Twist", "Norton Genie failed\nGlobal paste-bot · weak localisation"),
    ]
    for i, (h, body) in enumerate(cards):
        x = M + i * Inches(3.15)
        box(s, x, Inches(1.7), Inches(3.0), Inches(4.5), WHITE, BORDER)
        tf = tb(s, x + Inches(0.18), Inches(1.95), Inches(2.65), Inches(0.4))
        set_p(tf, h, size=14, bold=True, color=BRAND)
        tf = tb(s, x + Inches(0.18), Inches(2.5), Inches(2.65), Inches(3.3))
        set_p(tf, body, size=15, color=INK)
    footer(s, 2)

    # 3 Problem
    s = prs.slides.add_slide(blank)
    bg(s)
    kicker(s, "The problem")
    title(s, "Social engineering still wins on chat")
    stats = [
        ("₦25.85bn", "digital-payment fraud losses 2025\n(NIBSS / Punch)"),
        ("₦250bn+", "yearly cybercrime estimate\n(NITDA / Guardian)"),
        ("WhatsApp", "fake bank-care OTP theft\n(FIJ Feb 2025)"),
        ("SIM-swap", "syndicates drain accounts\n(Vanguard Jan 2025)"),
    ]
    for i, (big, small) in enumerate(stats):
        x = M + i * Inches(3.15)
        box(s, x, Inches(1.75), Inches(3.0), Inches(3.2), WHITE, BORDER)
        tf = tb(s, x + Inches(0.12), Inches(2.05), Inches(2.75), Inches(0.7))
        set_p(tf, big, size=22, bold=True, color=BRAND, align=PP_ALIGN.CENTER)
        tf = tb(s, x + Inches(0.12), Inches(2.9), Inches(2.75), Inches(1.6))
        set_p(tf, small, size=13, color=INK, align=PP_ALIGN.CENTER)
    tf = tb(s, M, Inches(5.2), Inches(12.2), Inches(1.0))
    set_p(
        tf,
        "Banks catch cards. Victims still hand OTPs on WhatsApp / SMS / Instagram — especially in Pidgin and local languages global tools miss.",
        size=14,
        color=MUTED,
    )
    footer(s, 3)

    # 4 Customers + clear market table
    s = prs.slides.add_slide(blank)
    bg(s)
    kicker(s, "Who we serve")
    title(s, "Customers — clear segments")
    headers = ["Customer", "Pain today", "How they buy", "What they need"]
    col_w = [Inches(2.4), Inches(3.5), Inches(3.0), Inches(3.4)]
    rows = [
        ["University students", "OTP / loan-app / GitHub secret scams", "Free campus plan", "Pidgin chat check + GitHub passport"],
        ["WhatsApp SMBs", "Fake buyer / payment proof / phishing links", "₦ low monthly SaaS", "Fast Safe/Careful/Danger on chat"],
        ["Campus clubs / NGOs", "Awareness with no SOC budget", "Pilot / grant pack", "Demo lab + case library"],
        ["Later: banks / telcos", "Need consumer education layer", "B2B API / white-label", "NDPA-safe local language packs"],
    ]
    draw_table(s, M, Inches(1.55), col_w, Inches(0.85), headers, rows)
    tf = tb(s, M, Inches(5.5), Inches(12.2), Inches(0.9))
    set_p(
        tf,
        "Beachhead = students + WhatsApp SMBs (no security team). Upsell path = campus licence → SMB SaaS → bank/telco API.",
        size=14,
        bold=True,
        color=BRAND_DARK,
    )
    footer(s, 4)

    # 5 Market strategy
    s = prs.slides.add_slide(blank)
    bg(s)
    kicker(s, "Market strategy")
    title(s, "How we win customers (GTM)")
    steps = [
        ("1. Seed", "Campus ambassadors\nDemo Chat + GitHub\nin 2–3 universities"),
        ("2. Prove", "Measure blocked OTP\nattempts & false alarms\nCase Library stories"),
        ("3. Monetise", "SMB WhatsApp plan\n₦2–5k / month starter\nInbox scan add-on"),
        ("4. Scale", "SEC / CBN advice hooks\nWhite-label for fintech\nNCC-CSIRT report path"),
    ]
    for i, (h, body) in enumerate(steps):
        x = M + i * Inches(3.15)
        box(s, x, Inches(1.7), Inches(3.0), Inches(3.5), WHITE, BORDER)
        tf = tb(s, x + Inches(0.18), Inches(1.95), Inches(2.65), Inches(0.4))
        set_p(tf, h, size=16, bold=True, color=BRAND)
        tf = tb(s, x + Inches(0.18), Inches(2.55), Inches(2.65), Inches(2.4))
        set_p(tf, body, size=14, color=INK)
    # market size strip
    box(s, M, Inches(5.4), Inches(12.3), Inches(1.0), BRAND_LIGHT, BORDER)
    tf = tb(s, M + Inches(0.25), Inches(5.55), Inches(11.8), Inches(0.7))
    set_p(
        tf,
        "Nigeria cybersecurity market ≈ USD 230m (2025) → USD 415m (2031, ~10% CAGR). We take the empty consumer/SMB trust layer — not enterprise SIEM.",
        size=13,
        color=INK,
    )
    footer(s, 5)

    # 6 GTM flowchart
    s = prs.slides.add_slide(blank)
    bg(s)
    kicker(s, "Go-to-market flowchart")
    title(s, "From first user → revenue")
    nodes = [
        (M, "Awareness\nCampus demo day"),
        (M + Inches(3.15), "Activation\nChat Demo BLOCK"),
        (M + Inches(6.3), "Retention\nWeekly scam digest"),
        (M + Inches(9.45), "Revenue\nSMB SaaS / API"),
    ]
    y = Inches(2.2)
    for i, (x, label) in enumerate(nodes):
        flow_node(s, x, y, Inches(2.7), Inches(1.15), label, BRAND if i < 3 else GREEN)
        if i < 3:
            arrow_right(s, x + Inches(2.75), y + Inches(0.45))
    # second row
    flow_node(s, M + Inches(1.5), Inches(4.0), Inches(3.2), Inches(1.0), "Feedback → phrase packs\n+ Case Library", BRAND_LIGHT, BRAND_DARK, 12)
    arrow_down(s, M + Inches(4.9), Inches(3.45))
    flow_node(s, M + Inches(5.5), Inches(4.0), Inches(3.2), Inches(1.0), "Partner channel\nClubs · NGOs · fintech", AMBER, WHITE, 12)
    flow_node(s, M + Inches(9.0), Inches(4.0), Inches(3.2), Inches(1.0), "Compliance path\nNDPA · EFCC advice", BRAND_DARK, WHITE, 12)
    tf = tb(s, M, Inches(5.5), Inches(12.2), Inches(0.9))
    set_p(tf, "Strategy: prove trust on campus → sell to WhatsApp SMBs → license language packs to larger platforms.", size=14, color=MUTED)
    footer(s, 6)

    # 7 Solution
    s = prs.slides.add_slide(blank)
    bg(s)
    kicker(s, "Solution")
    title(s, "One decision everywhere: Safe / Careful / Danger")
    triad = [
        (GREEN, "SAFE", "Looks okay\nStill verify big payments"),
        (AMBER, "CAREFUL", "Warning + why\nWhat to check next"),
        (RED, "DANGER", "Stop now\nNo OTP · no transfer"),
    ]
    for i, (c, h, body) in enumerate(triad):
        x = M + i * Inches(4.15)
        box(s, x, Inches(1.75), Inches(3.9), Inches(3.6), WHITE, BORDER)
        badge = box(s, x + Inches(0.9), Inches(2.05), Inches(2.1), Inches(0.55), c)
        tf = badge.text_frame
        set_p(tf, h, size=16, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        tf = tb(s, x + Inches(0.25), Inches(2.9), Inches(3.4), Inches(2.0))
        set_p(tf, body, size=16, color=INK, align=PP_ALIGN.CENTER)
    footer(s, 7)

    # 8 Engine flowchart
    s = prs.slides.add_slide(blank)
    bg(s)
    kicker(s, "How it works")
    title(s, "Scan engine flowchart")
    # inputs
    inputs = ["WhatsApp", "Gmail", "Link / crypto", "GitHub"]
    for i, label in enumerate(inputs):
        flow_node(s, M + i * Inches(3.15), Inches(1.65), Inches(2.9), Inches(0.7), label, BRAND_LIGHT, BRAND_DARK, 13)
        arrow_down(s, M + i * Inches(3.15) + Inches(1.3), Inches(2.4))
    flow_node(s, M + Inches(2.0), Inches(2.85), Inches(8.8), Inches(0.75), "Phrase packs (EN · Pidgin · Hausa · Yoruba · Igbo)  +  link visit / SEC  +  secret patterns", BRAND)
    arrow_down(s, M + Inches(6.35), Inches(3.7))
    flow_node(s, M + Inches(3.5), Inches(4.1), Inches(5.8), Inches(0.7), "Risk score → SAFE / CAREFUL / DANGER", BRAND_DARK)
    arrow_down(s, M + Inches(6.35), Inches(4.9))
    flow_node(s, M + Inches(2.0), Inches(5.3), Inches(8.8), Inches(0.7), "Plain advice (EN + Pidgin)  ·  Trust Chain  ·  next step (call bank / don’t send OTP)", GREEN)
    footer(s, 8)

    # 9 Prototype WhatsApp
    s = prs.slides.add_slide(blank)
    bg(s)
    kicker(s, "Prototype — live UI")
    title(s, "Messages: Pidgin OTP scam → BLOCK")
    pic = IMG / "proto-whatsapp-block.jpg"
    add_img(s, pic, M, Inches(1.4), Inches(8.6))
    box(s, M + Inches(8.85), Inches(1.4), Inches(3.5), Inches(5.0), WHITE, BORDER)
    tf = tb(s, M + Inches(9.05), Inches(1.65), Inches(3.15), Inches(4.5))
    set_p(tf, "What judges see", size=14, bold=True, color=BRAND)
    add_p(tf, "• Real channel connect (WhatsApp / Gmail / IG)", size=12)
    add_p(tf, "• Paste Pidgin OTP sample", size=12)
    add_p(tf, "• Decision: BLOCK · 0.95", size=12, bold=True, color=RED)
    add_p(tf, "• Advice in Pidgin: no share OTP / PIN / BVN", size=12)
    add_p(tf, "• Finding: otp_theft · pidgin", size=12)
    add_p(tf, "URL: http://127.0.0.1:5174/messages", size=11, color=MUTED)
    footer(s, 9)

    # 10 Prototype gallery 2
    s = prs.slides.add_slide(blank)
    bg(s)
    kicker(s, "Prototype — more screens")
    title(s, "Connect channels · language packs · GitHub bad-code picture")
    shots = [
        (IMG / "proto-messages-connect.jpg", "Connect WhatsApp / Gmail"),
        (IMG / "proto-languages.jpg", "EN · Pidgin · Hausa · Yoruba · Igbo"),
        (IMG / "proto-github-block.jpg", "GitHub secrets → BLOCK + code frame"),
    ]
    for i, (path, caption) in enumerate(shots):
        x = M + i * Inches(4.15)
        box(s, x, Inches(1.5), Inches(4.0), Inches(5.0), WHITE, BORDER)
        add_img(s, path, x + Inches(0.15), Inches(1.7), Inches(3.7))
        tf = tb(s, x + Inches(0.15), Inches(5.85), Inches(3.7), Inches(0.5))
        set_p(tf, caption, size=12, bold=True, color=BRAND, align=PP_ALIGN.CENTER)
    footer(s, 10)

    # 11 Competitive clear table
    s = prs.slides.add_slide(blank)
    bg(s)
    kicker(s, "Why us")
    title(s, "Clear comparison table")
    headers = ["Need in Nigeria", "Norton Genie standalone", "SafeNaija"]
    col_w = [Inches(3.5), Inches(4.3), Inches(4.5)]
    rows = [
        ["Local languages", "English-centric", "EN + Pidgin + Hausa/Yoruba/Igbo"],
        ["Where scam happens", "Paste-only app", "WhatsApp · Gmail · IG · links"],
        ["Student builders", "Not covered", "GitHub Risk Passport + bad-code pic"],
        ["Regulator cues", "Generic", "SEC demo pack · bank helpline advice"],
        ["Business model", "Free → paywall / pulled", "Campus free → SMB SaaS → API"],
        ["Privacy (NDPA)", "Cloud paste unclear", "Offline packs · permissioned inbox"],
    ]
    draw_table(s, M, Inches(1.5), col_w, Inches(0.7), headers, rows)
    footer(s, 11)

    # 12 Feasibility
    s = prs.slides.add_slide(blank)
    bg(s)
    kicker(s, "Feasibility")
    title(s, "Fits Nigeria’s rules & systems")
    items = [
        ("NDPA 2023", "Minimise data · local scan · user permission for inbox"),
        ("Cybercrimes Act", "Advise report paths (EFCC / police / NCC-CSIRT)"),
        ("CBN / NIBSS", "Align with NeFF fraud trends (SIM-swap, social eng.)"),
        ("SEC Nigeria", "Warn on unregistered investment / crypto pitches"),
    ]
    for i, (h, body) in enumerate(items):
        y = Inches(1.6) + i * Inches(1.15)
        box(s, M, y, Inches(12.3), Inches(1.05), WHITE, BORDER)
        tf = tb(s, M + Inches(0.3), y + Inches(0.15), Inches(11.7), Inches(0.35))
        set_p(tf, h, size=16, bold=True, color=BRAND)
        tf = tb(s, M + Inches(0.3), y + Inches(0.5), Inches(11.7), Inches(0.4))
        set_p(tf, body, size=14, color=INK)
    footer(s, 12)

    # 13 Future steps — clear
    s = prs.slides.add_slide(blank)
    bg(s)
    kicker(s, "Future steps")
    title(s, "Clear roadmap — what we do next")
    phases = [
        ("Now (MVP)", GREEN, ["Chat Demo + Messages live", "Gmail App Password connect", "GitHub bad-code frames", "Phrase packs EN/Pidgin + NG langs"]),
        ("+90 days", BRAND, ["Campus pilot 2–3 unis", "WhatsApp Cloud production", "Measure blocked OTP shares", "Ambassador playbook"]),
        ("+6 months", AMBER, ["SMB WhatsApp SaaS trial", "Live SEC registry hook", "Expand Hausa/Yoruba/Igbo", "Offline mobile pack"]),
        ("+12 months", BRAND_DARK, ["Bank/telco API talks", "White-label language packs", "NCC-CSIRT report assist", "West Africa localisation"]),
    ]
    for i, (h, color, bullets) in enumerate(phases):
        x = M + i * Inches(3.15)
        box(s, x, Inches(1.55), Inches(3.0), Inches(5.0), WHITE, BORDER)
        head = box(s, x, Inches(1.55), Inches(3.0), Inches(0.55), color)
        tf = head.text_frame
        set_p(tf, h, size=13, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        tf = tb(s, x + Inches(0.18), Inches(2.3), Inches(2.65), Inches(4.0))
        for j, b in enumerate(bullets):
            p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
            p.space_after = Pt(8)
            run(p, "•  ", size=13, bold=True, color=color)
            run(p, b, size=13, color=INK)
    footer(s, 13)

    # 14 Roadmap flowchart
    s = prs.slides.add_slide(blank)
    bg(s)
    kicker(s, "Future steps flowchart")
    title(s, "Build → pilot → product → partners")
    chain = [
        ("Build\nMVP demo", BRAND),
        ("Pilot\nCampuses", BRAND),
        ("Product\nSMB SaaS", GREEN),
        ("Partners\nBank / telco API", BRAND_DARK),
    ]
    y = Inches(2.3)
    for i, (label, c) in enumerate(chain):
        x = M + i * Inches(3.15)
        flow_node(s, x, y, Inches(2.85), Inches(1.3), label, c, WHITE, 14)
        if i < 3:
            arrow_right(s, x + Inches(2.9), y + Inches(0.55))
    # success metrics under
    box(s, M, Inches(4.2), Inches(12.3), Inches(2.2), WHITE, BORDER)
    tf = tb(s, M + Inches(0.3), Inches(4.4), Inches(11.7), Inches(1.8))
    set_p(tf, "Success metrics we track", size=15, bold=True, color=BRAND)
    add_p(tf, "1) % of OTP scam samples correctly BLOCKED   2) False BLOCK rate on clean chat   3) Campus weekly active users", size=13)
    add_p(tf, "4) SMB paid conversions after 30-day trial   5) Time-to-advice < 2 seconds on offline packs", size=13)
    footer(s, 14)

    # 15 Metrics / evidence
    s = prs.slides.add_slide(blank)
    bg(s)
    kicker(s, "Evidence")
    title(s, "What the prototype already proves")
    headers = ["Capability", "Status", "Demo proof"]
    col_w = [Inches(4.0), Inches(3.0), Inches(5.3)]
    rows = [
        ["Pidgin / local OTP detection", "Working", "Messages → BLOCK 0.95 on GTBank OTP sample"],
        ["Gmail inbox scan", "Working", "App Password connect · HDFC phishing BLOCK"],
        ["GitHub secret picture", "Working", "demo-student repo → highlighted keys"],
        ["Chat Demo (WA / IG)", "Working", "Hausa / Yoruba / Igbo / Pidgin scenarios"],
        ["Link / website visit", "Working", "Live fetch + SEC demo cues"],
    ]
    draw_table(s, M, Inches(1.55), col_w, Inches(0.75), headers, rows)
    footer(s, 15)

    # 16 Ask
    s = prs.slides.add_slide(blank)
    bg(s, dark=True)
    tf = tb(s, M, Inches(1.8), Inches(12), Inches(0.4))
    set_p(tf, "CLOSING ASK", size=14, bold=True, color=RGBColor(0x93, 0xC5, 0xFD))
    tf = tb(s, M, Inches(2.4), Inches(12), Inches(1.5))
    set_p(
        tf,
        "Mentor a campus pilot so SafeNaija reaches\nstudents before the next OTP scam.",
        size=28,
        bold=True,
        color=WHITE,
    )
    tf = tb(s, M, Inches(4.4), Inches(12), Inches(1.3))
    set_p(
        tf,
        "Customers: students & WhatsApp SMBs first.\nStrategy: campus proof → SMB SaaS → bank/telco API.\nPrototype is runnable today on localhost:5174.",
        size=16,
        color=RGBColor(0xDB, 0xEA, 0xFE),
    )
    tf = tb(s, M, Inches(6.1), Inches(12), Inches(0.4))
    set_p(tf, "Q&A · Demo · Case Library", size=14, color=RGBColor(0x93, 0xC5, 0xFD))
    notes(s, "End on ask + offer live Chat Demo.")

    # write outputs
    out_downloads = DOWNLOADS / "SafeNaija.pptx"
    out_desktop = DESKTOP / "SafeNaija.pptx"
    out_pitch = DESKTOP / "SafeNaija_ThinkAI26_Pitch.pptx"
    out_repo = OUT_DIR / "SafeNaija.pptx"
    for path in (out_downloads, out_desktop, out_pitch, out_repo):
        prs.save(str(path))
        print("saved", path, path.stat().st_size)

    # Mermaid companion
    md = """# SafeNaija — flowcharts (ThinkAI ’26)

Open in [mermaid.live](https://mermaid.live).

## 1. Scan engine

```mermaid
flowchart TD
  WA[WhatsApp] --> ENG[SafeNaija engine]
  GM[Gmail] --> ENG
  LK[Link / crypto] --> ENG
  GH[GitHub] --> ENG
  ENG --> PH[Phrase packs\\nEN · Pidgin · Hausa · Yoruba · Igbo]
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
"""
    for path in (DESKTOP / "SafeNaija_diagrams.md", OUT_DIR / "SafeNaija_diagrams.md", DOWNLOADS / "SafeNaija_diagrams.md"):
        path.write_text(md, encoding="utf-8")
        print("md", path)


if __name__ == "__main__":
    build()
