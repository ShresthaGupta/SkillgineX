import React, { useState } from 'react';
import { X, Sparkles, RefreshCw, Copy, Check } from 'lucide-react';

interface BulletTailorerModalProps {
  skillName: string;
  isOpen: boolean;
  onClose: () => void;
}

export function BulletTailorerModal({ skillName, isOpen, onClose }: BulletTailorerModalProps) {
  const [draft, setDraft] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState('');
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleGenerate = async () => {
    if (!draft.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('http://localhost:8000/api/v1/tailor-bullets', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          original_bullet: draft,
          target_skill: skillName
        })
      });
      if (!res.ok) throw new Error('Generation failed');
      const data = await res.json();
      if (data.success && data.data) {
        setResult(data.data.tailored_bullet);
      } else {
        throw new Error(data.error || 'Failed to tailor');
      }
    } catch (err: any) {
      setError(err.message || 'Error communicating with backend.');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    if (!result) return;
    navigator.clipboard.writeText(result);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white dark:bg-slate-900 w-full max-w-xl rounded-2xl shadow-xl overflow-hidden flex flex-col border border-slate-200 dark:border-slate-800">
        <div className="p-4 border-b border-slate-200 dark:border-slate-800 flex justify-between items-center bg-indigo-50/50 dark:bg-indigo-950/20">
          <h2 className="font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-indigo-600" />
            Tailor for: <span className="text-indigo-600 dark:text-indigo-400">{skillName}</span>
          </h2>
          <button onClick={onClose} className="text-slate-500 hover:text-slate-800 dark:hover:text-slate-200">
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <div className="p-6 space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-2">
              Paste an existing resume bullet:
            </label>
            <textarea
              className="w-full text-sm p-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 focus:ring-2 focus:ring-indigo-500 resize-none h-24"
              placeholder="e.g., Developed a web application using React..."
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
            />
          </div>

          <button
            onClick={handleGenerate}
            disabled={loading || !draft.trim()}
            className="w-full py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-sm flex justify-center items-center gap-2 transition disabled:opacity-50"
          >
            {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
            {loading ? 'Generating...' : 'Apply XYZ Formula'}
          </button>

          {error && <p className="text-red-500 text-xs mt-2">{error}</p>}

          {result && (
            <div className="mt-4 p-4 rounded-xl border border-emerald-200 bg-emerald-50 dark:border-emerald-900/50 dark:bg-emerald-950/20 space-y-3">
              <label className="text-xs font-bold text-emerald-700 dark:text-emerald-400">Optimized Bullet (XYZ Format)</label>
              <p className="text-sm text-slate-800 dark:text-slate-200 font-medium leading-relaxed">{result}</p>
              <button
                onClick={handleCopy}
                className="flex items-center gap-1.5 text-xs font-semibold text-emerald-600 hover:text-emerald-700 dark:text-emerald-400"
              >
                {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                {copied ? 'Copied!' : 'Copy to Clipboard'}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

