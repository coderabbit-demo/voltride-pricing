# ⚡ voltride-pricing

Quote engine for the [VoltRide](https://github.com/coderabbit-demo/voltride-platform) e-bike store: discounts, surcharges, tax, and shipping. Python (FastAPI), stateless. Runs on **port 4005**.

Reads stock from [voltride-inventory](https://github.com/coderabbit-demo/voltride-inventory) to apply stock-based rules. Its quote response is consumed by [voltride-catalog](https://github.com/coderabbit-demo/voltride-catalog), [voltride-cart](https://github.com/coderabbit-demo/voltride-cart), and [voltride-orders](https://github.com/coderabbit-demo/voltride-orders). See `AGENTS.md` before changing any shape.

## Business rules

- Stock > 20 → 10% clearance discount · stock ≤ 2 → 4% low-stock surcharge (negative `discountPercent`)
- Promo code `VOLT10` → extra 10% off the subtotal
- 8.75% flat tax · $49 shipping, free over $3,000
- All money fields are **integer cents** (`*Cents`)

## Endpoints

- `GET /health`
- `POST /api/quotes` `{ items: [{productId, basePriceCents, quantity}], promoCode }` → quote with `lineItems`, `subtotalCents`, `discountCents`, `taxCents`, `shippingCents`, `grandTotalCents`, `promoApplied`

## Run

```sh
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn main:app --port 4005 --reload      # INVENTORY_URL env var supported
```

To run the whole VoltRide system, use the scripts in [voltride-platform](https://github.com/coderabbit-demo/voltride-platform).
