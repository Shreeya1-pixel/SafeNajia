"""
SafeNaija HTTP API — Nigeria ThinkAI / Imagine Cup features.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel, Field

from ..nigeria import connectors
from ..nigeria.engine import SafeNaijaEngine

router = APIRouter(prefix="/nigeria", tags=["SafeNaija — Nigeria"])
engine = SafeNaijaEngine()


class MessageScanRequest(BaseModel):
    text: str = Field(..., min_length=1)
    channel: str = "manual"
    offline: bool = True


class BatchMessageRequest(BaseModel):
    messages: List[MessageScanRequest]


class LinkScanRequest(BaseModel):
    url: str = Field(..., min_length=1)
    accompanying_text: str = ""


class PhoneCheckRequest(BaseModel):
    number: str = Field(..., min_length=3)


class SimSwapRiskRequest(BaseModel):
    phone_public_on_social: bool = False
    nin_or_bvn_shared_before: bool = False
    email_breached_known: bool = False
    reused_passwords: bool = False
    no_bank_transaction_alerts: bool = False
    dual_sim_unknown_apps: bool = False
    recent_sim_issues: bool = False
    public_home_address: bool = False
    full_name: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = "Lagos"
    run_google_search: bool = True


class OsintRequest(BaseModel):
    full_name: str = ""
    phone: str = ""
    city: str = "Lagos"


class AlertSimRequest(BaseModel):
    scenario: str = "sim_swap"


class AttackSimRequest(BaseModel):
    attack_type: str = "phishing"


class WhatsAppConnectRequest(BaseModel):
    phone_number_id: str
    access_token: str
    verify_token: str = "safenaija"


class GmailImapRequest(BaseModel):
    email: str
    app_password: str


class InstagramConnectRequest(BaseModel):
    access_token: str
    user_id: str = "me"


@router.get("/health")
async def nigeria_health():
    return {
        "status": "healthy",
        "service": "SafeNaija",
        "country": "NG",
        "fork_of": "SafeO (Tatweer)",
        "channels": connectors.status(),
        "offline": engine.offline_status(),
    }


@router.get("/channels")
async def list_channels():
    meta = engine.scan_channels_meta()
    live = connectors.status()
    for item in meta["supported"]:
        if item["id"] in live:
            item.update(live[item["id"]])
            if item["id"] == "whatsapp":
                item["connect_mode"] = "meta_cloud_api"
                item["note"] = "Enter Meta WhatsApp Cloud API Phone Number ID + Access Token. Webhook: /webhooks/whatsapp"
            elif item["id"] == "gmail":
                item["connect_mode"] = "oauth_or_imap"
                item["note"] = "Connect with Google OAuth or a Gmail App Password (IMAP)."
            elif item["id"] == "instagram":
                item["connect_mode"] = "graph_token"
                item["note"] = "Paste Instagram Graph / Meta access token for a professional account."
    return meta


@router.post("/channels/whatsapp/connect")
async def whatsapp_connect(req: WhatsAppConnectRequest):
    return await connectors.connect_whatsapp(req.phone_number_id, req.access_token, req.verify_token)


@router.get("/channels/gmail/oauth/start")
async def gmail_oauth_start(redirect_uri: Optional[str] = None):
    return connectors.gmail_oauth_start(redirect_uri)


@router.get("/channels/gmail/callback")
async def gmail_oauth_callback(code: str = Query(...), redirect_uri: Optional[str] = None):
    result = await connectors.gmail_oauth_callback(code, redirect_uri)
    if result.get("ok"):
        # bounce back to UI
        return RedirectResponse(url="http://127.0.0.1:5174/messages?gmail=connected")
    return HTMLResponse(
        f"<h3>Gmail connect failed</h3><pre>{result.get('error')}</pre>"
        f"<p><a href='http://127.0.0.1:5174/messages'>Back to SafeNaija</a></p>",
        status_code=400,
    )


@router.post("/channels/gmail/imap")
async def gmail_imap(req: GmailImapRequest):
    import asyncio

    return await asyncio.to_thread(connectors.connect_gmail_imap, req.email, req.app_password)


@router.post("/channels/instagram/connect")
async def instagram_connect(req: InstagramConnectRequest):
    return await connectors.connect_instagram(req.access_token, req.user_id)


@router.post("/channels/{channel}/disconnect")
async def channel_disconnect(channel: str):
    return connectors.disconnect(channel)


@router.get("/channels/{channel}/inbox")
async def channel_inbox(channel: str, force: bool = False):
    channel = channel.lower()
    if channel == "gmail":
        return await connectors.refresh_gmail_inbox(force=force)
    if channel == "whatsapp":
        return await connectors.fetch_whatsapp_inbox()
    return {"ok": True, "messages": connectors.get_inbox(channel)}


@router.post("/channels/{channel}/inbox/scan")
async def scan_channel_inbox(channel: str, force: bool = False):
    """Scan cached inbox by default so Chat Demo / Messages stay snappy."""
    channel = channel.lower()
    if channel == "gmail":
        box = await connectors.refresh_gmail_inbox(force=force)
    elif channel == "whatsapp":
        box = await connectors.fetch_whatsapp_inbox()
    else:
        box = {"ok": True, "messages": connectors.get_inbox(channel)}
    messages = box.get("messages") or []
    results = []
    for m in messages:
        text = m.get("text") or ""
        if m.get("subject"):
            text = f"{m.get('subject')}\n{text}"
        scanned = engine.scan_message(text, channel=channel, offline=True)
        results.append({"message": m, "scan": scanned})
    return {
        "ok": True,
        "count": len(results),
        "results": results,
        "account_hint": box.get("account_hint"),
        "cached": box.get("cached"),
        "warning": box.get("warning"),
    }


@router.post("/scan/message")
async def scan_message(req: MessageScanRequest):
    return engine.scan_message(req.text, channel=req.channel, offline=req.offline)


@router.post("/scan/messages")
async def scan_messages(req: BatchMessageRequest):
    return {
        "results": [
            engine.scan_message(m.text, channel=m.channel, offline=m.offline) for m in req.messages
        ]
    }


@router.post("/scan/link")
async def scan_link(req: LinkScanRequest):
    return engine.scan_link(req.url, accompanying_text=req.accompanying_text)


@router.post("/scan/github")
async def scan_github(req: LinkScanRequest):
    return engine.scan_github(req.url)


@router.post("/scan/crypto")
async def scan_crypto(req: LinkScanRequest):
    result = engine.scan_link(req.url, accompanying_text=req.accompanying_text)
    result["focus"] = "crypto_investment"
    return result


@router.post("/phone/check")
async def phone_check(req: PhoneCheckRequest):
    return engine.check_phone(req.number)


@router.post("/language/detect")
async def language_detect(req: MessageScanRequest):
    """Embedded helper — language detection is not a separate product page."""
    return engine.detect_languages(req.text)


@router.post("/sim-swap/osint")
async def sim_swap_osint(req: OsintRequest):
    return engine.google_osint_search(req.full_name, phone=req.phone, city=req.city)


@router.post("/sim-swap/risk")
async def sim_swap_risk(req: SimSwapRiskRequest):
    payload = req.model_dump()
    if not payload.get("run_google_search"):
        payload.pop("full_name", None)
        payload.pop("phone", None)
    return engine.sim_swap_risk(payload)


@router.post("/sim-swap/alerts/simulate")
async def sim_swap_alerts(req: AlertSimRequest):
    return engine.simulate_alerts(req.scenario)


@router.post("/attacks/simulate")
async def attacks_simulate(req: AttackSimRequest):
    return engine.attack_simulation(req.attack_type)


@router.get("/attacks/catalog")
async def attacks_catalog():
    return {
        "note": "Attack simulation lives under SIM Swap / Threat Lab (same family of demos).",
        "attacks": [
            {"id": "phishing", "label": "Bank phishing (WhatsApp)"},
            {"id": "investment", "label": "Fake crypto investment"},
            {"id": "sim_swap", "label": "SIM swap social engineering"},
            {"id": "fake_loan", "label": "Predatory loan app"},
            {"id": "github_secret", "label": "Student GitHub secret leak"},
        ],
    }


@router.get("/offline")
async def offline_info():
    return engine.offline_status()


@router.get("/features")
async def features():
    return {
        "product": "SafeNaija",
        "features": [
            {"id": 1, "name": "Message Scam Detection (+ email fields)", "path": "POST /nigeria/scan/message"},
            {"id": 2, "name": "Link & Crypto + Student Risk Passport", "path": "POST /nigeria/scan/link · /nigeria/scan/github"},
            {"id": 3, "name": "Fraud Call Detection", "path": "POST /nigeria/phone/check"},
            {"id": 4, "name": "Nigerian languages (embedded)", "path": "included in message/link/call scans"},
            {"id": 5, "name": "SIM Swap Risk + Google OSINT", "path": "POST /nigeria/sim-swap/risk"},
            {"id": 6, "name": "SIM Swap & Bank Account Alerts", "path": "POST /nigeria/sim-swap/alerts/simulate"},
            {"id": 7, "name": "Attack Simulation (same lab as SIM Swap)", "path": "POST /nigeria/attacks/simulate"},
            {"id": 8, "name": "Offline Capability", "path": "GET /nigeria/offline"},
            {"id": 9, "name": "Trust Chain explainability", "path": "UI on /messages /links /calls"},
            {"id": 10, "name": "Case Library & trusted entities", "path": "UI /cases"},
        ],
    }
