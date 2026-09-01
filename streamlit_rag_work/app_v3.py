import os
import re
import json
import streamlit as st
import pandas as pd
from pypdf import PdfReader
from dotenv import load_dotenv
import ollama

from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.retrievers import BM25Retriever
from pydantic import BaseModel, Field
from typing import List

load_dotenv()

# --- 1. Granular Pydantic Schemas ---
class SkillAudit(BaseModel):
    skill_name: str = Field(description="The required skill or capability from the Job Description")
    status: str = Field(description="'Found', 'Missing', or 'Partial'")
    evidence: str = Field(description="Exact quote or project context from the resume if found, otherwise 'N/A'")

class ATSAnalysisResult(BaseModel):
    match_percentage: int = Field(description="Match score from 0 to 100")
    years_experience_found: str = Field(description="Detected total years of experience")
    experience_criteria_met: bool = Field(description="Whether minimum experience requirement is met (true/false)")
    skill_audit: List[SkillAudit] = Field(description="Itemized evaluation of key JD requirements")
    strengths: List[str] = Field(description="Top 3 standout competencies matched in the resume")
    critical_gaps: List[str] = Field(description="Must-have requirements from JD that are absent")
    actionable_recommendations: List[str] = Field(description="Specific suggestions for the candidate to bridge gaps")
    summary_verdict: str = Field(description="Crisp 2-3 sentence assessment of candidate fit")

# --- 2. Text Extraction & Section Chunking ---
def extract_pdf_text(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        content = page.extract_text()
        if content:
            text += content + "\n"
    return text

def create_section_chunks(text: str) -> List[Document]:
    section_patterns = r"\n(?=(?:Summary|Experience|Projects|Skills|Education|Certifications|Work History)\b)"
    raw_sections = re.split(section_patterns, text, flags=re.IGNORECASE)
    
    docs = []
    for section in raw_sections:
        cleaned = section.strip()
        if len(cleaned) > 20:
            docs.append(Document(page_content=cleaned))
    return docs

# --- 3. Hybrid Retriever (BM25 + Dense Vectors) ---
def get_hybrid_context(documents: List[Document], query: str, top_k: int = 3) -> str:
    bm25_retriever = BM25Retriever.from_documents(documents)
    bm25_retriever.k = top_k
    bm25_docs = bm25_retriever.invoke(query)
    
    # Use qwen3-embedding:0.6b (or nomic-embed-text)
    embeddings = OllamaEmbeddings(model="qwen3-embedding:0.6b")
    vector_db = Chroma.from_documents(documents=documents, embedding=embeddings)
    vector_docs = vector_db.similarity_search(query, k=top_k)
    
    seen_content = set()
    combined_chunks = []
    for doc in (bm25_docs + vector_docs):
        if doc.page_content not in seen_content:
            seen_content.add(doc.page_content)
            combined_chunks.append(doc.page_content)
            
    return "\n\n---\n\n".join(combined_chunks)

# --- 4. LLM Generation with SkillAudit Schema ---
def run_ats_evaluation(context: str, job_desc: str) -> ATSAnalysisResult:
    system_prompt = """
You are an expert ATS screening system. Analyze the provided resume context strictly against the job description requirements.

Output ONLY valid JSON matching this schema:
{
  "match_percentage": <integer 0-100>,
  "years_experience_found": "<e.g., '4 years'>",
  "experience_criteria_met": <true/false based on JD requirement>,
  "skill_audit": [
    {
      "skill_name": "<skill from JD>",
      "status": "<'Found' | 'Missing' | 'Partial'>",
      "evidence": "<exact quote or context from resume if present, else 'N/A'>"
    }
  ],
  "strengths": ["<strength 1>", "<strength 2>"],
  "critical_gaps": ["<gap 1>", "<gap 2>"],
  "actionable_recommendations": ["<recommendation 1>", "<recommendation 2>"],
  "summary_verdict": "<short evaluation paragraph>"
}
"""

    user_prompt = f"JOB DESCRIPTION:\n{job_desc}\n\nRETRIEVED RESUME CONTEXT:\n{context}"

    response = ollama.chat(
        model='qwen3:0.6b',
        format='json',
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ]
    )
    
    raw_content = response['message']['content']
    cleaned = re.sub(r'<think>.*?</think>', '', raw_content, flags=re.DOTALL).strip()
    
    try:
        data = json.loads(cleaned)
        return ATSAnalysisResult(**data)
    except Exception:
        return ATSAnalysisResult(
            match_percentage=0,
            years_experience_found="Unknown",
            experience_criteria_met=False,
            skill_audit=[],
            strengths=[],
            critical_gaps=[],
            actionable_recommendations=[],
            summary_verdict=cleaned
        )

# --- 5. Streamlit Interface ---
st.set_page_config(page_title="ATS Skill & Requirement Auditor", layout="wide")
st.header("ATS Skill Audit & Alignment Engine")

col_input1, col_input2 = st.columns([1, 1])
with col_input1:
    input_text = st.text_area("Job Description:", height=240)
with col_input2:
    uploaded_file = st.file_uploader("Upload Resume (PDF):", type=["pdf"])

if st.button("Run Comprehensive Audit"):
    if uploaded_file and input_text.strip():
        with st.spinner("Executing hybrid retrieval and auditing criteria..."):
            raw_text = extract_pdf_text(uploaded_file)
            doc_sections = create_section_chunks(raw_text)
            retrieved_context = get_hybrid_context(doc_sections, input_text, top_k=3)
            result = run_ats_evaluation(retrieved_context, input_text)
            
            # High-Level Metrics
            m1, m2, m3 = st.columns(3)
            m1.metric("Match Score", f"{result.match_percentage}%")
            m2.metric("Experience Found", result.years_experience_found)
            m3.metric("Min Exp Met?", "Yes" if result.experience_criteria_met else "No")
            
            st.divider()
            
            # Granular Skill Audit Table
            st.subheader("Skill-by-Skill Requirement Audit")
            if result.skill_audit:
                audit_records = [
                    {
                        "Required Skill / Requirement": item.skill_name,
                        "Status": item.status,
                        "Resume Evidence / Quote": item.evidence
                    }
                    for item in result.skill_audit
                ]
                df_audit = pd.DataFrame(audit_records)
                st.dataframe(df_audit, use_container_width=True)
            else:
                st.write("No granular skill items extracted.")
            
            st.divider()
            
            # Strengths, Gaps, Recommendations
            c1, c2, c3 = st.columns(3)
            with c1:
                st.subheader("Standout Strengths")
                for s in result.strengths:
                    st.success(f"• {s}")
            with c2:
                st.subheader("Critical Gaps")
                for g in result.critical_gaps:
                    st.error(f"• {g}")
            with c3:
                st.subheader("Actionable Improvements")
                for r in result.actionable_recommendations:
                    st.info(f"• {r}")
                    
            st.subheader("Executive Summary Verdict")
            st.write(result.summary_verdict)
            
            with st.expander("Show Retrieved Evidence Chunks (BM25 + Semantic)"):
                st.text(retrieved_context)
    else:
        st.warning("Please provide both a job description and a resume.")