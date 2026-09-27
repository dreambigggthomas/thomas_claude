---
name: generate-monthly-invoices
description: Generates this month's Word (.docx) invoices for all 5 Dreambiggg Co. Ltd. clients (Thunder Thor, Excellence Fitness, Charles Heica, Simpson Marine, Joinmax), using the standard branded template, auto-incrementing each client's invoice number, and saving each into its own client-named folder. Use when the user says "generate invoices", "generate this month's invoices", "run month-end invoicing", "do invoicing for [month]", or it is month-end and invoices need to go out.
---

# Generate Monthly Invoices

Produces one professional, branded invoice per client for a given billing month, using each client's fixed line items from `references/clients.md`, and saves them into per-client folders.

## Steps

```
Task Progress:
- [ ] 1. Get the billing month and invoice date
- [ ] 2. Read client data and compute next invoice numbers
- [ ] 3. Build the invoices
- [ ] 4. Confirm with the user
- [ ] 5. Update the invoice-number state
```

### 1. Get the billing month and invoice date
Ask the user which month is being billed, unless they already said it. Default invoice date is the 27th of the month before the billing month (matches this company's pattern of invoicing in advance) — confirm this default rather than assuming silently the first time.

### 2. Read client data and compute next invoice numbers
Read `references/clients.md`. For each of the 5 clients, take "Last suffix used" + 1 as the new invoice number suffix (e.g. `03` -> `04`), and substitute the billing month into any `{MONTH}` / `{Month}` / `{MONTH_NUM}` / `{YEAR}` placeholder in that client's line items, matching the exact capitalization style already noted for that client.

### 3. Build the invoices
Follow `references/build-invoice.md` to turn the computed data into `.docx` files via `scripts/generate.js`.

### 4. Confirm with the user
Show a summary table (client, invoice number, total, file path) and ask the user to open and check each file. Do not treat the run as final until they confirm — this is the checkpoint before the invoice-number state changes.

### 5. Update the invoice-number state
Once confirmed, edit `references/clients.md` and set each client's "Last suffix used" to the number just issued, so next month continues from the right place.

## Human checkpoints
Step 4 is required before step 5. Never advance the stored invoice numbers on unconfirmed output — a rerun after a correction must reuse the same invoice number, not skip ahead.

## Self-improvement
This skill is never finished. Improve it as you use it.
- When the user corrects a client's line items, amount, address, or template detail, update `references/clients.md` (data) or `scripts/make_invoice.js` (layout) immediately, not just for the current run.
- When a correction is a hard rule ("always/never do X for this client"), add it as a note under that client in `references/clients.md`.
- When the user adds a 6th client or drops one, add/remove their section in `references/clients.md` — no other file needs to change.
- Keep this file small: if an addition doesn't change what the agent does, don't add it.

## Routing
| Step | Reference |
|------|-----------|
| 2 | `references/clients.md` |
| 3 | `references/build-invoice.md` |
