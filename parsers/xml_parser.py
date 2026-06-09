import xml.etree.ElementTree as ET

def to_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0
    
def parse_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    return {
        "invoice_no": root.findtext("InvoiceNumber"),
        "date": root.findtext("Date"),
        "vendor": root.findtext("VendorName"),
        "total": to_float(root.findtext("Total")),
        "currency": root.findtext("Currency") or "INR",
        "items": [
            {
                "name": item.findtext("Name"),
                "price": to_float(item.findtext("Price")),
                "qty": to_float(item.findtext("Quantity"))
            }
            for item in root.findall("Items/Item")
        ],
        "source_type": "xml"
    }