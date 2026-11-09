#!/usr/bin/env python3
"""Build SafeNaija pitch deck (M8 blue visual system)."""
from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

OUT_DIR = Path(__file__).resolve().parent
DESKTOP = Path.home() / "Desktop"
IMG = OUT_DIR / "img"

# M8 deck colours
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
FONT_TITLE = "Calibri"

W = Inches(13.333)
H = Inches(7.5)
M = Inches(0.6)


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
    tf.margin_left = tf.margin_right = Inches(0.05)
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


def add_p(tf, text, *, size=15, bold=False, color=INK, space=8):
    p = tf.add_paragraph()
    p.space_before = Pt(space)
    run(p, text, size=size, bold=bold, color=color)
    return p


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def footer(slide, n, total=16):
    tf = tb(slide, M, H - Inches(0.4), Inches(6), Inches(0.3))
    set_p(tf, "SafeNaija  ·  ThinkAI ’26  ·  Nigeria", size=10, color=MUTED)
    num = tb(slide, W - M - Inches(1.2), H - Inches(0.4), Inches(1.2), Inches(0.3))
    set_p(num, f"{n} / {total}", size=10, color=MUTED, align=PP_ALIGN.RIGHT)


def bg(slide, dark=False):
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, W, H)
    fill(sh, BRAND_DARK if dark else GRAY_BG)
    return sh


def kicker(slide, text):
    tf = tb(slide, M, Inches(0.35), Inches(10), Inches(0.35))
    set_p(tf, text.upper(), size=11, bold=True, color=BRAND)
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, M, Inches(0.72), Inches(0.55), Inches(0.05))
    fill(bar, BRAND)


def title(slide, text, top=Inches(0.9), size=28):
    tf = tb(slide, M, top, Inches(12), Inches(0.7))
    set_p(tf, text, size=size, bold=True, color=INK)
    return tf


def bullets(slide, items, l, t, w, h, size=15):
    tf = tb(slide, l, t, w, h)
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(8)
        run(p, "•  ", size=size, bold=True, color=BRAND)
        run(p, item, size=size, color=INK)


def try_picture(slide, name, l, t, w, h):
    path = IMG / name
    if path.exists():
        slide.shapes.add_picture(str(path), l, t, width=w)
        return True
    ph = box(slide, l, t, w, h, BRAND_LIGHT, BORDER)
    tf = ph.text_frame
    tf.word_wrap = True
    set_p(tf, f"[Demo screenshot: {name}]", size=12, color=MUTED, align=PP_ALIGN.CENTER)
    return False


def build():
    prs = Presentation()
    prs.slide_width = W
    prs.slide_height = H
    blank = prs.slide_layouts[6]
    total = 16

    # 1 Title
    s = prs.slides.add_slide(blank)
    bg(s, dark=True)
    tf = tb(s, M, Inches(1.8), Inches(12), Inches(0.4))
    set_p(tf, "THINKAI ’26  ·  NIGERIA  ·  IMAGINE CUP MVP", size=12, bold=True, color=RGBColor(0x93, 0xC5, 0xFD))
    tf = tb(s, M, Inches(2.4), Inches(12), Inches(1))
    set_p(tf, "SafeNaija", size=54, bold=True, color=WHITE)
    tf = tb(s, M, Inches(3.5), Inches(11), Inches(1.2))
    set_p(
        tf,
        "Protects students and small businesses on WhatsApp, email, and GitHub — explaining scams in plain English and Pidgin before money or secrets are lost.",
        size=20,
        color=RGBColor(0xDB, 0xEA, 0xFE),
    )
    tf = tb(s, M, Inches(5.2), Inches(10), Inches(0.4))
    set_p(tf, "Hackathon pitch  ·  ~8 minutes  ·  16 slides", size=14, color=RGBColor(0x93, 0xC5, 0xFD))
    notes(
        s,
        "Open with the one-line pitch. Say: we don’t build another SOC dashboard — we sit on the chats people already use.",
    )

    # 2 Victim story hook
    s = prs.slides.add_slide(blank)
    bg(s)
    kicker(s, "Opening hook")
    title(s, "A WhatsApp “bank agent” emptied her account")
    bullets(
        s,
        [
            "A Plateau woman complained about ALAT by Wema on X.",
            "A WhatsApp number then claimed to be bank customer care.",
            "She opened a lookalike login link. N102,000 left her account.",
            "Source: Foundation for Investigative Journalism (FIJ), 20 Feb 2025.",
        ],
        M,
        Inches(2.0),
        Inches(11.5),
        Inches(4),
        size=18,
    )
    notes(
        s,
        "Tell it plainly. Link: https://fij.ng/article/alat-by-wema-fraudster-steals-plateau-womans-n102000/ — do not invent extra details.",
    )
    footer(s, 2, total)

    # 3 Problem Nigeria
    s = prs.slides.add_slide(blank)
    bg(s)
    kicker(s, "The problem in Nigeria")
    title(s, "Fraud is rising on the same channels people trust")
    cards = [
        ("N52.3bn", "lost to bank fraud in 2024\n(Punch citing NIBSS / FITC, Jul 2025)"),
        ("+45%", "attempted fraud in 2023\nmobile & online most hit\n(Premium Times / NIBSS, Oct 2025)"),
        ("SIM swap", "Police in Katsina arrested a 4-person SIM-swap syndicate, Jan 2025\n(Vanguard / NAN)"),
        ("47 apps", "unregistered loan apps delisted from Play Store by May 2024; many moved to APK links\n(Nairametrics)"),
    ]
    for i, (big, small) in enumerate(cards):
        x = M + (i % 2) * Inches(6.2)
        y = Inches(1.9) + (i // 2) * Inches(2.2)
        box(s, x, y, Inches(5.9), Inches(2.0), WHITE, BORDER)
        tf = tb(s, x + Inches(0.25), y + Inches(0.25), Inches(5.4), Inches(0.55))
        set_p(tf, big, size=26, bold=True, color=BRAND)
        tf = tb(s, x + Inches(0.25), y + Inches(0.85), Inches(5.4), Inches(1.0))
        set_p(tf, small, size=13, color=INK)
    notes(
        s,
        "Cite every number. Punch: https://punchng.com/protecting-your-bank-apps-from-hackers/ · Premium Times Oct 2025 · Vanguard 16 Jan 2025 · Nairametrics 12 Jun 2024.",
    )
    footer(s, 3, total)

    # 4 Two more stories
    s = prs.slides.add_slide(blank)
    bg(s)
    kicker(s, "Real cases")
    title(s, "Two more documented stories")
    box(s, M, Inches(1.9), Inches(5.9), Inches(4.2), WHITE, BORDER)
    tf = tb(s, M + Inches(0.25), Inches(2.1), Inches(5.4), Inches(3.8))
    set_p(tf, "SIM-swap syndicate — Katsina", size=18, bold=True, color=BRAND)
    add_p(tf, "Police arrested four suspects who swapped SIMs to drain bank accounts.", size=15)
    add_p(tf, "Recovered: 32 SIM cards, phones, victim data.", size=15)
    add_p(tf, "Source: Vanguard / NAN, 16 Jan 2025.", size=13, color=MUTED)
    box(s, M + Inches(6.2), Inches(1.9), Inches(5.9), Inches(4.2), WHITE, BORDER)
    tf = tb(s, M + Inches(6.45), Inches(2.1), Inches(5.4), Inches(3.8))
    set_p(tf, "Forced loan via digital lender app", size=18, bold=True, color=BRAND)
    add_p(tf, "Ijeoma asked for N100,000; the app disbursed N1 million.", size=15)
    add_p(tf, "She was told to repay N1.118m within three days.", size=15)
    add_p(tf, "Source: Nairametrics, 14 Feb 2025.", size=13, color=MUTED)
    notes(
        s,
        "SIM swap: https://www.vanguardngr.com/2025/01/police-nab-syndicate-using-sim-swap-to-defraud-bank-customers/ · Loan: https://nairametrics.com/2025/02/14/licensed-loan-app-companies-in-nigeria-surge-to-380-amid-concerns-over-shady-practices/",
    )
    footer(s, 4, total)

    # 5 Who is affected
    s = prs.slides.add_slide(blank)
    bg(s)
    kicker(s, "Who is affected")
    title(s, "Students and small businesses first")
    box(s, M, Inches(2.0), Inches(5.9), Inches(3.8), WHITE, BORDER)
    tf = tb(s, M + Inches(0.3), Inches(2.2), Inches(5.3), Inches(3.4))
    set_p(tf, "Students & campus founders", size=20, bold=True, color=BRAND)
    add_p(tf, "Live on WhatsApp and Instagram.", size=16)
    add_p(tf, "Ship school / startup code to public GitHub.", size=16)
    add_p(tf, "GitGuardian: 23.8M new secrets on public GitHub in 2024 (+25% YoY).", size=14, color=MUTED)
    box(s, M + Inches(6.2), Inches(2.0), Inches(5.9), Inches(3.8), WHITE, BORDER)
    tf = tb(s, M + Inches(6.5), Inches(2.2), Inches(5.3), Inches(3.4))
    set_p(tf, "Small businesses", size=20, bold=True, color=BRAND)
    add_p(tf, "Sell and collect payments on WhatsApp.", size=16)
    add_p(tf, "No security team; refunds are slow.", size=16)
    add_p(tf, "Premium Times (2025): SIM-swap losses often hard to recover.", size=14, color=MUTED)
    notes(s, "GitGuardian State of Secrets Sprawl 2025. Keep the focus on people, not enterprise SOC buyers.")
    footer(s, 5, total)

    # 6 Gap
    s = prs.slides.add_slide(blank)
    bg(s)
    kicker(s, "What already exists")
    title(s, "Useful tools — still a gap for Nigerian chat")
    rows = [
        ("Norton Genie", "Paste check for scams — strong, not Nigeria/Pidgin-first"),
        ("WhatsApp / Meta alerts", "Some scam warnings — not a full OTP/BVN phrase coach"),
        ("Airtel Spam Alert", "Network SMS/call spam — not WhatsApp body text"),
        ("Prembly FraudLens", "Fraud intelligence for institutions"),
        ("Reporta", "Bank/fintech shared fraud registry — B2B"),
        ("GitHub secret scanning", "Great for repos — not for WhatsApp OTP scams"),
    ]
    bullets(
        s,
        [f"{a}: {b}" for a, b in rows] + ["Gap: one local decision layer across WhatsApp + email + GitHub, in Pidgin."],
        M,
        Inches(1.85),
        Inches(12),
        Inches(4.8),
        size=15,
    )
    notes(s, "Be fair to competitors. Our wedge is channel + language + student/SMB UX together.")
    footer(s, 6, total)

    # 7 Solution
    s = prs.slides.add_slide(blank)
    bg(s)
    kicker(s, "Our solution")
    title(s, "One decision everywhere")
    for i, (label, color, desc) in enumerate(
        [
            ("SAFE", GREEN, "Looks okay — still verify big payments"),
            ("CAREFUL", AMBER, "Warning + why + what to check"),
            ("DANGER", RED, "Stop. Do not send OTP or money"),
        ]
    ):
        x = M + i * Inches(4.1)
        box(s, x, Inches(2.1), Inches(3.9), Inches(3.5), WHITE, BORDER)
        badge = box(s, x + Inches(0.3), Inches(2.4), Inches(3.3), Inches(0.7), color)
        tf = badge.text_frame
        set_p(tf, label, size=22, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        tf = tb(s, x + Inches(0.3), Inches(3.4), Inches(3.3), Inches(1.8))
        set_p(tf, desc, size=16, color=INK)
        add_p(tf, "+ plain-language next step", size=14, color=MUTED)
    notes(s, "Map SAFE/CAREFUL/DANGER to ALLOW/WARN/BLOCK in the product demo.")
    footer(s, 7, total)

    # 8 Features overview
    s = prs.slides.add_slide(blank)
    bg(s)
    kicker(s, "Features")
    title(s, "What SafeNaija does")
    feats = [
        "WhatsApp scanner — ALLOW / WARN / BLOCK in English & Pidgin",
        "Email / paste checker — subject, body, links",
        "Link & fake loan-app / APK checker — visits the page",
        "OTP & bank-impersonation phrase pack (OTP, BVN, NIN, bank names)",
        "GitHub repo scanner — keys, .env, risky patterns + bad-code picture",
        "Student Risk Passport — score + top 3 fixes",
    ]
    bullets(s, feats, M, Inches(1.9), Inches(12), Inches(4.5), size=17)
    notes(s, "One slide overview; next slides zoom if judges want depth. Chat demo page shows the phone UI.")
    footer(s, 8, total)

    # 9 Feature detail A
    s = prs.slides.add_slide(blank)
    bg(s)
    kicker(s, "Features · channels")
    title(s, "WhatsApp, email, links")
    bullets(
        s,
        [
            "WhatsApp: visual chat demo + Cloud API webhook path",
            "Gmail: App Password / OAuth connect; scan recent inbox",
            "Paste any SMS / DM when you cannot connect an account",
            "Live website visit: title, forms, password fields, APK links",
            "Phrase packs cover Pidgin OTP theft and investment bait",
        ],
        M,
        Inches(1.9),
        Inches(12),
        Inches(4.5),
        size=17,
    )
    notes(s, "Demo Chat Demo page for WhatsApp/Instagram phones; Messages page for real Gmail.")
    footer(s, 9, total)

    # 10 Feature detail B
    s = prs.slides.add_slide(blank)
    bg(s)
    kicker(s, "Features · code & passport")
    title(s, "GitHub scan + Student Risk Passport")
    bullets(
        s,
        [
            "Paste a repo URL → fetch README / config / .env samples",
            "Flag API keys, AWS patterns, database URLs",
            "Show a picture of the bad code with highlighted lines",
            "Risk Passport: one score and the top three fixes",
            "Built for campus founders who ship public repos",
        ],
        M,
        Inches(1.9),
        Inches(7),
        Inches(4.5),
        size=17,
    )
    try_picture(s, "safenaija-demo-github-critical.png", Inches(8.2), Inches(1.9), Inches(4.5), Inches(4.5))
    notes(s, "Use the Links page screenshot if available. Stress rotate keys immediately.")
    footer(s, 10, total)

    # 11 Demo
    s = prs.slides.add_slide(blank)
    bg(s)
    kicker(s, "Demo")
    title(s, "Three screens in sixty seconds")
    labels = [
        ("1. WhatsApp BLOCK", "safenaija-demo-whatsapp-block.png", "Pidgin OTP theft → BLOCK"),
        ("2. Chat phone demo", "safenaija-demo-whatsapp-block.png", "Phone UI shows the warn"),
        ("3. GitHub critical", "safenaija-demo-github-critical.png", "Bad-code picture + keys"),
    ]
    for i, (lab, img, cap) in enumerate(labels):
        x = M + i * Inches(4.15)
        tf = tb(s, x, Inches(1.75), Inches(3.9), Inches(0.35))
        set_p(tf, lab, size=14, bold=True, color=BRAND)
        try_picture(s, img, x, Inches(2.15), Inches(3.9), Inches(3.6))
        tf = tb(s, x, Inches(6.3), Inches(3.9), Inches(0.4))
        set_p(tf, cap, size=12, color=MUTED)
    notes(s, "Live path: /chat-demo → OTP scenario, then /links → GitHub repo. Mention Gmail inbox scan if connected.")
    footer(s, 11, total)

    # 12 Metrics
    s = prs.slides.add_slide(blank)
    bg(s)
    kicker(s, "How we measure it")
    title(s, "Internal Nigerian-style phrase benchmark")
    metrics = [
        ("44", "scam phrases\nEN · Pidgin · Hausa · Yoruba · Igbo"),
        ("100%", "scam set flagged\n(BLOCK or WARN)"),
        ("0 / 20", "false BLOCKs\non benign campus / bank texts"),
        ("7 / 44", "caught by a naive\nEnglish keyword baseline"),
    ]
    for i, (big, small) in enumerate(metrics):
        x = M + i * Inches(3.1)
        box(s, x, Inches(2.0), Inches(2.95), Inches(3.6), WHITE, BORDER)
        tf = tb(s, x + Inches(0.15), Inches(2.3), Inches(2.65), Inches(1.0))
        set_p(tf, big, size=28, bold=True, color=BRAND, align=PP_ALIGN.CENTER)
        tf = tb(s, x + Inches(0.15), Inches(3.5), Inches(2.65), Inches(1.8))
        set_p(tf, small, size=13, color=INK, align=PP_ALIGN.CENTER)
    notes(
        s,
        "Be honest: this is our phrase-pack regression set, not a national dataset. Generic baseline = simple English keywords like otp/password/click here.",
    )
    footer(s, 12, total)

    # 13 Limitations
    s = prs.slides.add_slide(blank)
    bg(s)
    kicker(s, "Limitations and risks")
    title(s, "What can still go wrong")
    bullets(
        s,
        [
            "Attackers change wording faster than any fixed list.",
            "Hausa / Yoruba / Igbo coverage is smaller than Pidgin/English today.",
            "Scanning messages needs clear user permission and local-first defaults.",
            "Website visits can fail on blockers; we still score URL + pasted text.",
            "We do not replace banks, telcos, or the police.",
        ],
        M,
        Inches(1.9),
        Inches(12),
        Inches(4.5),
        size=17,
    )
    notes(s, "Judges respect honesty. Mention offline packs and permissioned channel connect.")
    footer(s, 13, total)

    # 14 Roadmap
    s = prs.slides.add_slide(blank)
    bg(s)
    kicker(s, "Roadmap")
    title(s, "Next steps")
    bullets(
        s,
        [
            "Now: campus demo + Gmail / WhatsApp chat lab",
            "Q1: pilot with student founders and one SMB WhatsApp Business line",
            "Q2: live SEC.gov.ng verification hook + wider language packs",
            "Later: offline mobile pack for low-connectivity users",
        ],
        M,
        Inches(1.9),
        Inches(12),
        Inches(4.5),
        size=18,
    )
    notes(s, "Point to diagrams.md gantt if projected.")
    footer(s, 14, total)

    # 15 Closing ask
    s = prs.slides.add_slide(blank)
    bg(s, dark=True)
    tf = tb(s, M, Inches(2.2), Inches(12), Inches(1))
    set_p(tf, "Closing ask", size=18, bold=True, color=RGBColor(0x93, 0xC5, 0xFD))
    tf = tb(s, M, Inches(2.9), Inches(11.5), Inches(2))
    set_p(
        tf,
        "Mentor us on a campus pilot, and help us put SafeNaija in front of students before the next OTP scam lands.",
        size=28,
        bold=True,
        color=WHITE,
    )
    tf = tb(s, M, Inches(5.3), Inches(11), Inches(0.5))
    set_p(tf, "SafeNaija  ·  ThinkAI ’26  ·  diagrams.md + live demo on localhost", size=14, color=RGBColor(0x93, 0xC5, 0xFD))
    notes(s, "End on the human ask. Offer to run the chat demo live.")

    # 16 Sources
    s = prs.slides.add_slide(blank)
    bg(s)
    kicker(s, "Sources")
    title(s, "Cited on this deck")
    bullets(
        s,
        [
            "Punch, 2 Jul 2025 — N52.3bn bank fraud 2024 (NIBSS / FITC)",
            "Premium Times, 22 Oct 2025 — NIBSS attempted fraud +45% in 2023",
            "Vanguard / NAN, 16 Jan 2025 — Katsina SIM-swap arrests",
            "FIJ, 20 Feb 2025 — ALAT WhatsApp phishing, N102,000 loss",
            "Nairametrics, 12 Jun 2024 & 14 Feb 2025 — loan apps / APK / Ijeoma case",
            "GitGuardian Secrets Sprawl 2025 — 23.8M new GitHub secrets in 2024",
        ],
        M,
        Inches(1.85),
        Inches(12),
        Inches(4.8),
        size=15,
    )
    notes(s, "Leave this slide on screen during Q&A if needed.")
    footer(s, 16, total)

    out1 = OUT_DIR / "SafeNaija_ThinkAI26_Pitch.pptx"
    out2 = DESKTOP / "SafeNaija_ThinkAI26_Pitch.pptx"
    prs.save(out1)
    prs.save(out2)
    return out1, out2


if __name__ == "__main__":
    a, b = build()
    print("saved", a)
    print("saved", b)
