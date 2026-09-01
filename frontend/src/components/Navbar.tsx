import React, { useState, useEffect } from 'react';
import { Activity, Server } from 'lucide-react';

export function Navbar() {
  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking');

  useEffect(() => {
    const checkBackend = async () => {
      try {
        const res = await fetch('http://localhost:8000/api/v1/health');
        if (res.ok) setBackendStatus('online');
        else setBackendStatus('offline');
      } catch (err) {
        setBackendStatus('offline');
      }
    };
    checkBackend();
  }, []);

  return (
    <nav className="border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-xs px-4 sm:px-6 lg:px-8 py-3 flex items-center justify-between">
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center">
          <Activity className="text-white w-5 h-5" />
        </div>
        <span className="font-extrabold text-lg tracking-tight text-slate-900 dark:text-white">TalentFit ATS</span>
      </div>
      
      <div className="flex items-center gap-2 text-xs font-semibold">
        <Server className="w-4 h-4 text-slate-400" />
        <span className="text-slate-600 dark:text-slate-400">Backend:</span>
        {backendStatus === 'checking' && (
          <span className="text-amber-500 animate-pulse">Checking...</span>
        )}
        {backendStatus === 'online' && (
          <span className="text-emerald-500 flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-emerald-500"></span> Online
          </span>
        )}
        {backendStatus === 'offline' && (
          <span className="text-red-500 flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-red-500"></span> Offline
          </span>
        )}
      </div>
    </nav>
  );
}

