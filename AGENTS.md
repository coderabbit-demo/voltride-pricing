# AGENTS.md — voltride-pricing

Part of VoltRide, a multi-repo microservices demo (see the `voltride-platform` repo for the system map). Every repo hand-maintains local copies of its peers' contracts — there is **no shared types package anywhere in VoltRide**, and nothing must ever change that.

## Contracts this repo PRODUCES

| Contract | Consumer repo | Consumer file | Failure mode if changed |
|---|---|---|---|
| `QuoteResponse` (`lineItems[].unitPriceCents/discountPercent/lineTotalCents`, `subtotalCents`, `discountCents`, `taxCents`, `shippingCents`, `grandTotalCents`, `promoApplied`) | voltride-cart | `src/clients/pricingClient.ts` | cart totals render `undefined`/NaN |
| `QuoteResponse` | voltride-catalog | `src/clients/pricingClient.ts` | product detail price breaks |
| `QuoteResponse` | voltride-orders | `clients.go` (`Quote`) | Go decodes missing keys **silently** as 0 → orders stored and "charged" at $0.00 |
| `QuoteRequest` (strict Pydantic: `items[].productId/basePriceCents/quantity`, `promoCode`) | callers above | — | renamed/missing caller fields → 422 for every quote |

All money fields are integer cents; negative `discountPercent` means surcharge — consumers rely on that sign convention. Unit or type changes are breaking even if names stay similar.

## Contracts this repo CONSUMES

| Producer repo | Contract | Used in |
|---|---|---|
| voltride-inventory | stock record (`stockCount`) | `inventory_client.py` (missing key silently reads 0) |

**Changing any produced shape is a breaking change for the consumer repos above** — it cannot be fixed in this PR; open coordinated PRs and link them. When inventory changes, update `inventory_client.py`.

## Conventions

- `INVENTORY_URL` env var with localhost default; Python ≥ 3.9 (no `X | None` syntax).
- Verify with: venv import check (`python -c "import main"`), then run and curl `/api/quotes` for clearance (stock > 20), surcharge (stock ≤ 2), and `VOLT10` cases.
