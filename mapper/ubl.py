import xml.etree.ElementTree as ET
from mapper.base import BaseMapper
from utils.schema import Invoice, Item


class UBLMapper(BaseMapper):
    format_name = "UBL"

    def map(self, parsed: dict) -> Invoice:
        root: ET.Element = parsed["raw"]

        def find(path):
            el = root.find(path)
            return el.text.strip() if el is not None and el.text else None

        def find_float(path):
            try:
                return float(find(path) or 0)
            except:
                return 0.0

        items = []
        for line in root.findall(".//{*}InvoiceLine"):
            desc = line.findtext(".//{*}Item//{*}Name")
            qty = line.findtext(".//{*}InvoicedQuantity")
            price = line.findtext(".//{*}Price//{*}PriceAmount")
            total = line.findtext(".//{*}LineExtensionAmount")

            items.append(Item(
                description=desc or "Unknown",
                quantity=float(qty or 0),
                unit_price=float(price or 0),
                line_total=float(total or 0)
            ))

        supplier_name = find(".//{*}AccountingSupplierParty//{*}Party//{*}PartyName//{*}Name")
        buyer_name = find(".//{*}AccountingCustomerParty//{*}Party//{*}PartyName//{*}Name")

        supplier_vat = find(".//{*}AccountingSupplierParty//{*}Party//{*}PartyTaxScheme//{*}CompanyID")
        buyer_vat = find(".//{*}AccountingCustomerParty//{*}Party//{*}PartyTaxScheme//{*}CompanyID")

        subtotal = find_float(".//{*}LegalMonetaryTotal//{*}LineExtensionAmount")
        tax_total = find_float(".//{*}TaxTotal//{*}TaxAmount")
        grand_total = find_float(".//{*}LegalMonetaryTotal//{*}PayableAmount")

        calculated_subtotal = sum(item.line_total for item in items)
        if subtotal == 0.0:
            subtotal = calculated_subtotal
        if grand_total == 0.0:
            grand_total = subtotal

        return Invoice(
            invoice_no=find("{*}ID"),
            invoice_type="UBL",

            issue_date=find("{*}IssueDate"),
            due_date=find("{*}DueDate"),

            supplier={
                "name": supplier_name,
                "vat_id": supplier_vat,
                "country": find(".//{*}AccountingSupplierParty//{*}Party//{*}PostalAddress//{*}Country//{*}IdentificationCode")
            },

            buyer={
                "name": buyer_name,
                "vat_id": buyer_vat,
                "country": find(".//{*}AccountingCustomerParty//{*}Party//{*}PostalAddress//{*}Country//{*}IdentificationCode")
            },

            currency=find(".//{*}DocumentCurrencyCode") or "EUR",

            subtotal=subtotal,
            tax_total=tax_total,
            grand_total=grand_total,

            items=items,

            source_type="xml",
            invoice_standard="UBL"
        )