"""Loads routing/domains config from vault/system/ (single source of truth, see ADR-004)."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

VAULT_SYSTEM_DIR = Path(__file__).resolve().parent.parent / "vault" / "system"


class ConfigNotFoundError(FileNotFoundError):
    """Raised when a required vault/system config file is missing."""


def _load_yaml(filename: str) -> dict:
    path = VAULT_SYSTEM_DIR / filename
    if not path.exists():
        raise ConfigNotFoundError(
            f"Config '{filename}' not found in {VAULT_SYSTEM_DIR}. "
            "Expected it to exist as part of Phase 0 scaffold (see ADR-004)."
        )
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data or {}


@lru_cache(maxsize=None)
def get_routing_config() -> dict:
    return _load_yaml("routing.yaml")


@lru_cache(maxsize=None)
def get_domains_config() -> dict:
    return _load_yaml("domains.yaml")


def clear_cache() -> None:
    """Forces configs to be re-read from disk on next access (tests / hot-reload)."""
    get_routing_config.cache_clear()
    get_domains_config.cache_clear()
