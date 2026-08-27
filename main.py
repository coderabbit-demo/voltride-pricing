"""Pricing service: turns base prices into quotes.

Rules:
  - stockCount > 20  -> 10% clearance discount
  - stockCount <= 2  -> 4% low-stock surcharge (expressed as negative discount)
  - promo code VOLT10 -> extra 10% off the subtotal
  - flat 8.75% sales tax
  - $49 shipping, free over $3,000 subtotal

Consumed by: catalog (display price), cart (totals), orders (final quote).
All three depend on the exact field names in QuoteResponse.
"""
from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel

from inventory_client import get_stock

app = FastAPI(title="pricing")

TAX_RATE = 0.0875
SHIPPING_CENTS = 4900
FREE_SHIPPING_THRESHOLD_CENTS = 300_000
CLEARANCE_DISCOUNT_PERCENT = 10
LOW_STOCK_SURCHARGE_PERCENT = 4
PROMO_CODES = {"VOLT10": 10}


class QuoteItemRequest(BaseModel):
    productId: str
    basePriceCents: int
    quantity: int


class QuoteRequest(BaseModel):
    items: List[QuoteItemRequest]
    promoCode: Optional[str] = None


class QuoteLineItem(BaseModel):
    productId: str
    unitPriceCents: int
    quantity: int
    discountPercent: int
    lineTotalCents: int


class QuoteResponse(BaseModel):
    lineItems: List[QuoteLineItem]
    subtotalCents: int
    discountCents: int
    taxCents: int
    shippingCents: int
    grandTotal: float
    promoApplied: bool


@app.get("/health")
def health():
    return {"status": "ok", "service": "pricing"}


@app.post("/api/quotes", response_model=QuoteResponse)
async def create_quote(req: QuoteRequest) -> QuoteResponse:
    line_items: List[QuoteLineItem] = []
    subtotal = 0
    full_price_total = 0

    for item in req.items:
        stock = await get_stock(item.productId)
        stock_count = stock.stock_count if stock else 0

        discount_percent = 0
        if stock_count > 20:
            discount_percent = CLEARANCE_DISCOUNT_PERCENT
        elif stock_count <= 2:
            discount_percent = -LOW_STOCK_SURCHARGE_PERCENT

        unit_price = round(item.basePriceCents * (100 - discount_percent) / 100)
        line_total = unit_price * item.quantity
        subtotal += line_total
        full_price_total += item.basePriceCents * item.quantity

        line_items.append(QuoteLineItem(
            productId=item.productId,
            unitPriceCents=unit_price,
            quantity=item.quantity,
            discountPercent=discount_percent,
            lineTotalCents=line_total,
        ))

    promo_applied = False
    promo_percent = PROMO_CODES.get((req.promoCode or "").upper())
    if promo_percent:
        subtotal = round(subtotal * (100 - promo_percent) / 100)
        promo_applied = True

    discount = full_price_total - subtotal
    tax = round(subtotal * TAX_RATE)
    shipping = 0 if subtotal >= FREE_SHIPPING_THRESHOLD_CENTS else SHIPPING_CENTS
    if not req.items:
        shipping = 0

    return QuoteResponse(
        lineItems=line_items,
        subtotalCents=subtotal,
        discountCents=discount,
        taxCents=tax,
        shippingCents=shipping,
        grandTotal=(subtotal + tax + shipping) / 100,
        promoApplied=promo_applied,
    )
