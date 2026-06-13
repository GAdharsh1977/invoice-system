import sqlite3
from utils.schema import Invoice


class InvoiceValidator:

    def validate(self, invoice: Invoice):

        flags = []

        if not invoice.invoice_no:
            flags.append("Missing invoice number")

        if not invoice.issue_date:
            flags.append("Missing issue date")

        if not invoice.currency:
            flags.append("Missing currency")

        if not invoice.supplier.name:
            flags.append("Missing supplier")

        if not invoice.buyer.name:
            flags.append("Missing buyer")

        if invoice.grand_total <= 0:
            flags.append("Invalid grand total")

        if invoice.subtotal < 0:
            flags.append("Invalid subtotal")

        if invoice.tax_total < 0:
            flags.append("Invalid tax total")

        if not invoice.items:
            flags.append("No line items found")

        else:

            calculated_subtotal = sum(
                item.line_total
                for item in invoice.items
            )

            if abs(calculated_subtotal - invoice.subtotal) > 0.01:
                flags.append(
                    f"Subtotal mismatch "
                    f"(Calculated: {calculated_subtotal}, "
                    f"Invoice: {invoice.subtotal})"
                )

        try:

            conn = sqlite3.connect("invoice.db")
            cursor = conn.cursor()

            #duplicate check by hashing.
            import hashlib
            import json
            data = invoice.model_dump()
            source_hash = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM invoices
                WHERE source_hash = ?
                """,
                (source_hash,)
            )
            hash_count = cursor.fetchone()[0]
            if hash_count > 0:
                flags.append("Duplicate invoice content detected (exact match)")

            #check invoice number (only if different content)
            if invoice.invoice_no:
                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM invoices
                    WHERE invoice_no = ? AND source_hash != ?
                    """,
                    (invoice.invoice_no, source_hash)
                )
                count = cursor.fetchone()[0]
                if count > 0:
                    flags.append("Duplicate invoice number detected")

            conn.close()

        except Exception as e:

            flags.append(
                f"Database validation error: {str(e)}"
            )

        return {
            "status": "APPROVED" if not flags else "FLAGGED",
            "flags": flags
        }