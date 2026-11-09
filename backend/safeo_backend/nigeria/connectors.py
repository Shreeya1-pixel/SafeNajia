"""
Live channel connectors for SafeNaija (WhatsApp Cloud API, Gmail OAuth/IMAP, Instagram token).

Credentials are stored locally in backend/.safenaija_connections.json (gitignored).
"""
from __future__ import annotations

import base64
import email
import imaplib
import json
import os
import re
import time
import urllib.parse
from email.header import decode_header
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

STORE = Path(__file__).resolve().parents[3] / ".safenaija_connections.json"
# parents: nigeria -> safeo_backend -> backend -> SafeNaija root... 
# __file__ = .../backend/safeo_backend/nigeria/connectors.py
# parents[0]=nigeria, [1]=safeo_backend, [2]=backend
STORE = Path(__file__).resolve().parents[2] / ".safenaija_connections.json"


def _load() -> Dict[str, Any]:
    if STORE.exists():
        try:
            return json.loads(STORE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save(data: Dict[str, Any]) -> None:
    STORE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def status() -> Dict[str, Any]:
    data = _load()
    out = {}
    for key in ("whatsapp", "gmail", "instagram"):
        cfg = data.get(key) or {}
        out[key] = {
            "connected": bool(cfg.get("connected")),
            "account_hint": cfg.get("account_hint"),
            "mode": cfg.get("mode"),
            "last_sync": cfg.get("last_sync"),
            "message_count": len(cfg.get("inbox") or []),
            "error": cfg.get("last_error"),
        }
    return out


# ── WhatsApp Cloud API ────────────────────────────────────────────────────────

async def connect_whatsapp(phone_number_id: str, access_token: str, verify_token: str = "safenaija") -> Dict[str, Any]:
    phone_number_id = (phone_number_id or "").strip()
    access_token = (access_token or "").strip()
    if not phone_number_id or not access_token:
        return {"ok": False, "error": "phone_number_id and access_token are required"}

    url = f"https://graph.facebook.com/v19.0/{phone_number_id}"
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(url, headers={"Authorization": f"Bearer {access_token}"})
    if resp.status_code >= 400:
        return {
            "ok": False,
            "error": f"WhatsApp Graph API rejected credentials ({resp.status_code}): {resp.text[:300]}",
        }

    profile = resp.json()
    display = profile.get("display_phone_number") or profile.get("verified_name") or phone_number_id
    data = _load()
    data["whatsapp"] = {
        "connected": True,
        "mode": "meta_cloud_api",
        "account_hint": display,
        "phone_number_id": phone_number_id,
        "access_token": access_token,
        "verify_token": verify_token or "safenaija",
        "last_sync": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "inbox": data.get("whatsapp", {}).get("inbox") or [],
        "last_error": None,
    }
    # Also export for existing webhook sender
    os.environ["WHATSAPP_PHONE_NUMBER_ID"] = phone_number_id
    os.environ["WHATSAPP_ACCESS_TOKEN"] = access_token
    os.environ["WHATSAPP_VERIFY_TOKEN"] = verify_token or "safenaija"
    _save(data)
    return {
        "ok": True,
        "channel": "whatsapp",
        "account_hint": display,
        "webhook_path": "/webhooks/whatsapp",
        "note": "Inbound messages hitting your webhook are scanned live. Point Meta webhook to your public URL + /webhooks/whatsapp",
        "profile": {"id": profile.get("id"), "display_phone_number": profile.get("display_phone_number")},
    }


def ingest_whatsapp_message(from_phone: str, text: str) -> None:
    data = _load()
    wa = data.setdefault("whatsapp", {"connected": False, "inbox": []})
    inbox = wa.setdefault("inbox", [])
    inbox.insert(
        0,
        {
            "id": f"wa-{int(time.time()*1000)}",
            "from": from_phone,
            "text": text,
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "channel": "whatsapp",
        },
    )
    wa["inbox"] = inbox[:50]
    wa["last_sync"] = wa["inbox"][0]["ts"]
    _save(data)


async def fetch_whatsapp_inbox() -> Dict[str, Any]:
    data = _load()
    wa = data.get("whatsapp") or {}
    if not wa.get("connected"):
        return {"ok": False, "error": "WhatsApp not connected", "messages": []}
    return {
        "ok": True,
        "messages": wa.get("inbox") or [],
        "account_hint": wa.get("account_hint"),
        "note": "Messages appear here when Meta delivers them to /webhooks/whatsapp, or via manual forward API.",
    }


# ── Gmail (OAuth + IMAP app password) ─────────────────────────────────────────

def gmail_oauth_start(redirect_uri: Optional[str] = None) -> Dict[str, Any]:
    client_id = os.getenv("GOOGLE_CLIENT_ID", "").strip()
    redirect = (redirect_uri or os.getenv("GOOGLE_REDIRECT_URI") or "http://127.0.0.1:8001/nigeria/channels/gmail/callback").strip()
    if not client_id:
        return {
            "ok": False,
            "error": "Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in backend/.env for OAuth, or use IMAP app-password connect.",
            "imap_alternative": True,
        }
    params = {
        "client_id": client_id,
        "redirect_uri": redirect,
        "response_type": "code",
        "scope": "https://www.googleapis.com/auth/gmail.readonly",
        "access_type": "offline",
        "prompt": "consent",
    }
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)
    return {"ok": True, "auth_url": url, "redirect_uri": redirect}


async def gmail_oauth_callback(code: str, redirect_uri: Optional[str] = None) -> Dict[str, Any]:
    client_id = os.getenv("GOOGLE_CLIENT_ID", "").strip()
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()
    redirect = (redirect_uri or os.getenv("GOOGLE_REDIRECT_URI") or "http://127.0.0.1:8001/nigeria/channels/gmail/callback").strip()
    if not client_id or not client_secret:
        return {"ok": False, "error": "Missing GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET"}

    async with httpx.AsyncClient(timeout=20.0) as client:
        token_resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect,
                "grant_type": "authorization_code",
            },
        )
        if token_resp.status_code >= 400:
            return {"ok": False, "error": token_resp.text[:400]}
        tokens = token_resp.json()
        access = tokens.get("access_token")
        refresh = tokens.get("refresh_token")

        profile = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access}"},
        )
        email_addr = (profile.json() or {}).get("email") if profile.status_code < 400 else "gmail-user"

        # Fetch recent messages
        listed = await client.get(
            "https://gmail.googleapis.com/gmail/v1/users/me/messages",
            headers={"Authorization": f"Bearer {access}"},
            params={"maxResults": 10, "q": "newer_than:14d"},
        )
        messages: List[Dict[str, Any]] = []
        if listed.status_code < 400:
            for item in (listed.json().get("messages") or [])[:10]:
                mid = item["id"]
                detail = await client.get(
                    f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{mid}",
                    headers={"Authorization": f"Bearer {access}"},
                    params={"format": "full"},
                )
                if detail.status_code >= 400:
                    continue
                messages.append(_parse_gmail_api_message(detail.json()))

    data = _load()
    data["gmail"] = {
        "connected": True,
        "mode": "oauth",
        "account_hint": email_addr,
        "access_token": access,
        "refresh_token": refresh,
        "inbox": messages,
        "last_sync": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "last_error": None,
    }
    _save(data)
    return {"ok": True, "channel": "gmail", "account_hint": email_addr, "messages": messages}


def _decode_mime(value: str) -> str:
    if not value:
        return ""
    parts = decode_header(value)
    out = []
    for chunk, enc in parts:
        if isinstance(chunk, bytes):
            out.append(chunk.decode(enc or "utf-8", errors="replace"))
        else:
            out.append(chunk)
    return "".join(out)


def _parse_gmail_api_message(payload: Dict[str, Any]) -> Dict[str, Any]:
    headers = {h["name"].lower(): h["value"] for h in (payload.get("payload") or {}).get("headers") or []}
    snippet = payload.get("snippet") or ""
    body = snippet
    # try extract text/plain
    def walk(part):
        nonlocal body
        if not part:
            return
        if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
            raw = part["body"]["data"]
            pad = "=" * (-len(raw) % 4)
            body = base64.urlsafe_b64decode(raw + pad).decode("utf-8", errors="replace")[:4000]
        for child in part.get("parts") or []:
            walk(child)

    walk(payload.get("payload"))
    return {
        "id": payload.get("id"),
        "from": headers.get("from", ""),
        "subject": headers.get("subject", "(no subject)"),
        "text": body or snippet,
        "ts": headers.get("date", ""),
        "channel": "gmail",
    }


def _imap_extract_body(msg: Any) -> str:
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                try:
                    body = part.get_payload(decode=True).decode(errors="replace")[:2500]
                except Exception:
                    body = ""
                break
    else:
        try:
            body = msg.get_payload(decode=True).decode(errors="replace")[:2500]
        except Exception:
            body = str(msg.get_payload())[:2500]
    return body


def connect_gmail_imap(email_addr: str, app_password: str) -> Dict[str, Any]:
    """Fetch last 10 inbox messages quickly. Hard socket timeout so demos never hang."""
    email_addr = (email_addr or "").strip()
    app_password = (app_password or "").replace(" ", "")
    if not email_addr or not app_password:
        return {"ok": False, "error": "email and app_password required"}

    mail = None
    try:
        # timeout= avoids freezing the whole API when Gmail is slow
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993, timeout=12)
        mail.login(email_addr, app_password)
        typ, sel = mail.select("INBOX", readonly=True)
        if typ != "OK":
            return {"ok": False, "error": "Could not open Gmail INBOX"}
        exists = int(sel[0]) if sel and sel[0] else 0
        messages: List[Dict[str, Any]] = []
        if exists > 0:
            # Sequence range — much faster than SEARCH ALL on large inboxes
            start = max(1, exists - 9)
            seq = f"{start}:{exists}"
            typ, msg_data = mail.fetch(seq, "(RFC822.HEADER BODY.PEEK[TEXT]<0.2500>)")
            if typ == "OK" and msg_data:
                # msg_data is a list of tuples / bytes; group by message
                chunks: List[bytes] = []
                for item in msg_data:
                    if isinstance(item, tuple) and len(item) >= 2 and isinstance(item[1], (bytes, bytearray)):
                        chunks.append(bytes(item[1]))
                # Fallback: some servers return full RFC822 in one blob per msg
                if not chunks:
                    for item in msg_data:
                        if isinstance(item, tuple) and len(item) >= 2:
                            chunks.append(bytes(item[1]))
                for i, raw in enumerate(reversed(chunks[-10:])):
                    try:
                        msg = email.message_from_bytes(raw)
                    except Exception:
                        continue
                    subject = _decode_mime(msg.get("Subject", ""))
                    from_ = _decode_mime(msg.get("From", ""))
                    body = _imap_extract_body(msg)
                    mid = str(exists - i)
                    messages.append(
                        {
                            "id": mid,
                            "from": from_,
                            "subject": subject,
                            "text": f"{subject}\n\n{body}".strip(),
                            "ts": msg.get("Date", ""),
                            "channel": "gmail",
                        }
                    )
            # If peek fetch failed, fall back to per-id HEADER+TEXT (still capped)
            if not messages:
                for mid in range(exists, start - 1, -1):
                    typ, one = mail.fetch(str(mid), "(RFC822)")
                    if typ != "OK" or not one or not isinstance(one[0], tuple):
                        continue
                    msg = email.message_from_bytes(one[0][1])
                    subject = _decode_mime(msg.get("Subject", ""))
                    from_ = _decode_mime(msg.get("From", ""))
                    body = _imap_extract_body(msg)
                    messages.append(
                        {
                            "id": str(mid),
                            "from": from_,
                            "subject": subject,
                            "text": f"{subject}\n\n{body}".strip(),
                            "ts": msg.get("Date", ""),
                            "channel": "gmail",
                        }
                    )
        try:
            mail.logout()
        except Exception:
            pass
    except imaplib.IMAP4.error as exc:
        return {
            "ok": False,
            "error": f"IMAP login failed: {exc}. Use a Gmail App Password (Google Account → Security → App passwords).",
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
    finally:
        if mail is not None:
            try:
                mail.shutdown()
            except Exception:
                pass

    data = _load()
    prev = data.get("gmail") or {}
    data["gmail"] = {
        "connected": True,
        "mode": "imap_app_password",
        "account_hint": email_addr,
        "email": email_addr,
        "app_password": app_password,
        "inbox": messages,
        "last_sync": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "last_sync_epoch": time.time(),
        "last_error": None,
        "message_count": prev.get("message_count") or len(messages),
    }
    _save(data)
    return {
        "ok": True,
        "channel": "gmail",
        "account_hint": email_addr,
        "messages": messages,
        "count": len(messages),
        "cached": False,
    }


def _gmail_cache_fresh(g: Dict[str, Any], max_age_sec: float = 90.0) -> bool:
    inbox = g.get("inbox") or []
    if not inbox:
        return False
    epoch = g.get("last_sync_epoch")
    if epoch is None and g.get("last_sync"):
        try:
            # rough: treat as stale if we cannot parse
            epoch = 0.0
        except Exception:
            epoch = 0.0
    try:
        return (time.time() - float(epoch or 0)) < max_age_sec
    except Exception:
        return False


async def refresh_gmail_inbox(force: bool = False) -> Dict[str, Any]:
    """Prefer cached inbox for demos; force=True re-hits Gmail IMAP/OAuth."""
    import asyncio

    data = _load()
    g = data.get("gmail") or {}
    if not g.get("connected"):
        return {"ok": False, "error": "Gmail not connected", "messages": []}

    if not force and _gmail_cache_fresh(g):
        return {
            "ok": True,
            "messages": g.get("inbox") or [],
            "account_hint": g.get("account_hint"),
            "cached": True,
            "count": len(g.get("inbox") or []),
        }

    if g.get("mode") == "imap_app_password":
        # Never block the asyncio event loop — that freezes Chat Demo / health
        result = await asyncio.to_thread(
            connect_gmail_imap, g.get("email", ""), g.get("app_password", "")
        )
        if not result.get("ok") and (g.get("inbox") or []):
            # Soft-fail: return last good cache so demo still works
            return {
                "ok": True,
                "messages": g.get("inbox") or [],
                "account_hint": g.get("account_hint"),
                "cached": True,
                "warning": result.get("error"),
            }
        return result

    if g.get("mode") == "oauth" and g.get("access_token"):
        async with httpx.AsyncClient(timeout=12.0) as client:
            listed = await client.get(
                "https://gmail.googleapis.com/gmail/v1/users/me/messages",
                headers={"Authorization": f"Bearer {g['access_token']}"},
                params={"maxResults": 10, "q": "newer_than:14d"},
            )
            if listed.status_code >= 400:
                return {"ok": False, "error": listed.text[:300], "messages": g.get("inbox") or []}
            messages = []
            for item in (listed.json().get("messages") or [])[:10]:
                detail = await client.get(
                    f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{item['id']}",
                    headers={"Authorization": f"Bearer {g['access_token']}"},
                    params={"format": "full"},
                )
                if detail.status_code < 400:
                    messages.append(_parse_gmail_api_message(detail.json()))
        g["inbox"] = messages
        g["last_sync"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        g["last_sync_epoch"] = time.time()
        data["gmail"] = g
        _save(data)
        return {"ok": True, "messages": messages, "account_hint": g.get("account_hint"), "cached": False}
    return {"ok": True, "messages": g.get("inbox") or [], "cached": True}


# ── Instagram (Graph token) ───────────────────────────────────────────────────

async def connect_instagram(access_token: str, user_id: str = "me") -> Dict[str, Any]:
    access_token = (access_token or "").strip()
    if not access_token:
        return {"ok": False, "error": "Instagram Graph access token required"}
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(
            f"https://graph.facebook.com/v19.0/{user_id}",
            params={"fields": "id,username,name", "access_token": access_token},
        )
    if resp.status_code >= 400:
        return {"ok": False, "error": f"Instagram/Graph auth failed: {resp.text[:300]}"}
    profile = resp.json()
    hint = profile.get("username") or profile.get("name") or profile.get("id")
    data = _load()
    data["instagram"] = {
        "connected": True,
        "mode": "graph_api",
        "account_hint": f"@{hint}" if hint else "instagram",
        "access_token": access_token,
        "user_id": profile.get("id"),
        "inbox": data.get("instagram", {}).get("inbox") or [],
        "last_sync": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "last_error": None,
        "note": "Instagram messaging APIs require a Messenger/IG professional account. Paste DMs anytime; webhook ingest supported.",
    }
    _save(data)
    return {"ok": True, "channel": "instagram", "account_hint": data["instagram"]["account_hint"], "profile": profile}


def disconnect(channel: str) -> Dict[str, Any]:
    data = _load()
    if channel in data:
        data[channel] = {"connected": False, "inbox": [], "account_hint": None}
        _save(data)
    return {"ok": True, "channel": channel, "connected": False}


def get_inbox(channel: str) -> List[Dict[str, Any]]:
    data = _load()
    return list((data.get(channel) or {}).get("inbox") or [])
