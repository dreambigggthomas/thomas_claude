const fs = require("fs");
const path = require("path");
const { buildInvoice } = require("./make_invoice");

// Usage: node generate.js <input.json>
// input.json shape: { outputRoot: string, invoices: [{ client, invoiceNo, invoiceDate, billTo: [string], items: [{description, amount}], total, termsUrl? }] }

const inputPath = process.argv[2];
if (!inputPath) {
  console.error("Usage: node generate.js <input.json>");
  process.exit(1);
}

const data = JSON.parse(fs.readFileSync(inputPath, "utf8"));
const outputRoot = data.outputRoot || "./clients";

(async () => {
  const results = [];
  for (const inv of data.invoices) {
    const outPath = path.join(outputRoot, inv.client, `invoice_${inv.invoiceNo}.docx`);
    await buildInvoice({ ...inv, outPath });
    results.push({ client: inv.client, invoiceNo: inv.invoiceNo, total: inv.total, path: outPath });
  }
  console.log(JSON.stringify(results, null, 2));
})();
