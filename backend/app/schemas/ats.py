from pydantic import BaseModel, Field
from typing import List, Optional

class SkillAudit(BaseModel):
    skill_name: str = Field(description="The required skill or capability from the Job Description")
    status: str = Field(description="'Found', 'Missing', or 'Partial'")
    evidence: str = Field(description="Exact quote or context from the resume if found, otherwise 'N/A'")

class JDRequirements(BaseModel):
    min_years_experience: int = Field(default=0, description="Minimum years required as an integer")
    core_skills: List[str] = Field(default_factory=list, description="List of required core technical and soft skills")

class ATSAnalysisResult(BaseModel):
    match_percentage: int = Field(description="Match score from 0 to 100")
    years_experience_found: str = Field(description="Detected total years of experience in resume")
    experience_criteria_met: bool = Field(description="Whether minimum experience requirement is met (true/false)")
    skill_audit: List[SkillAudit] = Field(default_factory=list, description="Itemized evaluation of key JD requirements")
    strengths: List[str] = Field(default_factory=list, description="Top standout competencies matched in the resume")
    critical_gaps: List[str] = Field(default_factory=list, description="Must-have requirements from JD that are absent")
    actionable_recommendations: List[str] = Field(default_factory=list, description="Specific suggestions for the candidate to bridge gaps")
    summary_verdict: str = Field(description="Crisp 2-3 sentence assessment of candidate fit")

class AnalyzeResponse(BaseModel):
    success: bool
    data: Optional[ATSAnalysisResult] = None
    retrieved_chunks: Optional[str] = None
    error: Optional[str] = None

class TailorBulletRequest(BaseModel):
    skill_name: str = Field(description="The missing or weak skill to target")
    job_title: Optional[str] = Field(default="Software Engineer", description="Target job title")
    user_context: Optional[str] = Field(default="", description="Candidate's raw experience or project context")

class TailoredBulletResponse(BaseModel):
    skill_name: str
    suggested_bullets: List[str] = Field(description="Action-oriented bullet points matching Google XYZ format")
    formula_breakdown: Optional[str] = Field(default="", description="Explanation of how the bullet aligns with Accomplished [X], measured by [Y], by doing [Z]")

