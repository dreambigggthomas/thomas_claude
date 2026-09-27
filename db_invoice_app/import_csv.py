"""
Bulk-import historical invoices from a CSV export into the tracker DB.

Usage:
    python3 import_csv.py <file.csv> [--status paid|sent]

CSV columns expected: amount, client, invoice_date, invoice_no
- amount: plain number, currency assumed HKD.
- invoice_date: "M/D/YY H:MM" (time is dropped, only the date is stored).
- client: matched to an existing tracker client by name, via NAME_ALIASES
  for known spelling variants in the export. Does NOT create new clients --
  every client in the CSV is expected to already exist in the tracker.
- invoice_no: imported as-is, even when it doesn't follow the xxxx-xx
  convention (older invoices predate that convention -- see clients.md /
  the generate-monthly-invoices skill for when it started). The client's
  running suffix counter is only advanced for rows that DO match
  "<client_id>-<n>", so legacy/mislabeled numbers under retired prefixes
  never affect the next auto-suggested invoice number.

paid_date is set equal to invoice_date when --status paid, since the CSV
has no separate payment-date column -- treat it as an approximation.
"""

import argparse
import csv
import sys
from datetime import datetime

from app import sync_client_suffix
from db import get_db, init_db

NAME_ALIASES = {
    "RPH Surveyor Ltd": "RPH",
}

# (client, invoice_no, invoice_date) rows to skip outright -- confirmed with
# the user as stray duplicates/mislabels in the source export.
SKIP_ROWS = {
    ("Excellence", "1010-19", "3/1/23 0:00"),  # predates the 1010 series (starts 9/22/24); duplicates the legitimate 3/1/26 entry
}


def parse_date(raw):
    return datetime.strptime(raw.strip(), "%m/%d/%y %H:%M").date().isoformat()


def resolve_client(db, csv_name):
    name = NAME_ALIASES.get(csv_name, csv_name)
    row = db.execute("SELECT * FROM clients WHERE name = ?", (name,)).fetchone()
    if not row:
        raise ValueError(f"No tracker client matches CSV client {csv_name!r} (tried name {name!r})")
    return row


def import_csv(csv_path, status):
    init_db()
    db = get_db()
    imported, skipped = [], []

    with open(csv_path) as f:
        for row in csv.DictReader(f):
            key = (row["client"], row["invoice_no"], row["invoice_date"])
            if key in SKIP_ROWS:
                skipped.append(row)
                continue

            client = resolve_client(db, row["client"])
            date_sent = parse_date(row["invoice_date"])
            invoice_number = row["invoice_no"].strip()
            amount = float(row["amount"])
            paid_date = date_sent if status == "paid" else None

            db.execute(
                """
                INSERT INTO invoices
                    (client_id, invoice_number, amount, currency, date_sent, status, paid_date)
                VALUES (?, ?, ?, 'HKD', ?, ?, ?)
                """,
                (client["id"], invoice_number, amount, date_sent, status, paid_date),
            )
            sync_client_suffix(db, client["id"], invoice_number)
            imported.append(row)

    db.commit()
    db.close()
    return imported, skipped


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path")
    parser.add_argument("--status", choices=["paid", "sent"], default="paid")
    args = parser.parse_args()

    imported, skipped = import_csv(args.csv_path, args.status)
    print(f"Imported {len(imported)} invoices, skipped {len(skipped)}.")
    for row in skipped:
        print(f"  skipped: {row}")
