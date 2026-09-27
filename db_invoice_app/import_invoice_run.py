"""
Log a completed generate-monthly-invoices run into the invoice tracker DB.

Usage:
    python3 import_invoice_run.py <input.json>

<input.json> is the same file the generate-monthly-invoices skill builds for
scripts/generate.js: {outputRoot, invoices: [{client, invoiceNo, invoiceDate,
total, ...}]}. Each invoice becomes one row in invoices.db, status "sent".
Re-running with the same client + invoice number updates that row (amount,
date, file path) instead of duplicating it, but never touches status or
paid_date once a human has set them via the tracker UI.
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

from db import get_db, init_db

AMOUNT_RE = re.compile(r"([A-Za-z$]+)\s*([\d,]+(?:\.\d+)?)")


def parse_amount(total):
    match = AMOUNT_RE.match(total.strip())
    if not match:
        raise ValueError(f"Could not parse amount from {total!r}")
    symbol, number = match.groups()
    currency = "HKD" if "HK" in symbol.upper() else symbol.upper().strip("$")
    return float(number.replace(",", "")), currency


def parse_date(invoice_date):
    return datetime.strptime(invoice_date.strip(), "%d-%b-%Y").date().isoformat()


INVOICE_NO_RE = re.compile(r"^(\d{4})-(\d+)$")


def get_or_create_client(db, invoice_no, fallback_name):
    """Match by the invoice number's 4-digit prefix (the tracker's client ID),
    not by name — the skill's internal client names (e.g. "Thunder Thor
    Limited") can differ from the tracker's display names (e.g. "Resurgo")."""
    match = INVOICE_NO_RE.match(invoice_no)
    if not match:
        raise ValueError(f"Invoice number {invoice_no!r} doesn't look like xxxx-xx")
    prefix, suffix = match.group(1), int(match.group(2))

    row = db.execute("SELECT * FROM clients WHERE client_id = ?", (prefix,)).fetchone()
    if not row:
        cur = db.execute(
            "INSERT INTO clients (name, client_id, last_suffix_used) VALUES (?, ?, ?)",
            (fallback_name, prefix, suffix),
        )
        return cur.lastrowid

    if suffix > row["last_suffix_used"]:
        db.execute("UPDATE clients SET last_suffix_used = ? WHERE id = ?", (suffix, row["id"]))
    return row["id"]


def import_run(input_path):
    data = json.loads(Path(input_path).read_text())
    output_root = data.get("outputRoot", "")

    init_db()
    db = get_db()
    logged = []
    for inv in data["invoices"]:
        client_id = get_or_create_client(db, inv["invoiceNo"], inv["client"])
        amount, currency = parse_amount(inv["total"])
        date_sent = parse_date(inv["invoiceDate"])
        file_path = str(Path(output_root) / inv["client"] / f"invoice_{inv['invoiceNo']}.docx")

        existing = db.execute(
            "SELECT id FROM invoices WHERE client_id = ? AND invoice_number = ?",
            (client_id, inv["invoiceNo"]),
        ).fetchone()

        if existing:
            db.execute(
                "UPDATE invoices SET amount = ?, currency = ?, date_sent = ?, file_path = ? WHERE id = ?",
                (amount, currency, date_sent, file_path, existing["id"]),
            )
        else:
            db.execute(
                """
                INSERT INTO invoices
                    (client_id, invoice_number, amount, currency, date_sent, status, file_path)
                VALUES (?, ?, ?, ?, ?, 'sent', ?)
                """,
                (client_id, inv["invoiceNo"], amount, currency, date_sent, file_path),
            )
        logged.append({"client": inv["client"], "invoiceNo": inv["invoiceNo"], "amount": amount, "currency": currency})

    db.commit()
    db.close()
    return logged


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 import_invoice_run.py <input.json>", file=sys.stderr)
        sys.exit(1)
    result = import_run(sys.argv[1])
    print(json.dumps(result, indent=2))
