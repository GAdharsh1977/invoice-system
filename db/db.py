import sqlite3
import json
import hashlib

from utils.schema import Invoice

conn = sqlite3.connect("invoice.db", check_same_thread=False)
cursor = conn.cursor()

# Initialize Database Schema if not exists
cursor.execute("""
    CREATE TABLE IF NOT EXISTS invoices (
        invoice_id INTEGER PRIMARY KEY AUTOINCREMENT,
        uuid TEXT UNIQUE,
        invoice_no TEXT,
        invoice_type TEXT,
        invoice_standard TEXT,
        source_type TEXT,
        issue_date TEXT,
        due_date TEXT,
        currency TEXT,
        subtotal REAL,
        tax_total REAL,
        grand_total REAL,
        status TEXT,
        source_hash TEXT UNIQUE
    )
""")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS invoice_parties (
        party_id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_id INTEGER,
        role TEXT,
        name TEXT,
        vat_id TEXT,
        country TEXT,
        address TEXT,
        city TEXT,
        postal_code TEXT,
        FOREIGN KEY(invoice_id) REFERENCES invoices(invoice_id)
    )
""")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS invoice_items (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_id INTEGER,
        description TEXT,
        quantity REAL,
        unit_price REAL,
        line_total REAL,
        unit TEXT,
        tax_rate REAL,
        discount REAL,
        sku TEXT,
        FOREIGN KEY(invoice_id) REFERENCES invoices(invoice_id)
    )
""")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS invoice_taxes (
        tax_id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_id INTEGER,
        tax_category TEXT,
        tax_rate REAL,
        tax_amount REAL,
        FOREIGN KEY(invoice_id) REFERENCES invoices(invoice_id)
    )
""")
conn.commit()

def generate_hash(data: dict) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

def save_invoice(invoice: Invoice, status="processed"):
    data = invoice.model_dump()

    source_hash = generate_hash(data)

    # Check if this exact invoice content already exists in the database
    cursor.execute("SELECT invoice_id FROM invoices WHERE source_hash = ?", (source_hash,))
    row = cursor.fetchone()
    if row:
        invoice_id = row[0]
        # Update the status (e.g., to FLAGGED now that it is uploaded twice)
        cursor.execute("UPDATE invoices SET status = ? WHERE invoice_id = ?", (status, invoice_id))
        conn.commit()
        return invoice_id

    try:
        cursor.execute("""
            INSERT INTO invoices (
                uuid,
                invoice_no,
                invoice_type,
                invoice_standard,
                source_type,
                issue_date,
                due_date,
                currency,
                subtotal,
                tax_total,
                grand_total,
                status,
                source_hash
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            source_hash,
            data.get("invoice_no"),
            data.get("invoice_type"),
            data.get("invoice_standard"),
            data.get("source_type"),
            data.get("issue_date"),
            data.get("due_date"),
            data.get("currency"),
            data.get("subtotal"),
            data.get("tax_total"),
            data.get("grand_total"),
            status,
            source_hash
        ))

        invoice_id = cursor.lastrowid

        # PARTIES
        for role in ["supplier", "buyer"]:
            party = data.get(role, {})

            cursor.execute("""
                INSERT INTO invoice_parties (
                    invoice_id,
                    role,
                    name,
                    vat_id,
                    country,
                    address,
                    city,
                    postal_code
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                invoice_id,
                role,
                party.get("name"),
                party.get("vat_id"),
                party.get("country"),
                None,
                None,
                None
            ))

        # ITEMS
        for item in data.get("items", []):
            cursor.execute("""
                INSERT INTO invoice_items (
                    invoice_id,
                    description,
                    quantity,
                    unit_price,
                    line_total,
                    unit,
                    tax_rate,
                    discount,
                    sku
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                invoice_id,
                item.get("description"),
                item.get("quantity"),
                item.get("unit_price"),
                item.get("line_total"),
                item.get("unit"),
                item.get("tax_rate"),
                item.get("discount"),
                item.get("sku")
            ))

        # TAXES
        for tax in data.get("tax_lines", []):
            cursor.execute("""
                INSERT INTO invoice_taxes (
                    invoice_id,
                    tax_category,
                    tax_rate,
                    tax_amount
                )
                VALUES (?, ?, ?, ?)
            """, (
                invoice_id,
                tax.get("tax_category"),
                tax.get("tax_rate"),
                tax.get("tax_amount")
            ))

        conn.commit()
        return invoice_id

    except Exception as e:
        conn.rollback()
        raise e

def get_invoices():
    cursor.execute("SELECT * FROM invoices")
    return cursor.fetchall()