import re

def map_pdf_to_invoice(pdf_data):
    text = pdf_data.get("raw_text")
    invoice_no = None
    vendor = None
    total = None

    invoice_match = re.search(r"INV-\d{4}-\d+", text, re.IGNORECASE)
    invoice_no = invoice_match.group(0) if invoice_match else None

    vendor_match = re.search(r"Vendor\s*:\s*(.*?)\s*Customer", text, re.IGNORECASE | re.DOTALL)

    vendor = vendor_match.group(1).strip() if vendor_match else None

    total_match = re.search(r"Total\s*[:\s]*([\d,.]+)", text, re.IGNORECASE)
    if total_match:
        total = float(total_match.group(1).replace(",", ""))

    return {
        "invoice_no": invoice_no,
        "vendor": vendor,
        "total": total,
        "currency": "INR",
        "items": [],
        "source_type": "pdf"
    }
