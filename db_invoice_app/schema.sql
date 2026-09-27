CREATE TABLE IF NOT EXISTS clients (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    name                 TEXT NOT NULL UNIQUE,
    client_id            TEXT NOT NULL UNIQUE,
    last_suffix_used     INTEGER NOT NULL DEFAULT 0,
    monthly_subscription REAL,
    email                TEXT,
    notes                TEXT
);

CREATE TABLE IF NOT EXISTS invoices (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id       INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    invoice_number  TEXT NOT NULL,
    amount          REAL NOT NULL,
    currency        TEXT NOT NULL DEFAULT 'HKD',
    date_sent       TEXT NOT NULL,
    due_date        TEXT,
    status          TEXT NOT NULL DEFAULT 'sent' CHECK (status IN ('draft', 'sent', 'paid', 'overdue', 'cancelled')),
    paid_date       TEXT,
    notes           TEXT,
    file_path       TEXT,
    created_at      TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (client_id, invoice_number)
);

CREATE INDEX IF NOT EXISTS idx_invoices_client ON invoices(client_id);
CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status);
