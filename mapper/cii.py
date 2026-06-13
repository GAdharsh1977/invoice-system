from mapper.base import BaseMapper
from utils.schema import Invoice, Item
import xml.etree.ElementTree as ET


class CIIMapper(BaseMapper):
    format_name = "CII"

    def map(self, parsed: dict) -> Invoice:
        root: ET.Element = parsed["raw"]

        def find(path):
            el = root.find(path)
            return el.text.strip() if el is not None and el.text else None

        def ffloat(x):
            try:
                return float(x or 0)
            except:
                return 0.0

        items = []

        for line in root.findall(".//{*}IncludedSupplyChainTradeLineItem"):
            desc = line.findtext(".//{*}SpecifiedTradeProduct//{*}Name")
            qty = line.findtext(".//{*}BasisQuantity") or line.findtext(".//{*}BilledQuantity")
            price = line.findtext(".//{*}NetPriceProductTradePrice//{*}ChargeAmount")
            total = line.findtext(".//{*}LineTotalAmount")

            qty_val = ffloat(qty)
            price_val = ffloat(price)
            total_val = ffloat(total) if total else (qty_val * price_val)

            items.append(Item(
                description=desc or "Unknown",
                quantity=qty_val,
                unit_price=price_val,
                line_total=total_val
            ))

        supplier_name = find(".//{*}SellerTradeParty//{*}Name")
        buyer_name = find(".//{*}BuyerTradeParty//{*}Name")

        supplier_id = find(".//{*}SellerTradeParty//{*}ID")
        buyer_id = find(".//{*}BuyerTradeParty//{*}ID")

        grand_total = ffloat(find(".//{*}GrandTotalAmount"))
        tax_total = ffloat(find(".//{*}TaxTotalAmount"))

        calculated_subtotal = sum(item.line_total for item in items)
        if grand_total == 0.0:
            grand_total = calculated_subtotal

        return Invoice(
            invoice_no=find(".//{*}ExchangedDocument//{*}ID"),
            invoice_type="CII",

            issue_date=find(".//{*}IssueDateTime//{*}DateTimeString"),
            due_date=None,

            supplier={
                "name": supplier_name,
                "vat_id": supplier_id,
                "country": find(".//{*}SellerTradeParty//{*}PostalTradeAddress//{*}CountryID")
            },

            buyer={
                "name": buyer_name,
                "vat_id": buyer_id,
                "country": find(".//{*}BuyerTradeParty//{*}PostalTradeAddress//{*}CountryID")
            },

            currency=find(".//{*}InvoiceCurrencyCode") or "EUR",

            subtotal=calculated_subtotal,
            tax_total=tax_total,
            grand_total=grand_total,

            items=items,

            source_type="xml",
            invoice_standard="CII"
        )