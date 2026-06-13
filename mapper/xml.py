from utils.schema import Invoice, Item, TaxLine
from mapper.base import BaseMapper
import xml.etree.ElementTree as ET


class XMLMapper(BaseMapper):
    format_name = "XML"

    def map(self, parsed: dict) -> Invoice:
        root: ET.Element = parsed["raw"]

        def find_any(paths, default=None, node=root):
            for path in paths:
                val = node.findtext(path)
                if val:
                    return val.strip()
            return default

        # Extract Fields
        invoice_no = find_any([".//ID", ".//InvoiceNumber", ".//InvoiceNo"])
        issue_date = find_any([".//IssueDate", ".//Date", ".//InvoiceDate"])
        currency = find_any([".//DocumentCurrencyCode", ".//Currency"], "EUR")
        grand_total = float(find_any([".//PayableAmount", ".//Total", ".//GrandTotal"], "0.0"))

        supplier_name = find_any([
            ".//AccountingSupplierParty//Party//PartyName//Name",
            ".//VendorName",
            ".//SupplierName"
        ])
        buyer_name = find_any([
            ".//AccountingCustomerParty//Party//PartyName//Name",
            ".//BuyerName",
            ".//CustomerName"
        ])

        # Parse items
        items = []
        item_nodes = root.findall(".//Item") or root.findall(".//InvoiceLine") or root.findall(".//LineItem")
        for node in item_nodes:
            desc = find_any([".//Name", ".//Description", ".//ItemName"], "Unknown", node)
            qty_str = find_any([".//Quantity", ".//InvoicedQuantity", ".//Qty"], "0.0", node)
            price_str = find_any([".//Price", ".//PriceAmount", ".//UnitPrice"], "0.0", node)

            try:
                qty = float(qty_str)
                price = float(price_str)
            except:
                qty = 0.0
                price = 0.0

            items.append(Item(
                description=desc,
                quantity=qty,
                unit_price=price,
                line_total=qty * price
            ))

        subtotal = sum(item.line_total for item in items)
        if grand_total == 0.0:
            grand_total = subtotal

        return Invoice(
            invoice_no=invoice_no,
            invoice_type="XML",
            issue_date=issue_date,
            due_date=None,

            supplier={"name": supplier_name, "vat_id": None, "country": None},
            buyer={"name": buyer_name, "vat_id": None, "country": None},

            currency=currency,

            subtotal=subtotal,
            tax_total=grand_total - subtotal,
            grand_total=grand_total,

            items=items,
            tax_lines=[],

            source_type="xml",
            invoice_standard="UNKNOWN"
        )