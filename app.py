import os
import tempfile
import streamlit as st

from core.pipeline import process_document
from main import dispatcher as parser_dispatcher, mapper_dispatcher
from core.validator import InvoiceValidator

st.title("Invoice Automation MVP")

uploaded = st.file_uploader(
    "Upload Invoice",
    type=["pdf", "xml", "jpg", "jpeg", "png"]
)

validator = InvoiceValidator()

result = None 

if uploaded:

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=os.path.splitext(uploaded.name)[1]
    ) as tmp:

        tmp.write(uploaded.getbuffer())
        file_path = tmp.name

    try:
        result = process_document(
            file_path=file_path,
            parser_dispatcher=parser_dispatcher,
            mapper_dispatcher=mapper_dispatcher,
            validator=validator
        )

        st.subheader("Processing Result")
        st.json(result)

    except Exception as e:
        st.error(str(e))

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

if result is not None:

    st.subheader("Invoice")
    st.json(result.get("invoice", {}))

    st.subheader("Validation")
    st.json({
        "status": result.get("status"),
        "flags": result.get("flags", [])
    })