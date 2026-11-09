"""
SafeNaija — FastAPI application entry point (fork of SafeO / Tatweer for Nigeria).

Registers legacy SafeO routes plus Nigeria-specific /nigeria/* APIs.
"""
import asyncio
import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import waf, simulate, feedback, metrics, erp, investigations, universal, scanner, whatsapp, nigeria
from .routers import ws as ws_router
from .middleware.auth import BearerAuthMiddleware
from .agents.behavior_agent import BehaviorAgent
from .models.schemas import BehaviorRequest

logger = logging.getLogger("safeo.startup")

app = FastAPI(
    title="SafeNaija — Nigeria Cyber-Safety API",
    description=(
        "SafeNaija (forked from SafeO / Tatweer): AI-assisted scam, phishing, crypto-fraud, "
        "fraud-call, and SIM-swap risk detection for Nigeria — with offline phrase packs "
        "for English, Pidgin, Hausa, Yoruba, and Igbo."
    ),
    version="3.0.0-ng",
    docs_url="/docs",
    redoc_url="/redoc",
)

_cors_origins = [
    o.strip()
    for o in (
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:8069",
        "http://127.0.0.1:8069",
        "*",
        *(os.getenv("CORS_ORIGINS", "").split(",") if os.getenv("CORS_ORIGINS") else []),
    )
    if o and o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(BearerAuthMiddleware)

app.include_router(waf.router)
app.include_router(simulate.router)
app.include_router(feedback.router)
app.include_router(metrics.router)
app.include_router(metrics.agents_router)
app.include_router(metrics.ml_router)
app.include_router(erp.router)
app.include_router(investigations.router)
app.include_router(universal.router)
app.include_router(scanner.router)
app.include_router(ws_router.router)
app.include_router(whatsapp.router)
app.include_router(nigeria.router)

_behavior_agent = BehaviorAgent()


def _startup_summary() -> None:
    """Print component readiness table on boot."""
    gpu_name = "none"
    gpu_ok = "no"
    try:
        from .utils.gpu_monitor import get_gpu_stats
        gs = get_gpu_stats()
        if gs.get("rocm_available"):
            gpu_ok = "yes"
            gpu_name = gs.get("device_name", "AMD GPU")
    except Exception:
        pass

    vllm_status = "unreachable"
    try:
        from .core.ml.llm_guard import is_llm_available
        vllm_status = "reachable" if is_llm_available() else "unreachable"
    except Exception:
        pass

    tier2_status = "fallback"
    try:
        from .core.ml.tier2_classifier import get_tier2_classifier
        clf = get_tier2_classifier()
        tier2_status = "loaded" if clf._model is not None else "fallback"
    except Exception:
        pass

    ml_status = "fallback"
    try:
        from .agents.multilingual_agent import MultilingualAgent
        ml_status = "loaded" if MultilingualAgent._model is not None else "fallback"
    except Exception:
        pass

    from .band.bridge import BAND_ENABLED, _band_agents
    if BAND_ENABLED:
        band_status = f"enabled, {len(_band_agents)} agents connected"
    else:
        band_status = "disabled (set BAND_ENABLED=true to enable)"

    lines = [
        "",
        "╔══════════════════════════════════════════════════════╗",
        "║             SafeNaija (NG) Engine Ready                ║",
        "╠══════════════════════════════════════════════════════╣",
        f"║  AMD GPU detected     : {gpu_ok:<28} ║",
        f"║  Device name          : {gpu_name[:28]:<28} ║",
        f"║  vLLM server          : {vllm_status:<28} ║",
        f"║  Tier 2 model         : {tier2_status:<28} ║",
        f"║  Multilingual model   : {ml_status:<28} ║",
        f"║  Band                 : {band_status[:28]:<28} ║",
        "║  SafeNaija on port    : 8001                         ║",
        "║  Nigeria API          : /nigeria/*                   ║",
        "╚══════════════════════════════════════════════════════╝",
        "",
    ]
    banner = "\n".join(lines)
    print(banner)
    logger.info("SafeNaija startup: gpu=%s vllm=%s tier2=%s ml=%s", gpu_ok, vllm_status, tier2_status, ml_status)


@app.on_event("startup")
async def on_startup():
    try:
        from .utils.gpu_monitor import register_model
        register_model("distilbert-tier2")
        register_model("arabert-multilingual")
    except Exception:
        pass
    from .band.bridge import BAND_ENABLED, _init_band_agents
    if BAND_ENABLED:
        asyncio.create_task(_init_band_agents())
    _startup_summary()


@app.post("/waf/behavior")
async def track_behavior(req: BehaviorRequest):
    return _behavior_agent.track_action(req.user_id, req.action)


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "SafeNaija", "country": "NG", "version": "3.0.0-ng"}


@app.get("/")
async def root():
    return {
        "service": "SafeNaija — Nigeria Cyber-Safety",
        "version": "3.0.0-ng",
        "fork_of": "SafeO (Tatweer)",
        "nigeria_api": [
            "/nigeria/health",
            "/nigeria/features",
            "/nigeria/scan/message",
            "/nigeria/scan/link",
            "/nigeria/scan/github",
            "/nigeria/phone/check",
            "/nigeria/language/detect",
            "/nigeria/sim-swap/risk",
            "/nigeria/sim-swap/alerts/simulate",
            "/nigeria/attacks/simulate",
            "/nigeria/offline",
        ],
        "legacy_safeo": [
            "/v1/scan",
            "/scanner/website",
            "/webhooks/whatsapp",
            "/docs",
        ],
    }
