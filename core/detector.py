import os

def extract_format(file_path: str):
    ext = os.path.splitext(file_path)[1].lower()
    if(ext == ".xml"):
        return "xml"
    elif(ext == ".pdf"):
        return "pdf"
    elif(ext in [".jpg", ".jpeg", ".png"]):
        return "image"
    else:
        return "unknown"