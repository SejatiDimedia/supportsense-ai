import React, { useState } from 'react';
import { ChevronDown, Share2, MoreVertical, Check } from 'lucide-react';

interface HeaderProps {
  sessionId: string;
  onResetSession: () => void;
}

export const Header: React.FC<HeaderProps> = ({ sessionId, onResetSession }) => {
  const [copied, setCopied] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  const handleShare = () => {
    navigator.clipboard.writeText(window.location.href);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <header className="flex items-center justify-between border-b border-slate-100 bg-white px-8 py-3.5">
      {/* Model Selector Dropdown */}
      <div className="relative">
        <button
          onClick={() => setIsDropdownOpen(!isDropdownOpen)}
          className="flex items-center gap-2 rounded-lg px-2 py-1 text-sm font-semibold text-slate-800 hover:bg-slate-50 transition-colors"
        >
          <span>SupportSense 1.0</span>
          <ChevronDown className="h-4 w-4 text-slate-500 transition-transform" />
        </button>

        {isDropdownOpen && (
          <div className="absolute left-0 mt-1 w-64 rounded-xl border border-slate-200 bg-white p-2 shadow-xl shadow-slate-200/50 z-50 text-xs">
            <div className="rounded-lg bg-slate-50 p-2 border border-slate-100 mb-1">
              <div className="font-semibold text-slate-900">SupportSense 1.0</div>
              <div className="text-slate-500 mt-0.5">Hybrid RAG + KAG with PostgreSQL Parity</div>
            </div>
            <div className="p-2 text-slate-500 font-mono text-[11px] border-t border-slate-100">
              <span className="text-slate-400 block text-[10px] uppercase">Session ID</span>
              <span className="truncate block text-slate-700">{sessionId}</span>
            </div>
          </div>
        )}
      </div>

      {/* Right Actions: Share, Options, Profile */}
      <div className="flex items-center gap-3">
        <button
          onClick={handleShare}
          title="Share conversation"
          className="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200/80 bg-slate-50/50 text-slate-600 hover:bg-slate-100 hover:text-slate-900 transition-colors"
        >
          {copied ? <Check className="h-4 w-4 text-emerald-600" /> : <Share2 className="h-4 w-4" />}
        </button>

        <button
          onClick={onResetSession}
          title="Session settings & reset"
          className="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200/80 bg-slate-50/50 text-slate-600 hover:bg-slate-100 hover:text-slate-900 transition-colors"
        >
          <MoreVertical className="h-4 w-4" />
        </button>

        {/* Operator Profile Avatar Badge */}
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-slate-900 text-xs font-bold text-white shadow-sm border border-slate-800">
          OP
        </div>
      </div>
    </header>
  );
};
