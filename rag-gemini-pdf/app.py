import streamlit as st
import tempfile
import os
from utils.document_loader import load_unstructured_file, chunk_text
from utils.qdrant_client import create_or_get_collection, upload_chunks_to_qdrant, search_similar_chunks
from utils.gemini_llm import embed_fn, generate_answer

#st.title("📄 Document-based Q&A (PDF, DOCX, PPTX Only)")
#st.markdown("Upload your **unstructured document**, ask any question related to its content.")

# Initialize session state for document tracking
if 'current_document_id' not in st.session_state:
    st.session_state.current_document_id = None
if 'uploaded_documents' not in st.session_state:
    st.session_state.uploaded_documents = []

# Check if file was uploaded from main app, otherwise show file uploader
if 'uploaded_file_path' in st.session_state:
    file_path = st.session_state.uploaded_file_path
    #st.success(f"Processing document: {st.session_state.uploaded_file_name}")
else:
    uploaded_file = st.file_uploader("Upload DOCX / PDF / PPTX", type=["pdf", "docx", "pptx"])
    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[-1]) as tmp_file:
            tmp_file.write(uploaded_file.read())
            file_path = tmp_file.name
        st.success("Document uploaded successfully.")
    else:
        file_path = None

if file_path:
    
    # Get document name
    if 'uploaded_file_name' in st.session_state:
        doc_name = st.session_state.uploaded_file_name
    else:
        doc_name = f"Document_{len(st.session_state.uploaded_documents) + 1}"
    
    # Check if document with same name already exists
    existing_doc = next((doc for doc in st.session_state.uploaded_documents if doc['name'] == doc_name), None)
    
    if existing_doc:
        st.warning(f"📄 Document '{doc_name}' already exists in the knowledge base. Skipping upload.")
        st.session_state.current_document_id = existing_doc['id']
        st.info("Using existing document for queries.")
    else:
        # Step 1: Extract and chunk
        full_text = load_unstructured_file(file_path)
        chunks = chunk_text(full_text)

        # Step 2: Qdrant upload (do NOT clear previous document data)
        create_or_get_collection(clear_existing=False)
        document_id = upload_chunks_to_qdrant(chunks, embed_fn)
        
        # Store current document ID and add to document list
        st.session_state.current_document_id = document_id
        
        # Add to uploaded documents list
        st.session_state.uploaded_documents.append({
            'id': document_id,
            'name': doc_name
        })

        st.success(f"📄 Document '{doc_name}' processed and added to knowledge base!")
    
    # Show all uploaded documents
    if st.session_state.uploaded_documents:
        #st.info(f"📚 Knowledge base now contains {len(st.session_state.uploaded_documents)} document(s):")
        for doc in st.session_state.uploaded_documents:
            st.write(f"  • {doc['name']}")

# Query interface
st.subheader("🔍 Ask Questions")
query = st.text_input("Ask a question based on your uploaded documents:")

if query:
    if not st.session_state.uploaded_documents:
        st.warning("Please upload a document first!")
    else:
        with st.spinner("Searching across your documents..."):
            # Search only in the current document
            matched_chunks = search_similar_chunks(
                query, 
                embed_fn, 
                document_id=st.session_state.current_document_id  # Search current document only
            )
            response = generate_answer(matched_chunks, query)
            
        st.subheader("📌 Answer")
        st.write(response)
        
        # Show which document was searched
        current_doc_name = next(
            (doc['name'] for doc in st.session_state.uploaded_documents 
             if doc['id'] == st.session_state.current_document_id), 
            "current document"
        )
        st.caption(f"🔍 Searched in: '{current_doc_name}'")
