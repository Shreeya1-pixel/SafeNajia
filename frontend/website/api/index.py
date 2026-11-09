"""
Vercel Python entry — SafeNaija /api/nigeria/* offline engine.
Frontend calls /api/nigeria/... ; this app is mounted at /api.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from safenaija_pkg.nigeria import connectors  # noqa: E402
from safenaija_pkg.nigeria.engine import SafeNaijaEngine  # noqa: E402

engine = SafeNaijaEngine()

app = FastAPI(title="SafeNaija API", version="3.0.0-ng-vercel")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MessageScanRequest(BaseModel):
    text: str = Field(..., min_length=1)
    channel: str = "manual"
    offline: bool = True


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
    run_google_search: bool = False


class OsintRequest(BaseModel):
    full_name: str = ""
    phone: str = ""
    city: str = "Lagos"


class AlertSimRequest(BaseModel):
    scenario: str = "sim_swap"


class AttackSimRequest(BaseModel):
    attack_type: str = "phishing"


@app.get("/api/nigeria/health")
@app.get("/nigeria/health")
async def nigeria_health():
    return {
        "status": "healthy",
        "service": "SafeNaija",
        "country": "NG",
        "deploy": "vercel",
        "channels": connectors.status(),
        "offline": engine.offline_status(),
    }


@app.get("/api/nigeria/channels")
@app.get("/nigeria/channels")
async def list_channels():
    meta = engine.scan_channels_meta()
    live = connectors.status()
    for item in meta["supported"]:
        if item["id"] in live:
            item.update(live[item["id"]])
    return meta


@app.post("/api/nigeria/scan/message")
@app.post("/nigeria/scan/message")
async def scan_message(req: MessageScanRequest):
    return engine.scan_message(req.text, channel=req.channel, offline=req.offline)


@app.post("/api/nigeria/scan/link")
@app.post("/nigeria/scan/link")
async def scan_link(req: LinkScanRequest):
    return engine.scan_link(req.url, accompanying_text=req.accompanying_text)


@app.post("/api/nigeria/scan/github")
@app.post("/nigeria/scan/github")
async def scan_github(req: LinkScanRequest):
    return engine.scan_github(req.url)


@app.post("/api/nigeria/phone/check")
@app.post("/nigeria/phone/check")
async def phone_check(req: PhoneCheckRequest):
    return engine.check_phone(req.number)


@app.post("/api/nigeria/sim-swap/risk")
@app.post("/nigeria/sim-swap/risk")
async def sim_swap_risk(req: SimSwapRiskRequest):
    payload = req.model_dump()
    if not payload.get("run_google_search"):
        payload.pop("full_name", None)
        payload.pop("phone", None)
    return engine.sim_swap_risk(payload)


@app.post("/api/nigeria/sim-swap/osint")
@app.post("/nigeria/sim-swap/osint")
async def sim_swap_osint(req: OsintRequest):
    return engine.google_osint_search(req.full_name, phone=req.phone, city=req.city)


@app.post("/api/nigeria/sim-swap/alerts/simulate")
@app.post("/nigeria/sim-swap/alerts/simulate")
async def sim_swap_alerts(req: AlertSimRequest):
    return engine.simulate_alerts(req.scenario)


@app.post("/api/nigeria/attacks/simulate")
@app.post("/nigeria/attacks/simulate")
async def attacks_simulate(req: AttackSimRequest):
    return engine.attack_simulation(req.attack_type)


@app.get("/api/nigeria/attacks/catalog")
@app.get("/nigeria/attacks/catalog")
async def attacks_catalog():
    return {
        "attacks": [
            {"id": "phishing", "label": "Bank phishing (WhatsApp)"},
            {"id": "investment", "label": "Fake crypto investment"},
            {"id": "sim_swap", "label": "SIM swap social engineering"},
            {"id": "fake_loan", "label": "Predatory loan app"},
            {"id": "github_secret", "label": "Student GitHub secret leak"},
        ]
    }


@app.get("/api/nigeria/offline")
@app.get("/nigeria/offline")
async def offline_info():
    return engine.offline_status()


@app.get("/api/nigeria/features")
@app.get("/nigeria/features")
async def features():
    return {"product": "SafeNaija", "deploy": "vercel"}


@app.post("/api/nigeria/channels/{channel}/disconnect")
@app.post("/nigeria/channels/{channel}/disconnect")
async def channel_disconnect(channel: str):
    return connectors.disconnect(channel)


@app.get("/api/nigeria/channels/{channel}/inbox")
@app.get("/nigeria/channels/{channel}/inbox")
async def channel_inbox(channel: str, force: bool = False):
    return {"ok": True, "messages": connectors.get_inbox(channel)}


@app.post("/api/nigeria/channels/{channel}/inbox/scan")
@app.post("/nigeria/channels/{channel}/inbox/scan")
async def scan_channel_inbox(channel: str, force: bool = False):
    return {"ok": True, "count": 0, "results": [], "warning": "Inbox scan unavailable on serverless"}
