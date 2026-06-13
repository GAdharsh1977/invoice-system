from pypdf import PdfReader
from parsers.parser import BaseParser

class PDFParser(BaseParser):
    format_name = "PDF"

    def parse(self, file_path):
        reader = PdfReader(file_path)

        text = "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        )

        return {
            "format_hint": "PDF",
            "raw": text,
            "normalized": {
                "text": text
            }
        }