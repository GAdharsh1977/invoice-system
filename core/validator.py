def validate(invoice):
    flags = []

    if not invoice.get("invoice_no"):
        flags.append("Missing invoice number")
    if not invoice.get("vendor"):
        flags.append("Missing vendor name")
    if invoice.get("total", 0) < 0:
        flags.append("Total amount must be greater than zero")
    status = "APPROVED"
    if flags:
        status = "FLAGGED"
    return {
        "status": status,
        "flags": flags
    }