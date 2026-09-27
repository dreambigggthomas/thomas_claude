# Building the Invoices (Step 3)

One purpose: how to turn the per-client data from `references/clients.md` into the actual `.docx` files.

## 1. Install the dependency once
From the skill's `scripts/` folder: `cd scripts && npm install` (installs `docx` from package.json). Skip if `node -e "require('docx')"` already succeeds from that folder.

## 2. Build the input JSON
Write a temp JSON file (anywhere, e.g. the OS temp dir) shaped like this, one entry per client, using the data from `references/clients.md` with `{MONTH}` / `{YEAR}` / `{MONTH_NUM}` placeholders substituted for the billing month:

```json
{
  "outputRoot": "./clients",
  "invoices": [
    {
      "client": "Thunder Thor Limited",
      "invoiceNo": "1170-04",
      "invoiceDate": "27-Oct-2026",
      "billTo": ["Thunder Thor Limited (Resurgo)"],
      "items": [
        { "description": "Nov 2026 platform hosting fee (US$32.00)", "amount": "HK$250.00" },
        { "description": "Nov 2026 maintenance fee", "amount": "HK$1,800.00" }
      ],
      "total": "HK$2,050.00"
    }
  ]
}
```

`termsUrl` is optional — include it only for clients that have one in `clients.md` (currently only Joinmax).

## 3. Run the generator
```
node scripts/generate.js /path/to/input.json
```
This writes each file to `<outputRoot>/<client folder>/invoice_<invoiceNo>.docx` and prints a JSON summary (client, invoice number, total, path) — use that to build the confirmation summary for the user.

## 4. Validate before showing the user
Run each output file through the docx skill's XSD validator so a malformed file is never handed over:
```
python3 <docx-skill-dir>/scripts/office/validate.py <output-file>.docx
```
(Find `<docx-skill-dir>` the same way you'd load any other skill's files — it is not part of this skill.) If a rendering preview is available in the environment, also render and look at one invoice before sending all 5.
