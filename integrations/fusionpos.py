"""FusionPOS connector — structural stub for Phase 0 (see ADR-004).

No real HTTP calls or credentials yet. Endpoint shapes match SPECIFICATION.md
(/api/v3/orders, /api/v3/inventory).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

import core.env  # noqa: F401  side effect: loads .env


@dataclass
class FusionPOSOrder:
    id: str
    total: float
    created_at: str


@dataclass
class FusionPOSInventoryItem:
    sku: str
    name: str
    quantity: float


class FusionPOSClient:
    BASE_URL = "https://fusionpos.ru/api/v3"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("FUSIONPOS_API_KEY")

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def get_orders(self, period: Optional[str] = None) -> list[FusionPOSOrder]:
        raise NotImplementedError(
            "FusionPOS integration is a structural stub (Phase 0, see ADR-004). "
            "Set FUSIONPOS_API_KEY and implement the real call to "
            f"{self.BASE_URL}/orders in Phase 1+."
        )

    def get_inventory(self) -> list[FusionPOSInventoryItem]:
        raise NotImplementedError(
            "FusionPOS integration is a structural stub (Phase 0, see ADR-004). "
            "Set FUSIONPOS_API_KEY and implement the real call to "
            f"{self.BASE_URL}/inventory in Phase 1+."
        )
