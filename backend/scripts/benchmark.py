"""
Reproduce SafeO's internal detection and false-positive benchmark.

Usage (from backend/):
    PYTHONPATH=. python scripts/benchmark.py

Attack set: the 28 payloads in safeo_backend/routes/simulate.py (8 classes).
Benign set: 20 hand-written finance, CRM and support messages (English, Arabic,
Urdu, Arabizi) defined below. A result counts as "flagged" if the decision is
WARN, BLOCK or SANITIZE.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

logging.disable(logging.CRITICAL)

from safeo_backend.routes.simulate import PAYLOADS, _generic_waf_check  # noqa: E402
from safeo_backend.core.ml.risk_scorer import calculate_risk_score  # noqa: E402

FLAGGED = {"warn", "block", "sanitize"}
FIXED_TS = datetime(2026, 9, 30, 10, 0, tzinfo=timezone.utc)

BENIGN = [
    "normal support request for invoice clarification",
    "Please update my billing address to 12 Marina Walk, Dubai",
    "Transfer AED 500 to Ahmed for rent, thanks",
    "Can you resend the payment receipt for order 4471?",
    "Meeting moved to 3pm, please confirm attendance",
    "Customer asked about refund status for last week's purchase",
    "Hi, I would like to open a savings account",
    "What is the exchange rate from USD to AED today?",
    "Please add Sara (sara@example.com) as a new lead",
    "Invoice #2291 paid via bank transfer on 14 March",
    "My card was declined at the supermarket, can you check?",
    "Reminder: quarterly VAT filing due next Friday",
    "Lead from website: interested in solar panel pricing",
    "Please select the premium plan for our team of 10",
    "Order 55 dropped off at warehouse, update the table please",
    "مرحباً، أحتاج مساعدة في الفاتورة",
    "أريد تحويل ٢٠٠ درهم إلى حساب أخي",
    "شكراً، تم استلام الدفعة",
    "آپ کی رسید ای میل کر دی گئی ہے",
    "kifak, baddi a3ref wen sar el refund taba3i",
]


def _score(text: str, user_id: str):
    risk, decision, *_ = calculate_risk_score(text, user_id=user_id, timestamp=FIXED_TS)
    return risk, decision


def main() -> None:
    print("== Attack payloads ==")
    total = detected = waf_detected = 0
    multilingual_total = multilingual_detected = 0
    for attack_type, items in PAYLOADS.items():
        hits = 0
        for i, (payload, script) in enumerate(items):
            _, decision = _score(payload, user_id=f"atk_{attack_type}_{i}")
            hit = decision in FLAGGED
            hits += hit
            waf_detected += _generic_waf_check(payload)
            if script != "latin":
                multilingual_total += 1
                multilingual_detected += hit
        total += len(items)
        detected += hits
        print(f"  {attack_type:<20} {hits}/{len(items)}")
    print(f"  SafeO detection:        {detected}/{total} ({100 * detected / total:.1f}%)")
    print(f"  Regex-only WAF:         {waf_detected}/{total} ({100 * waf_detected / total:.1f}%)")
    print(f"  Non-Latin / mixed only: {multilingual_detected}/{multilingual_total}")

    print("\n== Benign messages ==")
    flagged = []
    for i, text in enumerate(BENIGN):
        risk, decision = _score(text, user_id=f"benign_{i}")
        if decision in FLAGGED:
            flagged.append((text, risk, decision))
    print(f"  False positives: {len(flagged)}/{len(BENIGN)}")
    for text, risk, decision in flagged:
        print(f"    {decision.upper():<5} {risk:.3f}  {text}")


if __name__ == "__main__":
    main()
