import os
import tempfile
import streamlit as st
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    ServiceContext,
    StorageContext,
    load_index_from_storage,
)
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.llms.openai import OpenAI
import hashlib


def get_file_hash(file):
    return hashlib.md5(file.read()).hexdigest()

def process_pdf(uploaded_file):
    file_hash = get_file_hash(uploaded_file)
    cache_dir = f"./cache/{file_hash}"

    if os.path.exists(cache_dir):
        # Load from cache if it exists
        storage_context = StorageContext.from_defaults(persist_dir=cache_dir)
        index = load_index_from_storage(storage_context)
    else:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(temp_file_path, "wb") as temp_file:
                uploaded_file.seek(0)
                temp_file.write(uploaded_file.read())
            
            documents = SimpleDirectoryReader(temp_dir).load_data()
            
            # Use a smaller chunk size for large documents
            node_parser = SimpleNodeParser.from_defaults(chunk_size=512, chunk_overlap=50)
            
            service_context = ServiceContext.from_defaults(
                llm=OpenAI(model="gpt-3.5-turbo", temperature=0),
                node_parser=node_parser,
            )
            
            index = VectorStoreIndex.from_documents(
                documents,
                service_context=service_context,
            )
            
            # Cache the processed index
            index.storage_context.persist(persist_dir=cache_dir)

    return index.as_query_engine(similarity_top_k=5)

st.title("Chat with your PDF")

if "query_engine" not in st.session_state:
    st.session_state.query_engine = None

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file:
    with st.spinner("Processing PDF... This may take a while for large files."):
        st.session_state.query_engine = process_pdf(uploaded_file)
    st.success("PDF processed successfully!")

if st.session_state.query_engine:
    user_question = st.text_input("Ask a question about your PDF:")
    if user_question:
        with st.spinner("Generating response..."):
            response = st.session_state.query_engine.query(user_question)
            st.write(response.response)
else:
    st.info("Please upload a PDF file to get started.")