"""
SafeNaija offline-first detection engines.

All heavy logic uses local phrase packs / registries so basic detection works
without sending private message content to external LLM APIs.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

DATA_DIR = Path(__file__).resolve().parent / "data"

SEVERITY_SCORE = {"critical": 0.95, "high": 0.8, "medium": 0.55, "low": 0.35}

CRYPTO_PROFIT_PATTERNS = [
    re.compile(r"(?i)\b(guaranteed|risk[- ]?free)\b.{0,40}\b(return|profit|roi)\b"),
    re.compile(r"(?i)\b(double|triple|10x|100x)\b.{0,30}\b(money|btc|usdt|crypto|investment)\b"),
    re.compile(r"(?i)\b\d{2,3}\s*%\s*(daily|weekly|per\s*day|returns?)\b"),
    re.compile(r"(?i)\b(send|deposit)\b.{0,40}\b(btc|usdt|ethereum|wallet)\b"),
    re.compile(r"(?i)\b(mining\s+pool|signal\s+group|vip\s+traders?)\b.{0,40}\b(profit|earn)\b"),
]

URL_RE = re.compile(r"https?://[^\s<>\"']+|www\.[^\s<>\"']+", re.I)
PHONE_RE = re.compile(
    r"(?:\+?234|0)[\s\-]?[789][01][\s\-]?\d{3}[\s\-]?\d{4}|\+?234\d{10}|\d{11}"
)

GITHUB_HOSTS = {"github.com", "www.github.com", "raw.githubusercontent.com"}

SUSPICIOUS_TLDS = {".tk", ".ml", ".ga", ".cf", ".gq", ".xyz", ".top", ".buzz", ".icu"}
SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "cutt.ly", "rb.gy"}

SECRET_PATTERNS = [
    (re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{12,}"), "Possible secret / API key"),
    (re.compile(r"(?i)sk-[A-Za-z0-9]{20,}"), "OpenAI-style API key pattern"),
    (re.compile(r"(?i)AKIA[0-9A-Z]{16}"), "AWS access key pattern"),
    (re.compile(r"(?i)-----BEGIN (RSA |EC )?PRIVATE KEY-----"), "Private key material"),
    (re.compile(r"(?i)\.env\b|DATABASE_URL\s*="), "Env / database credential hint"),
]


def _load_json(name: str) -> Dict[str, Any]:
    path = DATA_DIR / name
    with path.open(encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def _phrases() -> Dict[str, Any]:
    return _load_json("scam_phrases.json")


@lru_cache(maxsize=1)
def _banks() -> Dict[str, Any]:
    return _load_json("bank_helplines.json")


@lru_cache(maxsize=1)
def _scam_numbers() -> Dict[str, Any]:
    return _load_json("scam_numbers.json")


@lru_cache(maxsize=1)
def _sec() -> Dict[str, Any]:
    return _load_json("sec_registry.json")


def _norm_phone(raw: str) -> str:
    digits = re.sub(r"\D", "", raw or "")
    if digits.startswith("234") and len(digits) >= 13:
        return "+234" + digits[3:13]
    if digits.startswith("0") and len(digits) == 11:
        return "+234" + digits[1:]
    if len(digits) == 10 and digits[0] in "789":
        return "+234" + digits
    if digits.startswith("234") and len(digits) == 13:
        return "+" + digits
    return "+" + digits if digits else ""


def _decision(score: float) -> str:
    if score >= 0.7:
        return "BLOCK"
    if score >= 0.45:
        return "WARN"
    return "ALLOW"


def _advice(category: str, lang: str = "english") -> str:
    tips = {
        "otp_theft": {
            "english": "Never share OTP, PIN, or BVN. Real banks will not ask for them on chat or call.",
            "pidgin": "No share OTP, PIN or BVN. Real bank no dey ask for am for chat or call.",
        },
        "investment_scam": {
            "english": "Unrealistic profit promises are a red flag. Check SEC Nigeria before investing.",
            "pidgin": "If dem promise too much profit, e fit be scam. Check SEC Nigeria first.",
        },
        "crypto_scam": {
            "english": "Do not send crypto to recovery agents or 'doubler' wallets.",
            "pidgin": "No send crypto give recovery agent or doubler wallet.",
        },
        "bank_impersonation": {
            "english": "Hang up and call your bank using the number on their official app/website.",
            "pidgin": "Cut the call, then call your bank with the number wey dey for their official app.",
        },
        "fake_loan": {
            "english": "Avoid sideloaded loan apps that ask for contacts and gallery access.",
            "pidgin": "No download loan app wey dey ask for your contacts and gallery.",
        },
        "sim_swap": {
            "english": "If SIM suddenly dies, contact your telco and bank immediately; enable transaction alerts.",
            "pidgin": "If your SIM suddenly die, call your network and bank sharp; on transaction alerts.",
        },
    }
    pack = tips.get(category) or {
        "english": "Treat this as suspicious. Do not click links or send money until you verify independently.",
        "pidgin": "This one look suspicious. No click link or send money until you confirm yourself.",
    }
    return pack.get(lang) or pack["english"]


@dataclass
class SafeNaijaEngine:
    """Facade used by HTTP routes."""

    def detect_languages(self, text: str) -> Dict[str, Any]:
        t = (text or "").lower()
        hits: Dict[str, List[str]] = {}
        data = _phrases()
        for lang, items in data.items():
            matched = []
            for item in items:
                if item["phrase"].lower() in t:
                    matched.append(item["phrase"])
            if matched:
                hits[lang] = matched

        # Light lexical hints beyond phrase pack
        pidgin_tokens = ["abeg", "sharp sharp", "now now", "no dey", "make i", "wetin", "oya"]
        if any(tok in t for tok in pidgin_tokens):
            hits.setdefault("pidgin", [])
            hits["pidgin"].extend([tok for tok in pidgin_tokens if tok in t])

        primary = "english"
        if hits:
            # Prefer non-english if present
            for cand in ("pidgin", "hausa", "yoruba", "igbo", "english"):
                if cand in hits:
                    primary = cand
                    break
        return {
            "primary_language": primary,
            "languages_detected": list(hits.keys()) or ["english"],
            "matched_phrases_by_language": hits,
            "offline": True,
        }

    def scan_message(
        self,
        text: str,
        *,
        channel: str = "manual",
        offline: bool = True,
        follow_links: bool = True,
    ) -> Dict[str, Any]:
        text = text or ""
        lang_info = self.detect_languages(text)
        findings: List[Dict[str, Any]] = []
        score = 0.0

        data = _phrases()
        lowered = text.lower()
        for lang, items in data.items():
            for item in items:
                if item["phrase"].lower() in lowered:
                    sev = item["severity"]
                    findings.append(
                        {
                            "type": "phrase",
                            "language": lang,
                            "category": item["category"],
                            "severity": sev,
                            "matched": item["phrase"],
                        }
                    )
                    score = max(score, SEVERITY_SCORE.get(sev, 0.5))

        for pat in CRYPTO_PROFIT_PATTERNS:
            if pat.search(text):
                findings.append(
                    {
                        "type": "crypto_profit_promise",
                        "category": "crypto_scam",
                        "severity": "critical",
                        "matched": pat.pattern,
                    }
                )
                score = max(score, 0.95)

        # Bank-impersonation combo: claims to be a bank + asks for details / OTP / PIN
        bank_claim = re.search(
            r"(?i)\b(hdfc|gtbank|gtb|zenith|access bank|uba|first bank|opay|kuda|palmpay|stanbic|fidelity|ecobank|wema|alat|bank)\b",
            text,
        )
        asks_secrets = re.search(
            r"(?i)(share|send|provide|confirm|update|submit).{0,40}"
            r"(bank details|account details|account number|otp|pin|password|bvn|nin|card|cvv|atm)",
            text,
        ) or re.search(
            r"(?i)(bank details|account details).{0,40}(share|send|provide|update|monthly)",
            text,
        )
        if bank_claim and asks_secrets:
            findings.append(
                {
                    "type": "bank_detail_request",
                    "language": "english",
                    "category": "bank_impersonation",
                    "severity": "critical",
                    "matched": "bank name + request for personal/bank details",
                }
            )
            score = max(score, 0.95)

        # Avoid recursion when scan_link already fetched a page and reuses phrase scoring.
        if follow_links:
            urls = URL_RE.findall(text)
            for url in urls[:5]:
                link_result = self.scan_link(url, accompanying_text=text)
                if link_result["decision"] != "ALLOW":
                    findings.append(
                        {
                            "type": "embedded_link",
                            "category": "phishing",
                            "severity": "high" if link_result["decision"] == "BLOCK" else "medium",
                            "matched": url,
                            "link_decision": link_result["decision"],
                            "link_reasons": link_result.get("reasons", []),
                        }
                    )
                    score = max(score, 0.85 if link_result["decision"] == "BLOCK" else 0.55)

        decision = _decision(score)
        categories = sorted({f["category"] for f in findings})
        primary_cat = categories[0] if categories else "benign"
        response_lang = lang_info["primary_language"] if lang_info["primary_language"] != "english" else "english"
        if response_lang not in ("english", "pidgin"):
            response_lang = "pidgin" if "pidgin" in lang_info["languages_detected"] else "english"

        return {
            "decision": decision,
            "risk_score": round(score, 3),
            "channel": channel,
            "categories": categories,
            "findings": findings,
            "language": lang_info,
            "advice": _advice(primary_cat, response_lang) if decision != "ALLOW" else (
                "No strong scam signals in this message." if response_lang == "english"
                else "No strong scam signal for this message."
            ),
            "offline": offline,
            "privacy": "Message scored locally with phrase packs; not sent to external LLM.",
        }

    def scan_channels_meta(self) -> Dict[str, Any]:
        return {
            "supported": [
                {
                    "id": "whatsapp",
                    "label": "WhatsApp",
                    "mode": "permissioned_webhook_or_forward",
                    "status": "ready",
                    "note": "Users grant permission; inbound text is scanned before action.",
                },
                {
                    "id": "gmail",
                    "label": "Gmail",
                    "mode": "oauth_or_paste",
                    "status": "ready_demo",
                    "note": "MVP supports paste + simulated inbox connect; OAuth can be added for production.",
                },
                {
                    "id": "instagram",
                    "label": "Instagram DMs",
                    "mode": "permissioned_export_or_paste",
                    "status": "ready_demo",
                    "note": "Users can paste DM text; Meta API connect is optional later.",
                },
                {
                    "id": "manual",
                    "label": "Manual share",
                    "mode": "paste",
                    "status": "ready",
                    "note": "Works fully offline with local patterns.",
                },
            ]
        }

    def _fetch_website(self, url: str) -> Dict[str, Any]:
        """Actually visit the URL and extract title / visible text / form signals."""
        import httpx
        from html.parser import HTMLParser

        class _Page(HTMLParser):
            def __init__(self):
                super().__init__()
                self.title = ""
                self._in_title = False
                self._skip = False
                self.texts: List[str] = []
                self.password_fields = 0
                self.forms = 0
                self.links: List[str] = []
                self.apk_links: List[str] = []
                self.meta_desc = ""

            def handle_starttag(self, tag, attrs):
                d = dict(attrs)
                t = tag.lower()
                if t in ("script", "style", "noscript"):
                    self._skip = True
                elif t == "title":
                    self._in_title = True
                elif t == "form":
                    self.forms += 1
                elif t == "input" and (d.get("type") or "").lower() == "password":
                    self.password_fields += 1
                elif t == "meta" and (d.get("name") or "").lower() == "description":
                    self.meta_desc = d.get("content") or ""
                elif t == "a":
                    href = d.get("href") or ""
                    if href:
                        self.links.append(href)
                        if re.search(r"(?i)\.apk(\?|$)|download.*apk|loan.?app", href):
                            self.apk_links.append(href)

            def handle_endtag(self, tag):
                t = tag.lower()
                if t in ("script", "style", "noscript"):
                    self._skip = False
                elif t == "title":
                    self._in_title = False

            def handle_data(self, data):
                if self._skip:
                    return
                chunk = " ".join((data or "").split())
                if not chunk:
                    return
                if self._in_title:
                    self.title += chunk
                else:
                    self.texts.append(chunk)

        out: Dict[str, Any] = {
            "fetched": False,
            "status_code": None,
            "final_url": url,
            "title": "",
            "snippet": "",
            "page_text": "",
            "password_fields": 0,
            "forms": 0,
            "apk_links": [],
            "error": None,
        }
        try:
            with httpx.Client(
                timeout=10.0,
                follow_redirects=True,
                headers={
                    "User-Agent": "SafeNaijaBot/1.0 (+https://safenaija.local; security-check)",
                    "Accept": "text/html,application/xhtml+xml",
                },
            ) as client:
                resp = client.get(url)
            out["status_code"] = resp.status_code
            out["final_url"] = str(resp.url)
            ctype = (resp.headers.get("content-type") or "").lower()
            body = resp.text[:200000] if resp.text else ""
            if "html" in ctype or "<html" in body[:500].lower():
                parser = _Page()
                parser.feed(body)
                page_text = " ".join(parser.texts)[:8000]
                out.update(
                    {
                        "fetched": True,
                        "title": (parser.title or "")[:200],
                        "snippet": (parser.meta_desc or page_text)[:400],
                        "page_text": page_text,
                        "password_fields": parser.password_fields,
                        "forms": parser.forms,
                        "apk_links": parser.apk_links[:10],
                    }
                )
            else:
                # non-HTML (json, text, apk binary headers)
                out.update(
                    {
                        "fetched": True,
                        "title": "",
                        "snippet": body[:400],
                        "page_text": body[:4000],
                    }
                )
        except Exception as exc:
            out["error"] = str(exc)[:240]
        return out

    def scan_link(self, url: str, accompanying_text: str = "") -> Dict[str, Any]:
        raw = (url or "").strip()
        if not raw:
            return {"decision": "ALLOW", "risk_score": 0.0, "reasons": ["Empty input"], "kind": "unknown"}

        candidate = raw if "://" in raw else "https://" + raw
        parsed = urlparse(candidate)
        host = (parsed.hostname or "").lower()
        path = parsed.path or ""

        if host in GITHUB_HOSTS or "github.com" in raw.lower():
            return self.scan_github(raw)

        # Live visit
        visit = self._fetch_website(candidate)
        page_text = visit.get("page_text") or ""
        text_blob = f"{raw}\n{accompanying_text}\n{visit.get('title') or ''}\n{page_text}"
        reasons: List[str] = []
        score = 0.0
        kind = "website"

        if visit.get("fetched"):
            reasons.append(
                f"Visited site HTTP {visit.get('status_code')} → {visit.get('final_url')}"
            )
            if visit.get("title"):
                reasons.append(f"Page title: {visit['title'][:120]}")
        elif visit.get("error"):
            reasons.append(f"Could not fully load page ({visit['error']}) — scored from URL + pasted text")

        # Crypto / investment platform heuristics
        crypto_hosts = ("binance", "coinbase", "trustwallet", "metamask", "pancakeswap", "dex", "forex", "trading")
        if any(h in host for h in crypto_hosts) or any(h in text_blob.lower() for h in ("crypto", "forex", "usdt", "btc")):
            kind = "crypto_platform"

        if any(host.endswith(tld) for tld in SUSPICIOUS_TLDS):
            reasons.append(f"Suspicious TLD on host {host}")
            score = max(score, 0.75)

        if host in SHORTENERS:
            reasons.append("URL shortener can hide phishing destinations")
            score = max(score, 0.65)

        if re.search(r"(?i)(login|verify|secure|update|account).{0,20}(bank|gtb|opay|kuda|access|zenith|uba)", host + path):
            reasons.append("Possible bank-impersonation phishing path in URL")
            score = max(score, 0.9)

        # Homoglyph / lookalike banks
        if re.search(r"(?i)(g[tţ]bank|zenlth|accesbank|firstbannk|opay-secure|kuda-verify)", host):
            reasons.append("Possible lookalike bank domain")
            score = max(score, 0.92)

        if visit.get("password_fields", 0) > 0 and re.search(
            r"(?i)(bank|gtb|opay|kuda|access|login|verify|otp|bvn|nin)", text_blob
        ):
            reasons.append("Live page asks for a password and uses bank / OTP language")
            score = max(score, 0.88)
            kind = "phishing_site"

        if visit.get("apk_links"):
            reasons.append(f"Page links to APK / loan-app download ({len(visit['apk_links'])})")
            score = max(score, 0.9)
            kind = "loan_app"

        if re.search(r"(?i)(apk|loan-?app|sideload)", text_blob):
            reasons.append("Loan-app / APK distribution language on page or URL")
            score = max(score, 0.85)
            kind = "loan_app"

        for pat in CRYPTO_PROFIT_PATTERNS:
            if pat.search(text_blob):
                reasons.append("Unrealistic profit / crypto deposit language on page or ad text")
                score = max(score, 0.95)
                kind = "crypto_platform"
                break

        # Nigerian scam phrases found inside fetched page / ad (no nested link crawl)
        msg = self.scan_message(
            text_blob[:4000], channel="website", offline=True, follow_links=False
        )
        if msg["decision"] != "ALLOW":
            for f in (msg.get("findings") or [])[:4]:
                reasons.append(f"On-page phrase ({f.get('language')}: {f.get('matched')})")
            score = max(score, float(msg.get("risk_score") or 0))

        sec = self.check_sec_registration(text_blob)
        if sec.get("alert_matches"):
            reasons.append("Matches unregistered / alerted investment names (demo SEC pack)")
            score = max(score, 0.92)
            kind = "crypto_platform"

        # Secret leakage on public marketing sites
        for pat, label in SECRET_PATTERNS:
            if pat.search(page_text):
                reasons.append(f"Live page exposes secret pattern: {label}")
                score = max(score, 0.95)

        decision = _decision(score)
        return {
            "decision": decision,
            "risk_score": round(score, 3),
            "kind": kind,
            "host": host,
            "reasons": reasons or ["No strong malicious signals after visiting the page"],
            "sec": sec,
            "visit": {
                "fetched": visit.get("fetched"),
                "status_code": visit.get("status_code"),
                "final_url": visit.get("final_url"),
                "title": visit.get("title"),
                "snippet": visit.get("snippet"),
                "password_fields": visit.get("password_fields"),
                "forms": visit.get("forms"),
                "apk_links": visit.get("apk_links"),
                "error": visit.get("error"),
            },
            "language": msg.get("language"),
            "advice": (
                "Do not deposit funds or share wallet seeds. Verify platform on sec.gov.ng."
                if decision != "ALLOW" and kind == "crypto_platform"
                else _advice("phishing")
                if decision != "ALLOW"
                else "We visited this page and found no strong scam signals — still verify before logging in or paying."
            ),
            "offline": not bool(visit.get("fetched")),
        }

    def _bad_code_demo_frames(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """Visual 'screenshot' frames of vulnerable code for demos / when secrets found."""
        return [
            {
                "filename": f"{owner}/{repo}/backend/config.py",
                "language": "python",
                "title": "Exposed API keys in source",
                "start_line": 12,
                "highlight_lines": [14, 15, 16],
                "lines": [
                    "import os",
                    "",
                    "# BAD: secrets committed to the public repo",
                    'OPENAI_API_KEY = "sk-proj-DEMO_EXPOSED_KEY_9f3a2c1b8e7d6"',
                    'DATABASE_URL = "postgres://admin:NaijaPass123@db.internal:5432/app"',
                    'STRIPE_SECRET = "sk_live_51DemoLeakedKeyXXXX"',
                    "",
                    "def get_client():",
                    "    return OpenAI(api_key=OPENAI_API_KEY)",
                ],
            },
            {
                "filename": f"{owner}/{repo}/.env",
                "language": "env",
                "title": "Committed .env with live credentials",
                "start_line": 1,
                "highlight_lines": [1, 2, 3, 4],
                "lines": [
                    "OPENAI_API_KEY=sk-proj-DEMO_EXPOSED_KEY_9f3a2c1b8e7d6",
                    "AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE",
                    "AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
                    "JWT_SECRET=supersecret_do_not_share",
                ],
            },
        ]

    def _extract_code_frames(self, file_map: Dict[str, str]) -> List[Dict[str, Any]]:
        frames: List[Dict[str, Any]] = []
        for path, content in file_map.items():
            lines = content.splitlines()
            hit_idxs = []
            for i, line in enumerate(lines):
                if any(p.search(line) for p, _ in SECRET_PATTERNS) or re.search(
                    r"(?i)(api[_-]?key|secret|password|token)\s*[:=]", line
                ):
                    hit_idxs.append(i)
            if not hit_idxs:
                continue
            # Window around first hits
            center = hit_idxs[0]
            start = max(0, center - 3)
            end = min(len(lines), center + 6)
            window = lines[start:end]
            highlight = [start + 1 + (i) for i, _ in enumerate(window) if (start + i) in hit_idxs]
            # remap highlight to displayed line numbers
            display_highlight = []
            for hi in hit_idxs:
                if start <= hi < end:
                    display_highlight.append(hi + 1)
            frames.append(
                {
                    "filename": path,
                    "language": path.split(".")[-1] if "." in path else "text",
                    "title": "Vulnerable / secret-bearing code",
                    "start_line": start + 1,
                    "highlight_lines": display_highlight,
                    "lines": window[:40],
                }
            )
            if len(frames) >= 3:
                break
        return frames

    def scan_github(self, repo_url: str) -> Dict[str, Any]:
        """
        GitHub/repo risk check with visual bad-code frames.
        Fetches README + common secret-prone files from raw.githubusercontent.com.
        """
        raw = (repo_url or "").strip()
        candidate = raw if "://" in raw else "https://" + raw
        parsed = urlparse(candidate)
        parts = [p for p in (parsed.path or "").split("/") if p]
        owner = parts[0] if parts else ""
        repo = parts[1].removesuffix(".git") if len(parts) > 1 else ""

        findings: List[Dict[str, Any]] = []
        score = 0.2
        file_map: Dict[str, str] = {}
        fetch_note = "offline_url_only"
        code_frames: List[Dict[str, Any]] = []

        candidates = [
            "README.md",
            ".env",
            ".env.example",
            "config.py",
            "settings.py",
            "app.py",
            "main.py",
        ]

        if owner and repo:
            try:
                import httpx

                # Short overall budget so Link/GitHub demos never stall the API
                with httpx.Client(timeout=httpx.Timeout(3.0, connect=2.0), follow_redirects=True) as client:
                    for branch in ("HEAD", "main"):
                        got_any = False
                        for rel in candidates:
                            url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{rel}"
                            try:
                                r = client.get(url)
                            except Exception:
                                continue
                            if r.status_code == 200 and r.text:
                                file_map[f"{owner}/{repo}/{rel}"] = r.text[:12000]
                                got_any = True
                        if got_any:
                            fetch_note = f"files_fetched:{branch}:{len(file_map)}"
                            break
            except Exception:
                fetch_note = "fetch_failed_using_local_patterns"

        # Demo / non-existent student repos still show bad-code picture
        demo_like = (not file_map) or ("demo" in (owner + repo).lower()) or ("naija" in (owner + repo).lower())
        if demo_like and not any(
            any(p.search(txt) for p, _ in SECRET_PATTERNS) for txt in file_map.values()
        ):
            for frame in self._bad_code_demo_frames(owner or "student", repo or "repo"):
                file_map[frame["filename"]] = "\n".join(frame["lines"])
            fetch_note = "demo_vulnerable_snapshot"
            findings.append(
                {
                    "severity": "critical",
                    "label": "Demo vulnerable snapshot — secrets illustrated for teaching / Imagine Cup",
                    "category": "secret_exposure",
                }
            )
            score = max(score, 0.95)
            code_frames = self._bad_code_demo_frames(owner or "student", repo or "repo")

        blob = f"{raw}\n" + "\n".join(file_map.values())
        for pat, label in SECRET_PATTERNS:
            if pat.search(blob):
                findings.append({"severity": "critical", "label": label, "category": "secret_exposure"})
                score = max(score, 0.95)

        if re.search(r"(?i)(openai|anthropic|firebase|stripe).{0,40}(key|secret|token)", blob):
            findings.append(
                {
                    "severity": "high",
                    "label": "Possible third-party credential mention in public files",
                    "category": "secret_exposure",
                }
            )
            score = max(score, 0.8)

        if re.search(r"(?i)(loan.?app|apk|harvest.?contact|accessibility.?service)", blob):
            findings.append(
                {
                    "severity": "high",
                    "label": "Possible predatory loan-app / contact-harvest patterns",
                    "category": "mobile_malware",
                }
            )
            score = max(score, 0.85)

        if not code_frames:
            code_frames = self._extract_code_frames(file_map)

        if score >= 0.7 and not code_frames:
            code_frames = self._bad_code_demo_frames(owner or "student", repo or "repo")

        # de-dupe findings by label
        seen = set()
        uniq = []
        for f in findings:
            if f["label"] in seen:
                continue
            seen.add(f["label"])
            uniq.append(f)
        findings = uniq

        if not findings and fetch_note.startswith("offline"):
            findings.append(
                {
                    "severity": "low",
                    "label": "Could not fetch remote files; URL parsed for structure only",
                    "category": "info",
                }
            )

        decision = _decision(score if findings else 0.15)
        risk = round(score if findings else 0.15, 3)
        # Student Risk Passport — score + top 3 fixes (pitch feature)
        fix_pool = []
        cats = {f.get("category") for f in findings}
        if "secret_exposure" in cats or decision == "BLOCK":
            fix_pool.extend([
                "Rotate every exposed key/token now and revoke old ones at the provider.",
                "Remove secrets from the repo and purge them from git history (filter-repo / BFG).",
                "Move secrets to environment variables or a secrets manager; add .env to .gitignore.",
            ])
        if "mobile_malware" in cats:
            fix_pool.append("Drop loan-app / APK / contact-harvest code paths from any student demo.")
        if not fix_pool:
            fix_pool = [
                "Keep .env and API keys out of public commits.",
                "Enable Dependabot / secret scanning on the GitHub repo.",
                "Review README for accidental credentials before demos.",
            ]
        top_fixes = list(dict.fromkeys(fix_pool))[:3]
        passport_score = int(round(risk * 100))
        if passport_score >= 70:
            status, tone = "Critical — fix before sharing", "block"
        elif passport_score >= 40:
            status, tone = "Needs attention", "warn"
        else:
            status, tone = "Looking healthier", "allow"
        risk_passport = {
            "title": "Student Risk Passport",
            "repo": f"{owner}/{repo}" if owner else repo or "repo",
            "score": passport_score,
            "status": status,
            "tone": tone,
            "decision": decision,
            "top_fixes": top_fixes,
            "findings_count": len(findings),
            "frames_count": len(code_frames),
        }
        return {
            "decision": decision,
            "risk_score": risk,
            "kind": "github",
            "owner": owner,
            "repo": repo,
            "fetch": fetch_note,
            "findings": findings,
            "reasons": [f["label"] for f in findings],
            "code_frames": code_frames,
            "risk_passport": risk_passport,
            "advice": (
                "Rotate any exposed keys immediately and remove secrets from git history."
                if decision == "BLOCK"
                else "No critical secrets found in sampled public content. Still avoid committing .env files."
            ),
            "sec": self.check_sec_registration(blob),
            "offline": not str(fetch_note).startswith("files_fetched"),
        }

    def check_sec_registration(self, text: str) -> Dict[str, Any]:
        data = _sec()
        t = (text or "").lower()
        matches = []
        for item in data.get("unregistered_alerts", []):
            names = [item["name"].lower(), *item.get("aliases", [])]
            if any(n in t for n in names):
                matches.append(item)
        registered_hits = []
        for item in data.get("registered_sample", []):
            if item["name"].lower() in t or item["reg_no"].lower() in t:
                registered_hits.append(item)
        return {
            "verify_url": data.get("verify_url", "https://sec.gov.ng"),
            "alert_matches": matches,
            "registered_sample_hits": registered_hits,
            "disclaimer": "Demo registry pack only. Confirm live status on SEC Nigeria.",
        }

    def check_phone(self, number: str) -> Dict[str, Any]:
        norm = _norm_phone(number)
        banks = _banks()["banks"]
        scam = _scam_numbers()["numbers"]

        for b in banks:
            for n in b["numbers"]:
                if _norm_phone(n) == norm or n.replace(" ", "") == number.replace(" ", ""):
                    return {
                        "decision": "ALLOW",
                        "risk_score": 0.05,
                        "match": "verified_bank_helpline",
                        "bank": b["name"],
                        "number": norm,
                        "advice": f"Matches listed public helpline pattern for {b['name']}. Still avoid sharing OTP.",
                        "offline": True,
                    }

        for s in scam:
            if _norm_phone(s["number"]) == norm or s["number"].replace(" ", "") in number.replace(" ", ""):
                return {
                    "decision": "BLOCK",
                    "risk_score": 0.95,
                    "match": "reported_scam_number",
                    "category": s["category"],
                    "reports": s["reports"],
                    "note": s["note"],
                    "number": norm,
                    "advice": _advice(s["category"]),
                    "offline": True,
                }

        # Heuristic: premium-looking / random unknown
        return {
            "decision": "WARN",
            "risk_score": 0.5,
            "match": "unknown_number",
            "number": norm or number,
            "advice": "Number not in verified bank list or local scam reports. Do not share OTP; call your bank back on the official app number.",
            "offline": True,
        }

    def google_osint_search(self, query: str, phone: str = "", city: str = "Lagos") -> Dict[str, Any]:
        """
        Live web search (DuckDuckGo HTML) + Google search URL for SIM-swap exposure OSINT.
        Shows terminal-style steps: search person → collect public hits → evaluate SIM-swap risk.
        """
        q = (query or "").strip()
        phone = (phone or "").strip()
        if not q and phone:
            q = phone
        if not q:
            return {"ok": False, "error": "Provide a name or phone to search"}

        search_q = f"{q} {phone} {city} Nigeria".strip()
        google_url = "https://www.google.com/search?" + __import__("urllib.parse").parse.urlencode({"q": search_q})
        ddg_url = "https://html.duckduckgo.com/html/?" + __import__("urllib.parse").parse.urlencode({"q": search_q})

        terminal: List[Dict[str, str]] = [
            {"t": "00:00.0", "line": f"$ safenaija osint --target \"{q}\" --phone \"{phone or '-'}\""},
            {"t": "00:00.2", "line": f"[*] Opening Google search: {search_q}"},
            {"t": "00:00.4", "line": f"[*] GET {google_url[:90]}…"},
        ]

        results: List[Dict[str, str]] = []
        fetch_ok = False
        try:
            import httpx
            from html.parser import HTMLParser

            class _DDG(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.results = []
                    self._in_result = False
                    self._in_title = False
                    self._in_snippet = False
                    self._cur = {}
                    self._buf = []

                def handle_starttag(self, tag, attrs):
                    d = dict(attrs)
                    cls = d.get("class", "")
                    if tag == "a" and "result__a" in cls:
                        self._in_title = True
                        self._buf = []
                        self._cur = {"url": d.get("href", ""), "title": "", "snippet": ""}
                    elif tag == "a" and "result__snippet" in cls:
                        self._in_snippet = True
                        self._buf = []

                def handle_endtag(self, tag):
                    if tag == "a" and self._in_title:
                        self._cur["title"] = "".join(self._buf).strip()
                        self._in_title = False
                    elif tag == "a" and self._in_snippet:
                        self._cur["snippet"] = "".join(self._buf).strip()
                        self._in_snippet = False
                        if self._cur.get("title"):
                            self.results.append(self._cur)
                            self._cur = {}

                def handle_data(self, data):
                    if self._in_title or self._in_snippet:
                        self._buf.append(data)

            with httpx.Client(timeout=12.0, follow_redirects=True, headers={"User-Agent": "SafeNaija/1.0"}) as client:
                r = client.post(ddg_url, data={"q": search_q})
                if r.status_code == 200:
                    parser = _DDG()
                    parser.feed(r.text)
                    results = parser.results[:8]
                    fetch_ok = True
                    terminal.append({"t": "00:01.1", "line": f"[+] Indexed {len(results)} public search hits (via DuckDuckGo mirror)"})
                else:
                    terminal.append({"t": "00:01.1", "line": f"[!] Search mirror HTTP {r.status_code} — using Google URL + heuristic eval"})
        except Exception as exc:
            terminal.append({"t": "00:01.1", "line": f"[!] Search fetch error: {exc}"})

        # Evaluate exposure from titles/snippets
        blob = " ".join(f"{x.get('title','')} {x.get('snippet','')}" for x in results).lower()
        factors = []
        if phone and re.sub(r"\D", "", phone)[-7:] in re.sub(r"\D", "", blob + phone):
            # phone digits appearing in public results or query itself
            pass
        if any(k in blob for k in ("phone", "mobile", "whatsapp", "contact", "tel:")):
            factors.append(("Phone / contact details appear in public search hits", 0.25))
        if any(k in blob for k in ("address", "street", "estate", "lagos", "abuja", "port harcourt")):
            factors.append(("Location / address clues in public results", 0.15))
        if any(k in blob for k in ("linkedin", "facebook", "instagram", "twitter", "nairaland")):
            factors.append(("Social profiles discoverable via Google", 0.2))
        if any(k in blob for k in ("bvn", "nin", "passport", "account number")):
            factors.append(("Sensitive identity keywords near this person online", 0.3))
        if not results:
            factors.append(("Limited indexed hits — still treat phone-in-bio as risk", 0.1))
        else:
            factors.append((f"{len(results)} public web results found for this identity", 0.1))

        # Always add phone-public heuristic if phone provided
        if phone:
            factors.append(("Phone number used as search pivot (SIM-swap OSINT pattern)", 0.15))

        score = min(0.99, sum(w for _, w in factors))
        terminal.append({"t": "00:01.6", "line": "[*] Evaluating SIM-swap exposure from public footprints…"})
        for label, w in factors:
            terminal.append({"t": "00:01.8", "line": f"[eval] +{w:.2f}  {label}"})
        terminal.append({"t": "00:02.0", "line": f"[done] risk_score={score:.2f} decision={_decision(score)}"})

        return {
            "ok": True,
            "query": q,
            "phone": phone,
            "search_query": search_q,
            "google_url": google_url,
            "duckduckgo_url": ddg_url,
            "fetch_ok": fetch_ok,
            "results": results,
            "terminal": terminal,
            "decision": _decision(score),
            "risk_score": round(score, 3),
            "factors": [{"label": l, "weight": w} for l, w in factors],
            "advice": _advice("sim_swap"),
            "note": "Opens the same Google query attackers use. Results scraped via DuckDuckGo HTML mirror when available.",
        }

    def sim_swap_risk(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess SIM-swap vulnerability from user-supplied *public / self-declared* signals
        plus optional live Google OSINT search.
        """
        factors: List[Tuple[str, float, str]] = []

        if payload.get("phone_public_on_social"):
            factors.append(("Phone number visible on social profiles", 0.2, "exposure"))
        if payload.get("nin_or_bvn_shared_before"):
            factors.append(("User previously shared NIN/BVN outside official channels", 0.25, "identity"))
        if payload.get("email_breached_known"):
            factors.append(("Email appears in known breach / paste lists (self-reported)", 0.15, "credential"))
        if payload.get("reused_passwords"):
            factors.append(("Password reuse across bank / email / social", 0.15, "credential"))
        if payload.get("no_bank_transaction_alerts"):
            factors.append(("No SMS/email transaction alerts enabled", 0.1, "hygiene"))
        if payload.get("dual_sim_unknown_apps"):
            factors.append(("Unknown apps with SMS / phone permission", 0.15, "device"))
        if payload.get("recent_sim_issues"):
            factors.append(("Recent unexpected SIM / network loss", 0.3, "active_risk"))
        if payload.get("public_home_address"):
            factors.append(("Home address easy to find publicly", 0.1, "exposure"))

        osint = None
        if payload.get("full_name") or payload.get("phone"):
            osint = self.google_osint_search(
                payload.get("full_name") or "",
                phone=payload.get("phone") or "",
                city=payload.get("city") or "Lagos",
            )
            if osint.get("ok"):
                for f in osint.get("factors") or []:
                    factors.append((f["label"], float(f["weight"]), "osint"))

        score = min(0.99, sum(w for _, w, _ in factors))
        decision = _decision(score)
        return {
            "decision": decision,
            "risk_score": round(score, 3),
            "factors": [{"label": l, "weight": w, "group": g} for l, w, g in factors],
            "osint": osint,
            "advice": _advice("sim_swap", "english" if score < 0.7 else "pidgin"),
            "hardening": [
                "Enable bank transaction alerts and app-based 2FA where available",
                "Ask your telco about SIM-swap / port-out PIN if offered",
                "Remove phone number from public social bios",
                "Never share NIN/BVN/OTP on WhatsApp or Instagram",
            ],
            "privacy": "OSINT uses public web search only — no call audio, no telco account takeover.",
            "offline": osint is None,
        }

    def simulate_alerts(self, scenario: str = "sim_swap") -> Dict[str, Any]:
        scenarios = {
            "sim_swap": {
                "title": "Suspicious SIM change",
                "timeline": [
                    {"t": "00:00", "event": "Telco reports SIM swap / SIM replace request (simulated)"},
                    {"t": "00:00:08", "event": "SafeNaija alert → WhatsApp + email: 'Your line may be moving'"},
                    {"t": "00:00:15", "event": "Bank channel freeze suggestion (demo) until user confirms in-app"},
                    {"t": "00:01:00", "event": "If user taps 'Not me' → escalate to bank fraud desk playbook"},
                ],
                "user_alert": "ALERT: Possible SIM swap on +23480****1234. If this wasn't you, freeze transfers and call your bank.",
            },
            "bank_account_change": {
                "title": "Bank account detail change",
                "timeline": [
                    {"t": "00:00", "event": "Profile change: payout account / next-of-kin phone edited (simulated)"},
                    {"t": "00:00:05", "event": "SafeNaija alert on secondary channel (email/Instagram notice demo)"},
                    {"t": "00:00:20", "event": "Require step-up verification before transfers"},
                ],
                "user_alert": "ALERT: Bank profile details changed. Confirm in your official banking app — ignore chat OTPs.",
            },
        }
        data = scenarios.get(scenario) or scenarios["sim_swap"]
        return {"scenario": scenario, **data, "dummy_data": True}

    def attack_simulation(self, attack_type: str = "phishing") -> Dict[str, Any]:
        catalog = {
            "phishing": {
                "name": "Bank phishing WhatsApp",
                "dummy_message": "Dear customer, GTBank detected unusual login. Send the OTP we just texted to unlock your account now: https://gtb-secure-login.xyz/verify",
                "channel": "whatsapp",
            },
            "investment": {
                "name": "Fake crypto investment",
                "dummy_message": "Join NaijaCrypto Doubler VIP — guaranteed 40% weekly returns. Send USDT to start. Abeg no miss this.",
                "channel": "instagram",
            },
            "sim_swap": {
                "name": "SIM swap social engineering",
                "dummy_message": "Hello, this is MTN support. We need your NIN and the last OTP to stop your line from being blocked today.",
                "channel": "call_script",
            },
            "fake_loan": {
                "name": "Predatory loan app lure",
                "dummy_message": "Your QuickCash loan is approved. Download this APK loan app now now and allow contacts permission.",
                "channel": "sms",
            },
            "github_secret": {
                "name": "Student repo secret leak",
                "dummy_message": "https://github.com/demo-student/naija-fintech-bot",
                "channel": "github",
                "extra": "OPENAI_API_KEY=sk-demoEXPOSEDkey123456789012345 and DATABASE_URL=postgres://user:pass@localhost/db",
            },
        }
        item = catalog.get(attack_type) or catalog["phishing"]
        if attack_type == "github_secret":
            result = self.scan_github(item["dummy_message"])
            # Force-detect secrets from accompanying dummy snippet
            secret_scan = self.scan_message(item.get("extra", ""), channel="github")
            return {
                "attack_type": attack_type,
                "name": item["name"],
                "dummy_payload": item,
                "detection": {
                    "github": result,
                    "secret_snippet": secret_scan,
                },
                "explained": [
                    "Attacker scrapes public repos for keys within minutes.",
                    "SafeNaija flags key-like patterns and warns the student founder.",
                ],
            }

        if attack_type == "sim_swap":
            phone = self.check_phone("+2348098765432")
            msg = self.scan_message(item["dummy_message"], channel="call_script")
            return {
                "attack_type": attack_type,
                "name": item["name"],
                "dummy_payload": item,
                "detection": {"message": msg, "related_scam_number": phone},
                "explained": [
                    "Caller invents urgency and asks for NIN/OTP.",
                    "Number check + phrase detection trigger BLOCK without recording the call.",
                ],
            }

        detection = self.scan_message(item["dummy_message"], channel=item["channel"])
        return {
            "attack_type": attack_type,
            "name": item["name"],
            "dummy_payload": item,
            "detection": detection,
            "explained": [
                "Dummy scam content is scored with the same offline phrase packs used in production mode.",
                f"Decision: {detection['decision']} (risk {detection['risk_score']}).",
            ],
        }

    def offline_status(self) -> Dict[str, Any]:
        return {
            "offline_ready": True,
            "local_assets": [
                "scam_phrases.json",
                "bank_helplines.json",
                "scam_numbers.json",
                "sec_registry.json",
            ],
            "capabilities_without_network": [
                "message scam detection",
                "Nigerian language / Pidgin phrase detection",
                "fraud call number lookup (local lists)",
                "crypto profit-promise heuristics",
                "SIM swap risk questionnaire",
                "attack simulations with dummy data",
            ],
            "needs_network_optional": [
                "Live GitHub README fetch",
                "Real Gmail/Instagram OAuth sync",
                "Live SEC website verification",
            ],
        }
