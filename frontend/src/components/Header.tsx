import React, { useState } from 'react';
import { Cpu, RotateCcw, Copy, Check, Activity } from 'lucide-react';

interface HeaderProps {
  sessionId: string;
  isBackendHealthy: boolean;
  onResetSession: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  sessionId,
  isBackendHealthy,
  onResetSession,
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopySession = () => {
    navigator.clipboard.writeText(sessionId);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <header className="border-b border-white/[0.08] bg-[#0A0E17]/95 px-6 py-3.5 backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-emerald-500/30 bg-emerald-500/10 text-emerald-400">
            <Cpu className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-bold tracking-tight text-white">
                SupportSense AI
              </h1>
              <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-500/25 bg-emerald-500/10 px-2.5 py-0.5 text-[11px] font-semibold uppercase tracking-wider text-emerald-400">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 shadow-[0_0_6px_#10B981]" />
                Operate Console
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Hybrid RAG + KAG Multi-Path Assistant with Relational Parity
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 rounded-md border border-white/[0.08] bg-white/[0.03] px-3 py-1.5 text-xs text-slate-300">
            <Activity className="h-3.5 w-3.5 text-slate-400" />
            <span className="text-slate-400">Backend:</span>
            <span className={isBackendHealthy ? 'font-medium text-emerald-400' : 'font-medium text-amber-400'}>
              {isBackendHealthy ? 'Online (Port 8000)' : 'Connecting...'}
            </span>
          </div>

          <div className="flex items-center gap-1.5 rounded-md border border-white/[0.08] bg-white/[0.03] px-2.5 py-1.5 text-xs text-slate-300 font-mono">
            <span className="text-slate-500">Session:</span>
            <span className="text-slate-200">{sessionId.slice(0, 12)}...</span>
            <button
              onClick={handleCopySession}
              title="Copy session ID"
              className="ml-1 text-slate-400 hover:text-white transition-colors"
            >
              {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
            </button>
          </div>

          <button
            onClick={onResetSession}
            title="Reset conversation session"
            className="flex items-center gap-1.5 rounded-md border border-white/[0.1] bg-white/[0.05] px-3 py-1.5 text-xs font-medium text-slate-300 hover:bg-white/[0.1] hover:text-white transition-colors"
          >
            <RotateCcw className="h-3.5 w-3.5" />
            Reset
          </button>
        </div>
      </div>
    </header>
  );
};
