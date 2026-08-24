import os
import streamlit as st
from pypdf import PdfReader
# from groq import Groq
from dotenv import load_dotenv
import ollama
import re

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.documents import Document

load_dotenv()

# --- PDF Extraction ---
def extract_pdf_text(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        content = page.extract_text()
        if content:
            text += content + "\n"
    return text

# --- RAG Setup: Indexing & Retrieval ---
def build_vector_store(text: str):
    """Chunk the resume text and create an in-memory Chroma vector database."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50,
        separators=["\n\n", "\n", ". ", " "]
    )
    chunks = splitter.split_text(text)
    documents = [Document(page_content=chunk) for chunk in chunks]
    
    # Generate embeddings locally using Ollama
    embeddings = OllamaEmbeddings(model="qwen3-embedding:0.6b")
    vector_db = Chroma.from_documents(documents=documents, embedding=embeddings)
    return vector_db

def retrieve_relevant_context(vector_db, query: str, top_k: int = 4) -> str:
    """Retrieve top-K matching chunks from the resume against the query."""
    docs = vector_db.similarity_search(query, k=top_k)
    return "\n---\n".join([doc.page_content for doc in docs])

def get_llm_response(prompt, pdf_text, job_desc):
    response = ollama.chat(
        model='qwen3:0.6b',
        messages=[
            {'role': 'system', 'content': prompt},
            {'role': 'user', 'content': f"Job Description:\n{job_desc}\n\nResume:\n{pdf_text}"}
        ]
    )
    content = response['message']['content']
    
    # Remove <think>...</think> block including newline characters
    cleaned_content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
    return cleaned_content

# Initialize Groq Client (Free tier API key from console.groq.com)
# client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_pdf_text(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        content = page.extract_text()
        if content:
            text += content + "\n"
    return text

# Streamlit App
st.set_page_config(page_title="ATS Resume Expert")
st.header("ATS Tracking System (Open-Source)")

input_text = st.text_area("Job Description:", key="input")
uploaded_file = st.file_uploader("Upload your resume (PDF)...", type=["pdf"])

if uploaded_file is not None:
    st.success("PDF Uploaded Successfully")

submit1 = st.button("Tell Me About the Resume")
submit3 = st.button("Percentage Match")

input_prompt1 = """
You are an experienced Technical Human Resource Manager. Review the provided resume against the job description. 
Highlight strengths, weaknesses, and overall alignment.
"""

input_prompt3 = """
You are a skilled ATS scanner. Evaluate the resume against the job description. 
Provide:
1. Match Percentage
2. Missing Keywords
3. Final Summary Thoughts
"""

if submit1 or submit3:
    if uploaded_file is not None and input_text.strip():
        chosen_prompt = input_prompt1 if submit1 else input_prompt3
        header_title = "HR Evaluation" if submit1 else "ATS Match Report"
        
        with st.spinner("Indexing resume into vector store and running RAG..."):
            # 1. Parse PDF
            raw_text = extract_pdf_text(uploaded_file)
            
            # 2. Build local vector store & retrieve top matches
            vector_db = build_vector_store(raw_text)
            retrieved_context = retrieve_relevant_context(vector_db, query=input_text, top_k=4)
            
            # 3. Query LLM with retrieved context
            response = get_llm_response(chosen_prompt, retrieved_context, input_text)
            
            st.subheader(header_title)
            st.write(response)
            
            # 4. Display source chunks for transparency
            with st.expander("Show Retrieved Evidence Chunks"):
                st.write(retrieved_context)
    else:
        st.warning("Please provide both a resume and a job description.")