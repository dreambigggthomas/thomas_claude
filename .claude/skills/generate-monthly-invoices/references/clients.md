# Client Data (Step 1 source of truth)

One purpose: per-client billing data and the running invoice-number state. Read this before generating, and update the "Last suffix used" line for every client after the user confirms a run.

Company constants (same on every invoice, set in scripts/make_invoice.js): Dreambiggg Co. Ltd. | info@dreambiggg.app | www.dreambiggg.app | HSBC 652-298985-838.

Output root: `/Users/thomasho/Documents/Google_Drive_Backup/All invoices` (fixed absolute path, syncs to Google Drive — do not use a path relative to the current working directory). Output folder for each client = the exact "Folder name" below, created directly under this root.

Some line items contain a `{MONTH}` placeholder. Replace it with the billing month in the exact case style shown (e.g. "Oct 2026" vs "OCT 2026") — each client keeps its own historical style, do not standardize across clients.

---

## Thunder Thor Limited (Resurgo)
- Folder name: `Thunder Thor Limited`
- Invoice prefix: `1170`
- Last suffix used: `03`
- Bill To lines:
  - Thunder Thor Limited (Resurgo)
- Line items:
  1. `{Month} platform hosting fee (US$32.00)` — HK$250.00
  2. `{Month} maintenance fee` — HK$1,800.00
- Total: HK$2,050.00

## Excellence Fitness Ltd
- Folder name: `Excellence Fitness Ltd`
- Invoice prefix: `1010`
- Last suffix used: `28`
- Bill To lines (keep on separate lines, this is a Traditional Chinese address):
  - Excellence Fitness Ltd
  - 晉利商業大廈12樓
  - 油麻地彌敦道494-496號
- Line items:
  1. `{MONTH} Monthly Subscription Fee\n(2 shop x $600 each) Plus 2 freelance shop $200` — HK$1,400.00
- Total: HK$1,400.00

## Charles Heica Service Company Ltd.
- Folder name: `Charles Heica Service Company Ltd`
- Invoice prefix: `1150`
- Last suffix used: `04`
- Bill To lines:
  - Charlotte Chan / Charles Heica Service Company Ltd.
- Line items (no month name in the text — leave as-is every run):
  1. `Platform hosting fee US$32.00` — HK$250.00
  2. `WhatsApp and geo tracking integration US$15.00` — HK$115.00
  3. `Maintenance fee` — HK$1,500.00
- Total: HK$1,865.00

## Simpson Marine Limited
- Folder name: `Simpson Marine Limited`
- Invoice prefix: `1120`
- Last suffix used: `16`
- Bill To lines:
  - May Choi / Simpson Marine Limited
  - Unit 6 Ground Floor Aberdeen Marina Tower
  - 8 Shum Wan Road, Aberdeen, Hong Kong
- Line items (first line is Traditional Chinese, keep the exact characters and the full-width parentheses （）):
  1. `代付BUBBLE.IO平台月費（{YEAR}年{MONTH_NUM}月）US$134.00` — HK$1,050.00
  2. `{Month} maintenance fee` — HK$2,000.00
- Total: HK$3,050.00
- `{YEAR}` = the 4-digit billing year, `{MONTH_NUM}` = the month number (e.g. 10 for October).

## Miro (Trillion International Clothing co. ltd)
- Folder name: `Miro`
- Invoice prefix: `1050`
- Last suffix used: `35`
- Bill To lines:
  - Trillion International Clothing co. ltd
  - 香港九龍長沙灣永康街9號 地下G02號舖
- Line items:
  1. `MPOS {MONTH} Monthly Subscription Fee\n(10 x HK$960.00)` — HK$9,600.00
- Total: HK$9,600.00

## Joinmax Display & Productions Ltd
- Folder name: `Joinmax Display & Productions Ltd`
- Invoice prefix: `1100`
- Last suffix used: `10`
- Bill To lines:
  - Joinmax Display & Productions Ltd
  - Unit 231, 2/F, Focal Industrial Centre Blk B,
  - 21 Man Lok Street, Hung Hom, Kowloon, Hong Kong
- Line items:
  1. `{MONTH} subscription fee to provide system support and bug fix.\n(Includes US$32.00 hosting platform fee)` — HK$1,350.00
- Total: HK$1,350.00
- Terms URL: `https://bubble.io/terms` (only this client gets a Terms & Conditions section)
