import io
import re
from typing import List
from pypdf import PdfReader
from langchain_core.documents import Document

def extract_pdf_text_from_bytes(file_bytes: bytes) -> str:
    """Extract full raw text from uploaded PDF bytes."""
    reader = PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        content = page.extract_text()
        if content:
            text += content + "\n"
    return text.strip()

def create_section_chunks(text: str) -> List[Document]:
    """Split resume text along semantic section boundaries (Experience, Projects, Skills, etc.)."""
    section_patterns = r"\n(?=(?:Summary|Professional Summary|Experience|Work Experience|Projects|Skills|Technical Skills|Education|Certifications|Work History|Key Achievements)\b)"
    raw_sections = re.split(section_patterns, text, flags=re.IGNORECASE)
    
    docs = []
    for section in raw_sections:
        cleaned = section.strip()
        if len(cleaned) > 20:
            docs.append(Document(page_content=cleaned))
            
    # Fallback if no section headers matched
    if not docs and text.strip():
        docs.append(Document(page_content=text.strip()))
        
    return docs

