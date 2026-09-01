'use client';

import React, { useState } from 'react';
import { 
  UploadCloud, 
  FileText, 
  Sparkles, 
  CheckCircle2, 
  XCircle, 
  AlertCircle, 
  Clock, 
  ArrowRight, 
  Briefcase, 
  ShieldCheck, 
  TrendingUp, 
  Database,
  RefreshCw,
  Award,
  Layers
} from 'lucide-react';
import { Navbar } from '@/components/Navbar';
import { ScoreGauge } from '@/components/ScoreGauge';
import { SkillMatrix } from '@/components/SkillMatrix';
import { BulletTailorerModal } from '@/components/BulletTailorerModal';
import { RetrievedEvidenceModal } from '@/components/RetrievedEvidenceModal';
import { JOB_PRESETS } from '@/data/jobPresets';
import { ATSAnalysisResult, AnalyzeResponse } from '@/types/ats';

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [analysisResult, setAnalysisResult] = useState<ATSAnalysisResult | null>(null);
  const [retrievedChunks, setRetrievedChunks] = useState<string>('');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Modals state
  const [tailorModalSkill, setTailorModalSkill] = useState<string | null>(null);
  const [evidenceModalOpen, setEvidenceModalOpen] = useState<boolean>(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      if (!selected.name.toLowerCase().endsWith('.pdf')) {
        setErrorMessage('Please upload a PDF resume.');
        return;
      }
      setFile(selected);
      setErrorMessage(null);
    }
  };

  const handleApplyPreset = (presetText: string) => {
    setJobDescription(presetText);
  };

  const handleRunAudit = async () => {
    if (!file) {
      setErrorMessage('Please upload your resume (PDF).');
      return;
    }
    if (!jobDescription.trim()) {
      setErrorMessage('Please paste a job description or select a preset.');
      return;
    }

    setLoading(true);
    setErrorMessage(null);

    const formData = new FormData();
    formData.append('resume', file);
    formData.append('job_description', jobDescription);

    try {
      const response = await fetch('http://localhost:8000/api/v1/analyze', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to analyze resume.');
      }

      const result: AnalyzeResponse = await response.json();
      if (!result.success || !result.data) {
        throw new Error(result.error || 'Audit analysis returned an error.');
      }

      setAnalysisResult(result.data);
      setRetrievedChunks(result.retrieved_chunks || '');
    } catch (err: any) {
      setErrorMessage(err.message || 'Connection to backend failed. Please ensure FastAPI is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 flex flex-col font-sans">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Hero Section */}
        <section className="text-center max-w-3xl mx-auto space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-100 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 text-xs font-semibold border border-indigo-200 dark:border-indigo-800">
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI Career Copilot for Job Seekers</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-slate-900 dark:text-white">
            Beat the ATS. Land the <span className="bg-gradient-to-r from-blue-600 via-indigo-600 to-violet-600 bg-clip-text text-transparent">Interview</span>.
          </h1>
          <p className="text-sm text-slate-600 dark:text-slate-400">
            Audit your resume with hybrid semantic RAG, itemize keyword match gaps with exact resume citations, and tailor missing bullet points instantly.
          </p>
        </section>

        {/* Input Configuration Panel */}
        <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Resume Upload Box */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-xs flex flex-col justify-between space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                  <FileText className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                  1. Upload Resume (PDF)
                </h2>
                {file && (
                  <span className="text-[11px] font-semibold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/40 px-2 py-0.5 rounded-md border border-emerald-200 dark:border-emerald-800">
                    Ready
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-500 mb-4">
                Upload your latest PDF resume. Sections will be semantically indexed.
              </p>

              <label
                htmlFor="resume-upload"
                className={`border-2 border-dashed rounded-xl p-6 flex flex-col items-center justify-center cursor-pointer transition ${
                  file
                    ? 'border-emerald-300 bg-emerald-50/30 dark:border-emerald-800 dark:bg-emerald-950/20'
                    : 'border-slate-300 dark:border-slate-700 hover:border-indigo-400 bg-slate-50/50 dark:bg-slate-800/40'
                }`}
              >
                <input
                  id="resume-upload"
                  type="file"
                  accept=".pdf"
                  onChange={handleFileChange}
                  className="hidden"
                />
                <UploadCloud className={`w-10 h-10 mb-2 ${file ? 'text-emerald-500' : 'text-slate-400'}`} />
                {file ? (
                  <div className="text-center">
                    <p className="text-sm font-semibold text-slate-900 dark:text-white">{file.name}</p>
                    <p className="text-xs text-slate-500">{(file.size / 1024).toFixed(1)} KB • PDF Document</p>
                  </div>
                ) : (
                  <div className="text-center">
                    <p className="text-xs font-semibold text-slate-700 dark:text-slate-300">Click to upload or drag & drop</p>
                    <p className="text-[11px] text-slate-400">PDF up to 10MB</p>
                  </div>
                )}
              </label>
            </div>

            <div className="text-[11px] text-slate-400 flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" />
              <span>Parsed locally in-memory with PyPDF & LangChain.</span>
            </div>
          </div>

          {/* Job Description Box */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-xs flex flex-col space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                  <Briefcase className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                  2. Target Job Description
                </h2>
              </div>
              
              {/* Presets */}
              <div className="flex flex-wrap items-center gap-1.5 mb-2">
                <span className="text-[11px] font-semibold text-slate-400 mr-1">Presets:</span>
                {JOB_PRESETS.map((preset) => (
                  <button
                    key={preset.id}
                    onClick={() => handleApplyPreset(preset.description)}
                    className="text-[11px] px-2.5 py-1 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:text-indigo-600 hover:border-indigo-300 transition"
                  >
                    {preset.title.split(' ')[0]} {preset.title.split(' ')[1]}
                  </button>
                ))}
              </div>

              <textarea
                rows={6}
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                placeholder="Paste the full job description or select a preset above..."
                className="w-full p-3 text-xs rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-indigo-500 resize-none font-mono"
              />
            </div>

            {errorMessage && (
              <div className="p-3 rounded-xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900 text-xs text-red-600 dark:text-red-400 flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{errorMessage}</span>
              </div>
            )}

            <button
              onClick={handleRunAudit}
              disabled={loading}
              className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-blue-600 via-indigo-600 to-violet-600 hover:from-blue-700 hover:to-violet-700 text-white font-semibold text-sm flex items-center justify-center gap-2 shadow-md shadow-indigo-500/25 disabled:opacity-50 transition"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Multi-Agent Hybrid RAG Pipeline Executing...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>Run Comprehensive ATS Audit</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
        </section>

        {/* Loading Progress State */}
        {loading && (
          <section className="bg-white dark:bg-slate-900 border border-indigo-200 dark:border-indigo-900/60 rounded-2xl p-6 shadow-sm space-y-4 animate-pulse">
            <h3 className="text-sm font-bold text-indigo-600 dark:text-indigo-400 flex items-center gap-2">
              <Layers className="w-4 h-4" />
              Pipeline Execution Status
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 text-xs">
              <div className="p-3 rounded-lg bg-indigo-50/60 dark:bg-indigo-950/40 border border-indigo-100 dark:border-indigo-900">
                <span className="font-semibold text-indigo-700 dark:text-indigo-300">1. PDF Chunking</span>
                <p className="text-[11px] text-slate-500">Semantic regex section indexing</p>
              </div>
              <div className="p-3 rounded-lg bg-indigo-50/60 dark:bg-indigo-950/40 border border-indigo-100 dark:border-indigo-900">
                <span className="font-semibold text-indigo-700 dark:text-indigo-300">2. Agent 1 (JD Parser)</span>
                <p className="text-[11px] text-slate-500">Extracting constraints & skills</p>
              </div>
              <div className="p-3 rounded-lg bg-indigo-50/60 dark:bg-indigo-950/40 border border-indigo-100 dark:border-indigo-900">
                <span className="font-semibold text-indigo-700 dark:text-indigo-300">3. Hybrid Retrieval</span>
                <p className="text-[11px] text-slate-500">BM25 + Chroma dense search</p>
              </div>
              <div className="p-3 rounded-lg bg-indigo-50/60 dark:bg-indigo-950/40 border border-indigo-100 dark:border-indigo-900">
                <span className="font-semibold text-indigo-700 dark:text-indigo-300">4. Agent 2 + Guardrail</span>
                <p className="text-[11px] text-slate-500">Auditing with Pydantic retry</p>
              </div>
            </div>
          </section>
        )}

        {/* Analysis Results Section */}
        {analysisResult && (
          <section className="space-y-6">
            {/* Top Row: Score + Experience + Executive Verdict */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Score Gauge */}
              <div className="flex flex-col">
                <ScoreGauge score={analysisResult.match_percentage} />
              </div>

              {/* Experience and Criteria KPI Cards */}
              <div className="flex flex-col justify-between gap-4">
                <div className="p-5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-xs space-y-2 flex-1">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold uppercase text-slate-400">Experience Detected</span>
                    <Clock className="w-4 h-4 text-indigo-500" />
                  </div>
                  <p className="text-2xl font-extrabold text-slate-900 dark:text-white">
                    {analysisResult.years_experience_found || 'Unknown'}
                  </p>
                  <p className="text-xs text-slate-500">Detected from work history dates and summary</p>
                </div>

                <div className="p-5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-xs space-y-2 flex-1">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold uppercase text-slate-400">Min Experience Requirement</span>
                    {analysisResult.experience_criteria_met ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                    ) : (
                      <AlertCircle className="w-4 h-4 text-amber-500" />
                    )}
                  </div>
                  <p className="text-2xl font-extrabold text-slate-900 dark:text-white">
                    {analysisResult.experience_criteria_met ? (
                      <span className="text-emerald-600">Requirement Met ✓</span>
                    ) : (
                      <span className="text-amber-600">Gap Detected</span>
                    )}
                  </p>
                  <p className="text-xs text-slate-500">Verified against job description threshold</p>
                </div>
              </div>

              {/* Executive Verdict */}
              <div className="p-5 bg-gradient-to-br from-indigo-50/80 via-white to-violet-50/50 dark:from-slate-900 dark:via-slate-900 dark:to-indigo-950/30 border border-indigo-100 dark:border-indigo-900/50 rounded-2xl shadow-xs flex flex-col justify-between">
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-indigo-600 dark:text-indigo-400 font-bold text-xs uppercase tracking-wider">
                    <Award className="w-4 h-4" />
                    <span>Executive Fit Verdict</span>
                  </div>
                  <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed font-medium">
                    &ldquo;{analysisResult.summary_verdict}&rdquo;
                  </p>
                </div>
                <div className="pt-3 border-t border-indigo-100/60 dark:border-slate-800 flex items-center justify-between">
                  <button
                    onClick={() => setEvidenceModalOpen(true)}
                    className="text-[11px] font-semibold text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1"
                  >
                    <Database className="w-3.5 h-3.5" />
                    <span>View Retrieved RAG Chunks</span>
                  </button>
                </div>
              </div>
            </div>

            {/* Strengths vs Critical Gaps vs Recommendations */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Standout Strengths */}
              <div className="bg-white dark:bg-slate-900 border border-emerald-200 dark:border-emerald-950/60 rounded-2xl p-5 shadow-xs space-y-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-700 dark:text-emerald-400 flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4" />
                  Standout Strengths ({analysisResult.strengths?.length || 0})
                </h4>
                <ul className="space-y-2">
                  {analysisResult.strengths?.map((s, idx) => (
                    <li key={idx} className="text-xs text-slate-700 dark:text-slate-300 bg-emerald-50/50 dark:bg-emerald-950/20 p-2.5 rounded-lg border border-emerald-100 dark:border-emerald-900/40">
                      • {s}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Critical Gaps */}
              <div className="bg-white dark:bg-slate-900 border border-red-200 dark:border-red-950/60 rounded-2xl p-5 shadow-xs space-y-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-red-700 dark:text-red-400 flex items-center gap-1.5">
                  <XCircle className="w-4 h-4" />
                  Critical Gaps ({analysisResult.critical_gaps?.length || 0})
                </h4>
                <ul className="space-y-2">
                  {analysisResult.critical_gaps?.map((g, idx) => (
                    <li key={idx} className="text-xs text-slate-700 dark:text-slate-300 bg-red-50/50 dark:bg-red-950/20 p-2.5 rounded-lg border border-red-100 dark:border-red-900/40">
                      • {g}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Actionable Improvements */}
              <div className="bg-white dark:bg-slate-900 border border-indigo-200 dark:border-indigo-950/60 rounded-2xl p-5 shadow-xs space-y-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-indigo-700 dark:text-indigo-400 flex items-center gap-1.5">
                  <TrendingUp className="w-4 h-4" />
                  Actionable Advice ({analysisResult.actionable_recommendations?.length || 0})
                </h4>
                <ul className="space-y-2">
                  {analysisResult.actionable_recommendations?.map((r, idx) => (
                    <li key={idx} className="text-xs text-slate-700 dark:text-slate-300 bg-indigo-50/50 dark:bg-indigo-950/20 p-2.5 rounded-lg border border-indigo-100 dark:border-indigo-900/40">
                      • {r}
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Granular Skill Audit Table */}
            <SkillMatrix
              skills={analysisResult.skill_audit || []}
              onTailorSkill={(skill) => setTailorModalSkill(skill)}
            />
          </section>
        )}
      </main>

      {/* Bullet Tailoring Modal */}
      {tailorModalSkill && (
        <BulletTailorerModal
          skillName={tailorModalSkill}
          isOpen={!!tailorModalSkill}
          onClose={() => setTailorModalSkill(null)}
        />
      )}

      {/* RAG Evidence Explorer Modal */}
      <RetrievedEvidenceModal
        evidenceText={retrievedChunks}
        isOpen={evidenceModalOpen}
        onClose={() => setEvidenceModalOpen(false)}
      />

      <footer className="border-t border-slate-200 dark:border-slate-800 py-6 text-center text-xs text-slate-400">
        <p>TalentFit ATS AI • Powered by Hybrid RAG (LangChain + Chroma + BM25) and FastAPI</p>
      </footer>
    </div>
  );
}
