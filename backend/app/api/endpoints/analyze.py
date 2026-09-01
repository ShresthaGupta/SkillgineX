from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import ollama

from app.core.config import settings
from app.schemas.ats import (
    AnalyzeResponse,
    TailorBulletRequest,
    TailoredBulletResponse
)
from app.services.pdf_service import extract_pdf_text_from_bytes, create_section_chunks
from app.services.rag_service import get_hybrid_context
from app.services.agent_service import (
    agent_1_extract_jd_criteria,
    agent_2_synthesize_and_audit,
    generate_tailored_bullets
)

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint to verify backend status and Ollama connectivity."""
    ollama_status = "unreachable"
    try:
        client = ollama.Client(host=settings.OLLAMA_BASE_URL)
        models = client.list()
        ollama_status = "connected"
    except Exception as e:
        ollama_status = f"error: {str(e)}"
        
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "ollama_status": ollama_status,
        "active_model": settings.OLLAMA_MODEL
    }

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    """End-to-end multi-agent ATS resume analysis endpoint."""
    if not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty.")
    
    if not resume.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    try:
        file_bytes = await resume.read()
        raw_text = extract_pdf_text_from_bytes(file_bytes)
        
        if not raw_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from the uploaded PDF.")
            
        doc_sections = create_section_chunks(raw_text)
        jd_criteria = agent_1_extract_jd_criteria(job_description)
        
        skills_query = ", ".join(jd_criteria.core_skills) if jd_criteria.core_skills else job_description[:300]
        retrieval_query = f"Experience: {jd_criteria.min_years_experience} years. Skills: {skills_query}"
        retrieved_context = get_hybrid_context(doc_sections, query=retrieval_query, top_k=4)
        
        analysis_result = agent_2_synthesize_and_audit(retrieved_context, jd_criteria, job_description)
        
        return AnalyzeResponse(
            success=True,
            data=analysis_result,
            retrieved_chunks=retrieved_context
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API Error /analyze]: {e}")
        return AnalyzeResponse(
            success=False,
            error=str(e)
        )

@router.post("/tailor-bullets", response_model=TailoredBulletResponse)
async def tailor_bullets(request: TailorBulletRequest):
    """Generates tailored resume bullets for a missing skill using the Google XYZ formula."""
    try:
        result = generate_tailored_bullets(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate bullets: {str(e)}")

