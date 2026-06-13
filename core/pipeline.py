import os
from core.detector import detect_document
from db.db import save_invoice

def process_document(
    file_path,
    parser_dispatcher,
    mapper_dispatcher,
    validator
):

    detected = detect_document(file_path)

    std = detected["standard"]
    container = detected["container"]

    # Normalize format hint to match registered parsers
    if container == "pdf":
        if std and std.startswith("ZUGFeRD"):
            format_hint = "UBL" if "UBL" in std else "CII"
        else:
            format_hint = "PDF"
    elif container == "xml":
        if std == "UBL":
            format_hint = "UBL"
        elif std == "CII":
            format_hint = "CII"
        else:
            format_hint = "XML"
    elif container == "image":
        format_hint = "IMAGE"
    else:
        format_hint = (container or "").upper()

    parser = parser_dispatcher.get(format_hint)

    # For ZUGFeRD PDF, extract the embedded XML and parse that
    temp_xml_path = None
    parse_path = file_path
    if container == "pdf" and std and "ZUGFeRD" in std:
        import tempfile
        import pypdf
        try:
            reader = pypdf.PdfReader(file_path)
            names = reader.trailer["/Root"]["/Names"]
            embedded_files = names["/EmbeddedFiles"]["/Names"]
            for i in range(0, len(embedded_files), 2):
                file_spec = embedded_files[i + 1]
                ef = file_spec["/EF"]["/F"].get_data()
                with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as tmp_file:
                    tmp_file.write(ef)
                    temp_xml_path = tmp_file.name
                parse_path = temp_xml_path
                break
        except Exception as e:
            print(f"Failed to extract ZUGFeRD XML: {e}")

    try:
        parsed = parser.parse(parse_path)
    finally:
        if temp_xml_path and os.path.exists(temp_xml_path):
            try:
                os.remove(temp_xml_path)
            except:
                pass

    mapper = mapper_dispatcher.get(
        parsed["format_hint"]
    )

    invoice = mapper.map(parsed)

    validation = validator.validate(invoice)

    save_invoice(
        invoice,
        validation["status"]
    )

    print(f"[DETECT] {format_hint}")
    print(f"[PARSE] {parser.__class__.__name__}")
    print(f"[MAP] {mapper.__class__.__name__}")
    print(f"[VALIDATE] {validation['status']}")

    return {
        "status": validation["status"],
        "flags": validation["flags"],
        "invoice": invoice.model_dump()
    }