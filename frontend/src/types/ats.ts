export interface SkillAuditItem {
  skill: string;
  status: 'FOUND' | 'PARTIAL' | 'MISSING';
  importance: 'HIGH' | 'MEDIUM' | 'LOW';
  evidence?: string;
}

export interface ATSAnalysisResult {
  match_percentage: number;
  years_experience_found: string;
  experience_criteria_met: boolean;
  summary_verdict: string;
  strengths: string[];
  critical_gaps: string[];
  actionable_recommendations: string[];
  skill_audit: SkillAuditItem[];
}

export interface AnalyzeResponse {
  success: boolean;
  data: ATSAnalysisResult;
  retrieved_chunks?: string;
  error?: string;
}

