import re
import sqlite3
from datetime import date
from functools import wraps

from flask import Flask, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from db import get_db, init_db

try:
    from config import PASSWORD_HASH, SECRET_KEY
except ImportError:
    raise RuntimeError(
        "Missing config.py. Copy config.py.example to config.py and fill in "
        "SECRET_KEY and PASSWORD_HASH (see that file for how to generate them)."
    )

app = Flask(__name__)
app.secret_key = SECRET_KEY


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)

    return wrapped


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        if check_password_hash(PASSWORD_HASH, request.form.get("password", "")):
            session["logged_in"] = True
            return redirect(request.args.get("next") or url_for("dashboard"))
        error = "Incorrect password."
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.template_filter("money")
def money(value):
    return f"{value:,.2f}"


SUFFIX_RE = re.compile(r"^(\d+)-(\d+)$")


def next_invoice_number(client_row):
    return f"{client_row['client_id']}-{client_row['last_suffix_used'] + 1:02d}"


def sync_client_suffix(db, client_row_id, invoice_number):
    """After an invoice is saved with a given number, bump the client's
    running counter to at least that suffix, so the next auto-suggested
    number never collides with one just entered (auto or manual)."""
    match = SUFFIX_RE.match(invoice_number.strip())
    if not match:
        return
    prefix, suffix = match.group(1), int(match.group(2))
    client = db.execute("SELECT * FROM clients WHERE id = ?", (client_row_id,)).fetchone()
    if client and client["client_id"] == prefix and suffix > client["last_suffix_used"]:
        db.execute("UPDATE clients SET last_suffix_used = ? WHERE id = ?", (suffix, client_row_id))


@app.route("/")
@login_required
def dashboard():
    status_filter = request.args.get("status", "")
    client_filter = request.args.get("client_id", "")

    query = """
        SELECT invoices.*, clients.name AS client_name
        FROM invoices
        JOIN clients ON clients.id = invoices.client_id
        WHERE 1=1
    """
    params = []
    if status_filter:
        query += " AND invoices.status = ?"
        params.append(status_filter)
    if client_filter:
        query += " AND invoices.client_id = ?"
        params.append(client_filter)
    query += " ORDER BY invoices.date_sent DESC, invoices.id DESC"

    db = get_db()
    invoices = db.execute(query, params).fetchall()
    clients = db.execute("SELECT * FROM clients ORDER BY name").fetchall()

    totals = db.execute(
        """
        SELECT
            COALESCE(SUM(CASE WHEN status IN ('sent', 'overdue') THEN amount ELSE 0 END), 0) AS outstanding,
            COALESCE(SUM(CASE WHEN status = 'paid' THEN amount ELSE 0 END), 0) AS paid
        FROM invoices
        """
    ).fetchone()

    monthly_recurring = db.execute(
        "SELECT COALESCE(SUM(monthly_subscription), 0) AS total FROM clients"
    ).fetchone()["total"]

    client_total = None
    if client_filter:
        row = db.execute(
            "SELECT clients.name, clients.monthly_subscription, COALESCE(SUM(invoices.amount), 0) AS total FROM clients "
            "LEFT JOIN invoices ON invoices.client_id = clients.id WHERE clients.id = ? GROUP BY clients.id",
            (client_filter,),
        ).fetchone()
        client_total = dict(row) if row else None
    db.close()

    return render_template(
        "index.html",
        invoices=invoices,
        clients=clients,
        totals=totals,
        monthly_recurring=monthly_recurring,
        client_total=client_total,
        status_filter=status_filter,
        client_filter=client_filter,
        today=date.today().isoformat(),
    )


@app.route("/invoices/add", methods=["GET", "POST"])
@login_required
def add_invoice():
    db = get_db()
    if request.method == "POST":
        client_row_id = int(request.form["client_id"])
        invoice_number = request.form["invoice_number"].strip()

        db.execute(
            """
            INSERT INTO invoices
                (client_id, invoice_number, amount, currency, date_sent, due_date, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                client_row_id,
                invoice_number,
                float(request.form["amount"]),
                request.form.get("currency", "HKD").strip() or "HKD",
                request.form["date_sent"],
                request.form.get("due_date") or None,
                request.form.get("status", "sent"),
                request.form.get("notes", "").strip(),
            ),
        )
        sync_client_suffix(db, client_row_id, invoice_number)
        db.commit()
        db.close()
        return redirect(url_for("dashboard"))

    clients = db.execute("SELECT * FROM clients ORDER BY name").fetchall()
    suggested = {c["id"]: next_invoice_number(c) for c in clients}
    db.close()
    return render_template(
        "invoice_form.html", clients=clients, invoice=None, suggested=suggested, today=date.today().isoformat()
    )


@app.route("/invoices/<int:invoice_id>/edit", methods=["GET", "POST"])
@login_required
def edit_invoice(invoice_id):
    db = get_db()
    if request.method == "POST":
        invoice_number = request.form["invoice_number"].strip()
        current = db.execute("SELECT client_id FROM invoices WHERE id = ?", (invoice_id,)).fetchone()
        db.execute(
            """
            UPDATE invoices
            SET invoice_number = ?, amount = ?, currency = ?, date_sent = ?,
                due_date = ?, status = ?, paid_date = ?, notes = ?
            WHERE id = ?
            """,
            (
                invoice_number,
                float(request.form["amount"]),
                request.form.get("currency", "HKD").strip() or "HKD",
                request.form["date_sent"],
                request.form.get("due_date") or None,
                request.form.get("status", "sent"),
                request.form.get("paid_date") or None,
                request.form.get("notes", "").strip(),
                invoice_id,
            ),
        )
        sync_client_suffix(db, current["client_id"], invoice_number)
        db.commit()
        db.close()
        return redirect(url_for("dashboard"))

    invoice = db.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,)).fetchone()
    clients = db.execute("SELECT * FROM clients ORDER BY name").fetchall()
    db.close()
    return render_template("invoice_form.html", clients=clients, invoice=invoice, suggested={}, today=date.today().isoformat())


@app.route("/invoices/<int:invoice_id>/mark_paid", methods=["POST"])
@login_required
def mark_paid(invoice_id):
    db = get_db()
    db.execute(
        "UPDATE invoices SET status = 'paid', paid_date = ? WHERE id = ?",
        (date.today().isoformat(), invoice_id),
    )
    db.commit()
    db.close()
    return redirect(request.referrer or url_for("dashboard"))


@app.route("/invoices/<int:invoice_id>/delete", methods=["POST"])
@login_required
def delete_invoice(invoice_id):
    db = get_db()
    db.execute("DELETE FROM invoices WHERE id = ?", (invoice_id,))
    db.commit()
    db.close()
    return redirect(request.referrer or url_for("dashboard"))


def parse_subscription(form):
    raw = form.get("monthly_subscription", "").strip()
    return float(raw) if raw else None


@app.route("/clients")
@login_required
def clients_page():
    db = get_db()
    clients = db.execute(
        """
        SELECT clients.*,
            COUNT(invoices.id) AS invoice_count,
            COALESCE(SUM(CASE WHEN invoices.status IN ('sent', 'overdue') THEN invoices.amount ELSE 0 END), 0) AS outstanding,
            COALESCE(SUM(CASE WHEN invoices.status = 'paid' THEN invoices.amount ELSE 0 END), 0) AS paid
        FROM clients
        LEFT JOIN invoices ON invoices.client_id = clients.id
        GROUP BY clients.id
        ORDER BY clients.name
        """
    ).fetchall()
    monthly_recurring = db.execute(
        "SELECT COALESCE(SUM(monthly_subscription), 0) AS total FROM clients"
    ).fetchone()["total"]
    db.close()
    return render_template("clients.html", clients=clients, monthly_recurring=monthly_recurring)


@app.route("/clients/add", methods=["GET", "POST"])
@login_required
def add_client():
    db = get_db()
    error = None
    if request.method == "POST":
        client_id = request.form["client_id"].strip()
        if not re.match(r"^\d{4}$", client_id):
            error = "Client ID must be exactly 4 digits (e.g. 1190)."
        else:
            try:
                db.execute(
                    "INSERT INTO clients (name, client_id, monthly_subscription, email, notes) VALUES (?, ?, ?, ?, ?)",
                    (
                        request.form["name"].strip(),
                        client_id,
                        parse_subscription(request.form),
                        request.form.get("email", "").strip(),
                        request.form.get("notes", "").strip(),
                    ),
                )
                db.commit()
                db.close()
                return redirect(url_for("clients_page"))
            except sqlite3.IntegrityError:
                error = f"Client ID {client_id} or that name is already in use."
    db.close()
    return render_template("client_form.html", error=error, form=request.form, client=None)


@app.route("/clients/<int:client_row_id>/edit", methods=["GET", "POST"])
@login_required
def edit_client(client_row_id):
    db = get_db()
    error = None
    if request.method == "POST":
        try:
            db.execute(
                "UPDATE clients SET name = ?, monthly_subscription = ?, email = ?, notes = ? WHERE id = ?",
                (
                    request.form["name"].strip(),
                    parse_subscription(request.form),
                    request.form.get("email", "").strip(),
                    request.form.get("notes", "").strip(),
                    client_row_id,
                ),
            )
            db.commit()
            db.close()
            return redirect(url_for("clients_page"))
        except sqlite3.IntegrityError:
            error = "That name is already in use by another client."

    client = db.execute("SELECT * FROM clients WHERE id = ?", (client_row_id,)).fetchone()
    db.close()
    return render_template("client_form.html", error=error, form=client, client=client)


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5050)
