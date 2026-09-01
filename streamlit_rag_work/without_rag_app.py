import os
import streamlit as st
from pypdf import PdfReader
# from groq import Groq
from dotenv import load_dotenv
import ollama
import re

load_dotenv()


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

if submit1:
    if uploaded_file is not None and input_text.strip():
        with st.spinner("Analyzing..."):
            pdf_text = extract_pdf_text(uploaded_file)
            response = get_llm_response(input_prompt1, pdf_text, input_text)
            st.subheader("HR Evaluation")
            st.write(response)
    else:
        st.warning("Please provide both a resume and a job description.")

elif submit3:
    if uploaded_file is not None and input_text.strip():
        with st.spinner("Calculating ATS score..."):
            pdf_text = extract_pdf_text(uploaded_file)
            response = get_llm_response(input_prompt3, pdf_text, input_text)
            st.subheader("ATS Match Report")
            st.write(response)
    else:
        st.warning("Please provide both a resume and a job description.")