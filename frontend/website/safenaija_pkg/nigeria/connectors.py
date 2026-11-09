"""Minimal connectors stub for serverless (no IMAP persistence)."""
from __future__ import annotations

from typing import Any, Dict, List


def status() -> Dict[str, Any]:
    return {
        "whatsapp": {"connected": False, "mode": "serverless"},
        "gmail": {"connected": False, "mode": "serverless"},
        "instagram": {"connected": False, "mode": "serverless"},
    }


def disconnect(channel: str) -> Dict[str, Any]:
    return {"ok": True, "channel": channel, "connected": False}


def get_inbox(channel: str) -> List[Dict[str, Any]]:
    return []


async def connect_whatsapp(*_a, **_k):
    return {"ok": False, "error": "Channel connect not available on serverless deploy"}


def gmail_oauth_start(*_a, **_k):
    return {"ok": False, "error": "OAuth not available on serverless deploy"}


async def gmail_oauth_callback(*_a, **_k):
    return {"ok": False, "error": "OAuth not available on serverless deploy"}


def connect_gmail_imap(*_a, **_k):
    return {"ok": False, "error": "IMAP not available on serverless deploy"}


async def connect_instagram(*_a, **_k):
    return {"ok": False, "error": "Instagram connect not available on serverless deploy"}


async def fetch_whatsapp_inbox():
    return {"ok": True, "messages": []}


async def refresh_gmail_inbox(force: bool = False):
    return {"ok": True, "messages": [], "cached": True}
