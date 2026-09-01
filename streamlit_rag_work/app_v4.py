import os
import re
import json
import streamlit as st
import pandas as pd
from pypdf import PdfReader
from dotenv import load_dotenv

# --- Step 4: Observability & Tracing Setup ---
import phoenix as px
from phoenix.otel import register
from openinference.instrumentation.ollama import OllamaInstrumentor

# Cache the Phoenix session so it only starts once across Streamlit reruns
@st.cache_resource
def setup_observability():
    session = px.launch_app()
    tracer_provider = register(project_name="ats-doc-analyzer")
    OllamaInstrumentor().instrument(tracer_provider=tracer_provider)
    return session

session = setup_observability()

import ollama
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.retrievers import BM25Retriever
from pydantic import BaseModel, Field, ValidationError
from typing import List

load_dotenv()

# --- Step 2: Verification & Guardrail Schemas ---
class SkillAudit(BaseModel):
    skill_name: str = Field(description="The required skill or capability from the Job Description")
    status: str = Field(description="'Found', 'Missing', or 'Partial'")
    evidence: str = Field(description="Exact quote or context from the resume if found, otherwise 'N/A'")

class JDRequirements(BaseModel):
    min_years_experience: int = Field(default=0, description="Minimum years required as an integer")
    core_skills: List[str] = Field(description="List of required core technical and soft skills")

class ATSAnalysisResult(BaseModel):
    match_percentage: int = Field(description="Match score from 0 to 100")
    years_experience_found: str = Field(description="Detected total years of experience")
    experience_criteria_met: bool = Field(description="Whether minimum experience requirement is met (true/false)")
    skill_audit: List[SkillAudit] = Field(description="Itemized evaluation of key JD requirements")
    strengths: List[str] = Field(description="Top standout competencies matched in the resume")
    critical_gaps: List[str] = Field(description="Must-have requirements from JD that are absent")
    actionable_recommendations: List[str] = Field(description="Specific suggestions for the candidate to bridge gaps")
    summary_verdict: str = Field(description="Crisp 2-3 sentence assessment of candidate fit")

# --- Ingestion & Chunking ---
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
    return [Document(page_content=s.strip()) for s in raw_sections if len(s.strip()) > 20]

def get_hybrid_context(documents: List[Document], query: str, top_k: int = 3) -> str:
    bm25 = BM25Retriever.from_documents(documents)
    bm25.k = top_k
    bm25_docs = bm25.invoke(query)
    
    embeddings = OllamaEmbeddings(model="qwen3-embedding:0.6b")
    vector_db = Chroma.from_documents(documents=documents, embedding=embeddings)
    dense_docs = vector_db.similarity_search(query, k=top_k)
    
    seen = set()
    combined = []
    for doc in (bm25_docs + dense_docs):
        if doc.page_content not in seen:
            seen.add(doc.page_content)
            combined.append(doc.page_content)
    return "\n\n---\n\n".join(combined)

# --- Guardrail Call with Self-Correction Retry Loop ---
def call_llm_with_guardrail(messages: list, schema_cls: BaseModel, max_retries: int = 3):
    current_messages = list(messages)
    for attempt in range(max_retries):
        response = ollama.chat(
            model='qwen3:0.6b',
            format='json',
            messages=current_messages
        )
        raw_content = response['message']['content']
        cleaned = re.sub(r'<think>.*?</think>', '', raw_content, flags=re.DOTALL).strip()
        
        try:
            parsed_json = json.loads(cleaned)
            return schema_cls(**parsed_json)
        except (json.JSONDecodeError, ValidationError) as e:
            # Self-correction: append the error back into history and ask LLM to fix it
            current_messages.append({'role': 'assistant', 'content': cleaned})
            current_messages.append({
                'role': 'user', 
                'content': f"Validation Error: {str(e)}. Please correct your output and return valid JSON adhering strictly to the schema."
            })
    raise ValueError(f"Failed to produce valid schema after {max_retries} attempts.")

# --- Step 3: Multi-Agent Pipeline ---
def agent_1_extract_jd_criteria(job_desc: str) -> JDRequirements:
    """Agent 1: Extracts explicit constraints and technical skills from the JD."""
    system_prompt = """Extract the core requirements from the job description. Return JSON matching:
    {"min_years_experience": <int>, "core_skills": ["skill1", "skill2"]}"""
    
    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': f"Job Description:\n{job_desc}"}
    ]
    return call_llm_with_guardrail(messages, JDRequirements)

def agent_2_synthesize_and_audit(context: str, jd_reqs: JDRequirements, job_desc: str) -> ATSAnalysisResult:
    """Agent 2: Evaluates the resume sections against the extracted requirements."""
    system_prompt = f"""You are an ATS Screening Evaluator. Audit the candidate context against requirements:
Minimum Experience Required: {jd_reqs.min_years_experience} years
Key Skills to Check: {', '.join(jd_reqs.core_skills)}

Return JSON adhering to schema:
{{
  "match_percentage": <0-100>,
  "years_experience_found": "<e.g., '4 years'>",
  "experience_criteria_met": <true/false>,
  "skill_audit": [
    {{"skill_name": "<skill>", "status": "<Found|Missing|Partial>", "evidence": "<quote or N/A>"}}
  ],
  "strengths": ["<strength>"],
  "critical_gaps": ["<gap>"],
  "actionable_recommendations": ["<recommendation>"],
  "summary_verdict": "<summary>"
}}"""

    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': f"RETRIEVED RESUME CONTEXT:\n{context}\n\nORIGINAL JOB DESCRIPTION:\n{job_desc}"}
    ]
    return call_llm_with_guardrail(messages, ATSAnalysisResult)

# --- Streamlit UI ---
st.set_page_config(page_title="Multi-Agent ATS Engine", layout="wide")
st.header("Multi-Agent ATS Engine (RAG + Guardrails + Tracing)")

with st.sidebar:
    st.subheader("Observability & APM")
    st.markdown(f"[Open Phoenix Trace Dashboard]({session.url})")
    st.caption("Live latency, chunk retrieval tracking, and token telemetry.")

col_input1, col_input2 = st.columns([1, 1])
with col_input1:
    input_text = st.text_area("Job Description:", height=240)
with col_input2:
    uploaded_file = st.file_uploader("Upload Resume (PDF):", type=["pdf"])

if st.button("Run Multi-Agent Audit"):
    if uploaded_file and input_text.strip():
        with st.status("Running Agentic Pipeline...") as status:
            # 1. Parsing & Section Ingestion
            status.write("1/3 Parsing PDF and preparing hybrid index...")
            raw_text = extract_pdf_text(uploaded_file)
            doc_sections = create_section_chunks(raw_text)
            
            # 2. Agent 1: Requirement Extraction
            status.write("2/3 Agent 1: Extracting JD criteria and hard constraints...")
            jd_criteria = agent_1_extract_jd_criteria(input_text)
            
            # 3. Hybrid Search over Resume
            retrieval_query = f"Experience: {jd_criteria.min_years_experience} years. Skills: {', '.join(jd_criteria.core_skills)}"
            retrieved_context = get_hybrid_context(doc_sections, query=retrieval_query, top_k=4)
            
            # 4. Agent 2: Synthesis & Audit with Guardrails
            status.write("3/3 Agent 2: Running audit and validating Pydantic guardrails...")
            result = agent_2_synthesize_and_audit(retrieved_context, jd_criteria, input_text)
            
            status.update(label="Analysis complete!", state="complete", expanded=False)
            
        # Display High-Level Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Match Score", f"{result.match_percentage}%")
        m2.metric("Experience Detected", result.years_experience_found)
        m3.metric("Experience Criteria Met?", "Yes" if result.experience_criteria_met else "No")
        
        st.divider()
        
        # Skill Audit Table
        st.subheader("Granular Skill Audit")
        if result.skill_audit:
            audit_records = [
                {
                    "Requirement": item.skill_name,
                    "Status": item.status,
                    "Evidence Quote": item.evidence
                }
                for item in result.skill_audit
            ]
            st.dataframe(pd.DataFrame(audit_records), use_container_width=True)
            
        st.divider()
        
        # Strengths / Gaps
        c1, c2, c3 = st.columns(3)
        with c1:
            st.subheader("Strengths")
            for s in result.strengths:
                st.success(f"• {s}")
        with c2:
            st.subheader("Critical Gaps")
            for g in result.critical_gaps:
                st.error(f"• {g}")
        with c3:
            st.subheader("Recommendations")
            for r in result.actionable_recommendations:
                st.info(f"• {r}")
                
        st.subheader("Verdict")
        st.write(result.summary_verdict)
    else:
        st.warning("Please upload both a resume and a job description.")