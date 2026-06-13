import re
from utils.schema import Invoice, Item, TaxLine
from mapper.base import BaseMapper


class ImageMapper(BaseMapper):
    format_name = "IMAGE"

    def map(self, parsed: dict) -> Invoice:
        text = parsed.get("normalized", {}).get("text", "")

        def search(pattern):
            m = re.search(pattern, text, re.IGNORECASE)
            return m.group(1).strip() if m else None

        def search_float(pattern):
            val = search(pattern)
            if val:
                cleaned = re.sub(r"[^\d\.]", "", val)
                try:
                    return float(cleaned)
                except:
                    return 0.0
            return 0.0

        # Extract Fields
        matches = re.findall(r"\b(INV[A-Z0-9\-O_]+)\b", text, re.IGNORECASE)
        invoice_no = None
        for m in matches:
            if m.upper() not in ["INVOICE", "INVOICES"]:
                invoice_no = m
                break

        issue_date = search(r"Invoice\s*Date\s*:\s*([^\n]+)")
        currency = search(r"Currency\s*:\s*(\w+)") or "EUR"

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        supplier_name = lines[0] if lines else None

        buyer_name = search(r"Bill\s*To\s*:\s*(?:Ship\s*To\s*:\s*)?([^\n]+)")
        if buyer_name:

            half_len = len(buyer_name) // 2
            first_half = buyer_name[:half_len].strip()
            second_half = buyer_name[half_len:].strip()
            if first_half == second_half:
                buyer_name = first_half

        subtotal = search_float(r"Subtotal\s+(?:INR\s*)?([\d\.,]+)")
        grand_total = search_float(r"Total\s+(?:INR\s*)?([\d\.,]+)")

        return Invoice(
            invoice_no=invoice_no,
            invoice_type="IMAGE",
            issue_date=issue_date,
            due_date=None,

            supplier={"name": supplier_name, "vat_id": None, "country": None},
            buyer={"name": buyer_name, "vat_id": None, "country": None},

            currency=currency,

            subtotal=subtotal,
            tax_total=grand_total - subtotal,
            grand_total=grand_total,

            items=[],
            tax_lines=[],

            source_type="image",
            invoice_standard="UNKNOWN"
        )