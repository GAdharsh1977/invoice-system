import os
import xml.etree.ElementTree as ET
from zipfile import ZipFile
import pypdf

def detect_xml_format(root):
    tag = root.tag
    if "Invoice-2" in tag:
        return "UBL"
    if "CrossIndustryInvoice" in tag:
        return "CII"
    return "Unknown"

def detect_xml_file(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    return detect_xml_format(root)

def detect_zugferd_from_pdf(file_path):
    try:
        reader = pypdf.PdfReader(file_path)
        if "/Names" in reader.trailer["/Root"]:
            names = reader.trailer["/Root"]["/Names"]
            if "/EmbeddedFiles" in names:
                embedded_files = names["/EmbeddedFiles"]["/Names"]
                for i in range(0, len(embedded_files), 2):
                    file_spec = embedded_files[i + 1]
                    ef = file_spec["/EF"]["/F"].get_data()
                    try:
                        root = ET.fromstring(ef)
                        return detect_xml_format(root)
                    except:
                        continue
        return None 
    except Exception as e:
        print(f"Error occurred while processing PDF file: {e}")
        return None

def detect_pdf_format(file_path):
    zugferd = detect_zugferd_from_pdf(file_path)
    if zugferd:
        return f"ZUGFeRD ({zugferd})"
    
    return "PDF (non-ZUGFeRD)"

def detect_document(file_path: str):
    
    ext = os.path.splitext(file_path)[1].lower()

    if(ext == ".xml"):
        return {
            "container": "xml",
            "standard": detect_xml_file(file_path)
        }
    
    elif(ext == ".pdf"):
        return {
            "container": "pdf",
            "standard": detect_pdf_format(file_path)
        }
    
    elif(ext in [".jpg", ".jpeg", ".png"]):
        return {
            "container": "image",
            "standard": None
        }
    
    else:
        return {
            "container": "unknown",
            "standard": None
        }