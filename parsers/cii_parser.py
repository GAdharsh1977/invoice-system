import xml.etree.ElementTree as ET
from parsers.parser import BaseParser

class CIIParser(BaseParser):
    format_name = "CII"

    def parse(self, file_path):
        tree = ET.parse(file_path)
        root = tree.getroot()

        return {
            "format_hint": "CII",
            "raw": root,
            "normalized": {
                "invoice_no": root.findtext(".//ExchangedDocument//ID"),
                "currency": root.findtext(".//InvoiceCurrencyCode"),
            }
        }