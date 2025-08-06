import streamlit as st
import os
import tempfile
import sys

# Add paths to both sub-apps
sys.path.append("rag-gemini-pdf")
sys.path.append("rag-structured-data")

# Title and UI
st.set_page_config(page_title="Unified Document QA")
st.title("📁 Unified Document Query Assistant")
st.markdown("Upload any document (PDF, DOCX, PPTX, CSV, XLSX). The system will automatically choose the correct pipeline.")

# File upload
uploaded_file = st.file_uploader("Upload a file", type=["pdf", "docx", "pptx", "csv", "xlsx"])

if uploaded_file:
    file_ext = os.path.splitext(uploaded_file.name)[-1].lower()
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    #st.success(f"Uploaded: {uploaded_file.name}")

    # Store the file path in session state so sub-apps can access it
    st.session_state.uploaded_file_path = tmp_path
    st.session_state.uploaded_file_name = uploaded_file.name

    # Determine and route based on file type
    if file_ext in [".pdf", ".docx", ".pptx"]:
        #st.subheader("🔎 Running Unstructured Document QA")
        # Execute the unstructured document QA app with the uploaded file
        exec(open("rag-gemini-pdf/app.py", encoding='utf-8').read(), globals())

    elif file_ext in [".csv", ".xlsx"]:
        #st.subheader("🧠 Running Structured Data QA")
        # Execute the structured data QA app with the uploaded file
        exec(open("rag-structured-data/app.py", encoding='utf-8').read(), globals())

    else:
        st.error("Unsupported file type.")
