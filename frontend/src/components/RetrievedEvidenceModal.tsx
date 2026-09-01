import React from 'react';
import { X, Database } from 'lucide-react';

interface RetrievedEvidenceModalProps {
  evidenceText: string;
  isOpen: boolean;
  onClose: () => void;
}

export function RetrievedEvidenceModal({ evidenceText, isOpen, onClose }: RetrievedEvidenceModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white dark:bg-slate-900 w-full max-w-3xl h-[80vh] rounded-2xl shadow-xl flex flex-col border border-slate-200 dark:border-slate-800 overflow-hidden">
        <div className="p-4 border-b border-slate-200 dark:border-slate-800 flex justify-between items-center bg-slate-50 dark:bg-slate-950">
          <h2 className="font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <Database className="w-4 h-4 text-indigo-500" />
            Raw RAG Context Retrieved
          </h2>
          <button onClick={onClose} className="text-slate-500 hover:text-slate-800 dark:hover:text-slate-200">
            <X className="w-5 h-5" />
          </button>
        </div>
        <div className="p-6 overflow-y-auto flex-1 bg-slate-50/50 dark:bg-slate-900/50">
          <p className="text-xs text-slate-500 mb-4">
            This is the exact text passed to the Agent LLM after the hybrid BM25 + Chroma retrieval step.
          </p>
          <pre className="whitespace-pre-wrap text-[11px] font-mono text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-950 p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-inner">
            {evidenceText || 'No evidence text provided.'}
          </pre>
        </div>
      </div>
    </div>
  );
}

