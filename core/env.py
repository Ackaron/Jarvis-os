"""Loads .env once so os.getenv() picks up local secrets (Anthropic/Bitrix/
FusionPOS/Telegram/Google Calendar) across the app. Import this for its
side effect — safe to import multiple times, python-dotenv won't override
variables already set in the real environment."""

from __future__ import annotations

from dotenv import load_dotenv

load_dotenv()
