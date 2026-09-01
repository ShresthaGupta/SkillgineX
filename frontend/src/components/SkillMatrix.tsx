import React, { useState } from 'react';
import { Search, Filter, AlertTriangle, CheckCircle2, XCircle, PenTool } from 'lucide-react';

interface SkillAuditItem {
  skill: string;
  status: 'FOUND' | 'PARTIAL' | 'MISSING';
  importance: 'HIGH' | 'MEDIUM' | 'LOW';
  evidence?: string;
}

export function SkillMatrix({ skills, onTailorSkill }: { skills: SkillAuditItem[], onTailorSkill: (skill: string) => void }) {
  const [filter, setFilter] = useState<'ALL' | 'FOUND' | 'MISSING'>('ALL');

  const filteredSkills = skills.filter((s) => {
    if (filter === 'ALL') return true;
    if (filter === 'FOUND') return s.status === 'FOUND';
    if (filter === 'MISSING') return s.status === 'MISSING' || s.status === 'PARTIAL';
    return true;
  });

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-xs overflow-hidden flex flex-col">
      <div className="p-5 border-b border-slate-200 dark:border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h3 className="text-sm font-bold text-slate-900 dark:text-white">Keyword & Skill Audit Matrix</h3>
          <p className="text-xs text-slate-500">Extracted from Job Description vs Resume Match</p>
        </div>
        <div className="flex bg-slate-100 dark:bg-slate-800 p-1 rounded-lg">
          {(['ALL', 'FOUND', 'MISSING'] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`text-xs px-3 py-1.5 rounded-md font-semibold transition ${
                filter === f
                  ? 'bg-white dark:bg-slate-700 text-indigo-600 dark:text-indigo-400 shadow-xs'
                  : 'text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm whitespace-nowrap">
          <thead className="bg-slate-50 dark:bg-slate-950/50 text-xs uppercase tracking-wider text-slate-500 border-b border-slate-200 dark:border-slate-800">
            <tr>
              <th className="px-6 py-3 font-semibold">Skill / Keyword</th>
              <th className="px-6 py-3 font-semibold">Importance</th>
              <th className="px-6 py-3 font-semibold">Match Status</th>
              <th className="px-6 py-3 font-semibold">Evidence / Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
            {filteredSkills.map((s, idx) => (
              <tr key={idx} className="hover:bg-slate-50 dark:hover:bg-slate-900/50 transition">
                <td className="px-6 py-4 font-semibold text-slate-900 dark:text-white">{s.skill}</td>
                <td className="px-6 py-4">
                  <span className={`text-[11px] px-2 py-0.5 rounded-md font-bold ${
                    s.importance === 'HIGH' ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400' :
                    s.importance === 'MEDIUM' ? 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400' :
                    'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400'
                  }`}>
                    {s.importance}
                  </span>
                </td>
                <td className="px-6 py-4">
                  {s.status === 'FOUND' ? (
                    <span className="flex items-center gap-1.5 text-emerald-600 dark:text-emerald-400 font-semibold text-xs">
                      <CheckCircle2 className="w-4 h-4" /> Found
                    </span>
                  ) : s.status === 'PARTIAL' ? (
                    <span className="flex items-center gap-1.5 text-amber-600 dark:text-amber-400 font-semibold text-xs">
                      <AlertTriangle className="w-4 h-4" /> Partial
                    </span>
                  ) : (
                    <span className="flex items-center gap-1.5 text-red-600 dark:text-red-400 font-semibold text-xs">
                      <XCircle className="w-4 h-4" /> Missing
                    </span>
                  )}
                </td>
                <td className="px-6 py-4 text-xs">
                  {s.status === 'FOUND' ? (
                    <span className="text-slate-500 truncate max-w-[200px] block" title={s.evidence}>
                      {s.evidence || 'Verified in text'}
                    </span>
                  ) : (
                    <button
                      onClick={() => onTailorSkill(s.skill)}
                      className="text-indigo-600 dark:text-indigo-400 font-semibold flex items-center gap-1.5 hover:underline"
                    >
                      <PenTool className="w-3.5 h-3.5" />
                      Auto-Tailor Bullet
                    </button>
                  )}
                </td>
              </tr>
            ))}
            {filteredSkills.length === 0 && (
              <tr>
                <td colSpan={4} className="px-6 py-8 text-center text-slate-500 text-xs">
                  No skills match the current filter.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

