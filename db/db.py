import sqlite3

conn = sqlite3.connect('invoice.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""Create table if not exists invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_no TEXT,
    vendor TEXT,
    total REAL,
    currency TEXT,
    status TEXT
)""")
conn.commit()

def save_invoice(invoice, status):
    cursor.execute(
        """
        INSERT INTO invoices
        (
            invoice_no,
            vendor,
            total,
            currency,
            status
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            invoice["invoice_no"],
            invoice["vendor"],
            invoice["total"],
            invoice["currency"],
            status
        )
    )

    conn.commit()

def get_invoices():
    cursor.execute("SELECT * FROM invoices")
    return cursor.fetchall()