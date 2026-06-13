import re
from utils.schema import Invoice, Item, TaxLine
from mapper.base import BaseMapper


class PDFMapper(BaseMapper):
    format_name = "PDF"

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
        invoice_no = search(r"Invoice\s*(?:Number|No)\s*[:\- ]+\s*([A-Z0-9_\-]+)")
        issue_date = search(r"Date\s*[:\- ]+\s*([\d\-\/]+)")
        supplier_name = search(r"Vendor\s*[:\- ]+\s*([^\n]+)")
        buyer_name = search(r"Customer\s*[:\- ]+\s*([^\n]+)")

        subtotal = search_float(r"Subtotal\s*[:\- ]+\s*([\d\.,]+)")
        tax_total = search_float(r"(?:GST|Tax)[^:]*:\s*([\d\.,]+)")
        grand_total = search_float(r"(?:Total|Grand\s*Total)\s*[:\- ]+\s*([\d\.,]+)")

        # Parse items
        items = []
        for line in text.splitlines():
            m_item = re.search(r"Item\s*\d+:\s*(.*?)\|\s*Qty:\s*([\d\.,]+)\s*\|\s*Price:\s*([\d\.,]+)", line, re.IGNORECASE)
            if m_item:
                desc = m_item.group(1).strip()
                try:
                    qty = float(re.sub(r"[^\d\.]", "", m_item.group(2)))
                    price = float(re.sub(r"[^\d\.]", "", m_item.group(3)))
                except:
                    qty = 0.0
                    price = 0.0
                items.append(Item(
                    description=desc,
                    quantity=qty,
                    unit_price=price,
                    line_total=qty * price
                ))
            else:
                m_item_fb = re.search(r"Item\s*\d+:\s*(.*?)\|\s*Qty:\s*([\d\.,]+)", line, re.IGNORECASE)
                if m_item_fb:
                    desc = m_item_fb.group(1).strip()
                    try:
                        qty = float(re.sub(r"[^\d\.]", "", m_item_fb.group(2)))
                    except:
                        qty = 0.0
                    items.append(Item(
                        description=desc,
                        quantity=qty,
                        unit_price=0.0,
                        line_total=0.0
                    ))

        # Tax Lines
        tax_lines = []
        if tax_total > 0:
            tax_rate = search_float(r"(?:GST|Tax)\s*\((\d+)%\)") or 0.0
            tax_lines.append(TaxLine(
                tax_category="GST" if "GST" in text else "Tax",
                tax_rate=tax_rate,
                tax_amount=tax_total
            ))

        return Invoice(
            invoice_no=invoice_no,
            invoice_type="PDF",
            issue_date=issue_date,
            due_date=None,

            supplier={"name": supplier_name, "vat_id": None, "country": None},
            buyer={"name": buyer_name, "vat_id": None, "country": None},

            currency="EUR",

            subtotal=subtotal,
            tax_total=tax_total,
            grand_total=grand_total,

            items=items,
            tax_lines=tax_lines,

            source_type="pdf",
            invoice_standard="UNKNOWN"
        )