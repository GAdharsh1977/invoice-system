import streamlit as st

from parsers.pdf_parser import parse_pdf
from core.mapper import map_pdf_to_invoice
from core.validator import validate
from db.db import save_invoice

st.title("Invoice Automation MVP")

uploaded = st.file_uploader(
    "Upload Invoice",
    type=["pdf", "xml", "jpg", "jpeg", "png"]
)

if uploaded:

    file_path = uploaded.name

    with open(file_path, "wb") as f:
        f.write(uploaded.getbuffer())

    pdf_data = parse_pdf(file_path)

    invoice = map_pdf_to_invoice(pdf_data)

    validation = validate(invoice)

    save_invoice(
        invoice,
        validation["status"]
    )

    st.subheader("Extracted Invoice")

    st.json(invoice)

    st.subheader("Validation")

    st.json(validation)