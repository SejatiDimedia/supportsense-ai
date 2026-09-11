import React, { useState } from 'react';
import { X, Copy, Check, Database, FileText, Cpu, ShieldAlert } from 'lucide-react';
import { ChatMessage } from '../types';

interface GroundingDrawerProps {
  message: ChatMessage | null;
  onClose: () => void;
}

export const GroundingDrawer: React.FC<GroundingDrawerProps> = ({ message, onClose }) => {
  const [copied, setCopied] = useState(false);

  if (!message) return null;

  const handleCopy = () => {
    if (message.context_used) {
      navigator.clipboard.writeText(message.context_used);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const isRelational = message.route_taken === 'kag' || message.context_used?.includes('RELATIONAL DATA');
  const isDocument = message.route_taken === 'rag' || message.context_used?.includes('DOCUMENT KNOWLEDGE BASE');

  return (
    <div className="flex h-full w-96 shrink-0 flex-col border-l border-slate-200 bg-white">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4 bg-slate-50/50">
        <div className="flex items-center gap-2">
          {isRelational ? (
            <Database className="h-4 w-4 text-purple-600" />
          ) : isDocument ? (
            <FileText className="h-4 w-4 text-emerald-600" />
          ) : (
            <Cpu className="h-4 w-4 text-blue-600" />
          )}
          <span className="text-xs font-bold uppercase tracking-wider text-slate-900">
            Grounding Audit Inspector
          </span>
        </div>

        <div className="flex items-center gap-1">
          <button
            onClick={handleCopy}
            title="Copy raw context"
            className="rounded p-1 text-slate-400 hover:bg-slate-200 hover:text-slate-700 transition-colors"
          >
            {copied ? <Check className="h-3.5 w-3.5 text-emerald-600" /> : <Copy className="h-3.5 w-3.5" />}
          </button>
          <button
            onClick={onClose}
            title="Close inspector"
            className="rounded p-1 text-slate-400 hover:bg-slate-200 hover:text-slate-700 transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Metadata Overview */}
      <div className="border-b border-slate-100 bg-slate-50/30 px-5 py-3 text-xs font-mono space-y-1.5 text-slate-500">
        <div className="flex justify-between">
          <span>Route Attribution:</span>
          <span className="font-bold uppercase text-slate-800">{message.route_taken}</span>
        </div>
        <div className="flex justify-between">
          <span>Confidence Score:</span>
          <span className="font-bold text-slate-800">
            {message.confidence_score !== undefined ? `${(message.confidence_score * 100).toFixed(1)}%` : 'N/A'}
          </span>
        </div>
        <div className="flex justify-between">
          <span>Inference Latency:</span>
          <span className="text-slate-800">
            {message.latency_ms !== undefined ? `${message.latency_ms.toFixed(1)} ms` : 'N/A'}
          </span>
        </div>
        <div className="flex justify-between">
          <span>Trace ID:</span>
          <span className="text-slate-600">#{message.trace_id || 'N/A'}</span>
        </div>
      </div>

      {/* Context Content */}
      <div className="flex-1 overflow-y-auto p-5 space-y-3">
        <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
          Source Grounding Excerpt:
        </div>

        {message.context_used ? (
          <pre className="whitespace-pre-wrap rounded-xl border border-slate-200 bg-slate-900 p-3.5 text-[11px] leading-relaxed text-slate-200 font-mono select-text">
            {message.context_used}
          </pre>
        ) : (
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-center text-xs text-slate-400">
            No grounding context was injected for this query (e.g. direct response).
          </div>
        )}

        {message.escalated && (
          <div className="rounded-xl border border-red-200 bg-red-50 p-3.5 text-xs text-red-800 flex items-start gap-2.5">
            <ShieldAlert className="h-4 w-4 shrink-0 text-red-600 mt-0.5" />
            <div>
              <div className="font-bold">Human Escalation Triggered</div>
              <p className="mt-0.5 text-[11px] text-red-700 leading-relaxed">
                Incident queued into zero-loss escalation repository and dispatched to n8n webhook.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
