import re
import json
from typing import Type, TypeVar
import ollama
from pydantic import BaseModel, ValidationError

from app.core.config import settings
from app.schemas.ats import (
    JDRequirements, 
    ATSAnalysisResult, 
    TailorBulletRequest, 
    TailoredBulletResponse
)

T = TypeVar("T", bound=BaseModel)

def call_llm_with_guardrail(messages: list, schema_cls: Type[T], max_retries: int = 3) -> T:
    """Invokes the Ollama LLM with structured JSON output and self-correction retry loop."""
    client = ollama.Client(host=settings.OLLAMA_BASE_URL)
    current_messages = list(messages)
    
    for attempt in range(max_retries):
        try:
            response = client.chat(
                model=settings.OLLAMA_MODEL,
                format='json',
                messages=current_messages
            )
            raw_content = response['message']['content']
            cleaned = re.sub(r'<think>.*?</think>', '', raw_content, flags=re.DOTALL).strip()
            
            parsed_json = json.loads(cleaned)
            return schema_cls(**parsed_json)
        except (json.JSONDecodeError, ValidationError) as e:
            current_messages.append({'role': 'assistant', 'content': raw_content})
            current_messages.append({
                'role': 'user', 
                'content': f"Validation error: {str(e)}. Please correct the JSON output strictly according to the required schema."
            })
        except Exception as e:
            print(f"[Agent Service Error] Attempt {attempt + 1}: {e}")
            
    raise ValueError(f"Failed to generate valid schema for {schema_cls.__name__} after {max_retries} attempts.")

def agent_1_extract_jd_criteria(job_desc: str) -> JDRequirements:
    """Agent 1: Extracts hard experience requirements and core technical/soft skills from the JD."""
    system_prompt = """You are an expert Job Specification Parser. 
Extract the core requirements from the job description.
Output ONLY valid JSON matching this schema:
{
  "min_years_experience": <integer, default 0 if not specified>,
  "core_skills": ["Skill 1", "Skill 2", "Skill 3", "Skill 4", "Skill 5"]
}"""
    
    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': f"Job Description:\n{job_desc}"}
    ]
    return call_llm_with_guardrail(messages, JDRequirements)

def agent_2_synthesize_and_audit(context: str, jd_reqs: JDRequirements, job_desc: str) -> ATSAnalysisResult:
    """Agent 2: Conducts comprehensive itemized ATS audit matching candidate evidence to JD criteria."""
    skills_list = ", ".join(jd_reqs.core_skills) if jd_reqs.core_skills else "all mentioned requirements"
    system_prompt = f"""You are an elite ATS Screening Evaluator and Career Coach. 
Audit the candidate's retrieved resume context against the Job Description.

Key Requirements to Check:
- Minimum Experience Target: {jd_reqs.min_years_experience} years
- Key Skills: {skills_list}

Output ONLY valid JSON matching this schema:
{{
  "match_percentage": <integer between 0 and 100>,
  "years_experience_found": "<e.g., '3.5 years'>",
  "experience_criteria_met": <true or false>,
  "skill_audit": [
    {{
      "skill_name": "<skill from JD>",
      "status": "<'Found' | 'Missing' | 'Partial'>",
      "evidence": "<exact direct quote or brief project context from resume if present, else 'N/A'>"
    }}
  ],
  "strengths": ["<top standout strength 1>", "<standout strength 2>", "<standout strength 3>"],
  "critical_gaps": ["<key missing must-have requirement 1>", "<key missing requirement 2>"],
  "actionable_recommendations": [
    "<specific improvement recommendation 1>",
    "<specific improvement recommendation 2>",
    "<specific improvement recommendation 3>"
  ],
  "summary_verdict": "<crisp, realistic 2-3 sentence hiring manager assessment>"
}}"""

    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': f"RETRIEVED RESUME EVIDENCE:\n{context}\n\nORIGINAL JOB DESCRIPTION:\n{job_desc}"}
    ]
    return call_llm_with_guardrail(messages, ATSAnalysisResult)

def generate_tailored_bullets(request: TailorBulletRequest) -> TailoredBulletResponse:
    """Generates high-impact resume bullet points tailored to bridge a candidate's missing skill using the Google XYZ formula."""
    system_prompt = """You are an Executive Resume Writer specializing in high-converting resumes.
Generate 3 tailored resume accomplishment bullets for the specified skill using the Google XYZ Formula:
"Accomplished [X], as measured by [Y], by doing [Z]"

Output ONLY valid JSON matching this schema:
{
  "skill_name": "<skill name>",
  "suggested_bullets": [
    "Accomplished [Impact/Result], as measured by [Metric/KPI], by [Action/Tool used]...",
    "Accomplished [Impact/Result], as measured by [Metric/KPI], by [Action/Tool used]...",
    "Accomplished [Impact/Result], as measured by [Metric/KPI], by [Action/Tool used]..."
  ],
  "formula_breakdown": "Accomplished [X: Business Goal], as measured by [Y: Quantitative Metric %/time/$], by doing [Z: Technical Implementation]"
}"""

    user_context = request.user_context if request.user_context else "Standard software engineering / tech project experience"
    user_prompt = f"""Target Skill: {request.skill_name}
Target Role: {request.job_title}
Candidate's Background / Context: {user_context}"""

    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_prompt}
    ]
    return call_llm_with_guardrail(messages, TailoredBulletResponse)

