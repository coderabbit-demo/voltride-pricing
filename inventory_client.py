"""HTTP client for the inventory service.

Pricing keeps its own local view of the inventory contract: it only cares
about stockCount. If inventory renames that field, quotes silently lose
their stock-based discount/surcharge rules.
"""
import os
from dataclasses import dataclass
from typing import Optional

import httpx

INVENTORY_URL = os.environ.get("INVENTORY_URL", "http://localhost:4003")


@dataclass
class StockLevel:
    product_id: str
    stock_count: int


async def get_stock(product_id: str) -> Optional[StockLevel]:
    async with httpx.AsyncClient(timeout=5.0) as client:
        resp = await client.get(f"{INVENTORY_URL}/api/stock/{product_id}")
    if resp.status_code != 200:
        return None
    data = resp.json()
    return StockLevel(
        product_id=data.get("productId", product_id),
        stock_count=data.get("stockCount", 0),
    )
