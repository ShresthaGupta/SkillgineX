import React from 'react';

export function ScoreGauge({ score }: { score: number }) {
  const normalizedScore = Math.min(Math.max(score, 0), 100);
  
  let color = 'text-red-500';
  if (normalizedScore >= 80) color = 'text-emerald-500';
  else if (normalizedScore >= 60) color = 'text-amber-500';

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-xs flex flex-col items-center justify-center h-full">
      <h3 className="text-sm font-bold uppercase tracking-wider text-slate-500 mb-4">Overall ATS Match</h3>
      <div className="relative flex items-center justify-center w-32 h-32">
        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
          <circle
            cx="50"
            cy="50"
            r="45"
            className="text-slate-200 dark:text-slate-800"
            strokeWidth="10"
            fill="none"
            stroke="currentColor"
          />
          <circle
            cx="50"
            cy="50"
            r="45"
            className={color}
            strokeWidth="10"
            fill="none"
            stroke="currentColor"
            strokeDasharray={`${(normalizedScore / 100) * 283} 283`}
            strokeLinecap="round"
          />
        </svg>
        <div className="absolute flex flex-col items-center justify-center">
          <span className={`text-4xl font-extrabold ${color}`}>{normalizedScore}%</span>
        </div>
      </div>
    </div>
  );
}

