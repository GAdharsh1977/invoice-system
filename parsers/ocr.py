import pytesseract
from PIL import Image
from parsers.parser import BaseParser

pytesseract.pytesseract.tesseract_cmd = (
    r"C:/Program Files/Tesseract-OCR/tesseract.exe"
)

class OCRParser(BaseParser):
    format_name = "IMAGE"

    def parse(self, file_path: str) -> dict:
        try:
            img = Image.open(file_path)
            text = pytesseract.image_to_string(img)
        except Exception as e:
            text = f"[OCR Failed] {str(e)}"

        return {
            "format_hint": "IMAGE",
            "raw": text,
            "normalized": {
                "text": text
            }
        }
