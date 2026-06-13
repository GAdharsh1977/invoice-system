import xml.etree.ElementTree as ET
from parsers.parser import BaseParser

class UBLParser(BaseParser):
    format_name = "UBL"

    def parse(self, file_path):
        tree = ET.parse(file_path)
        root = tree.getroot()

        return {
            "format_hint": "UBL",
            "raw": root,
            "normalized": {
                "invoice_no": root.findtext(".//InvoiceID"),
                "invoice_date": root.findtext(".//IssueDate"),
            }
        }