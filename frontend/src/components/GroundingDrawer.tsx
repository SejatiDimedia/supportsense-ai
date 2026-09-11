import React from 'react';
import { X, Copy, Check, FileText, Database, ShieldAlert, Cpu } from 'lucide-react';
import { ChatMessage } from '../types';

interface GroundingDrawerProps {
  message: ChatMessage | null;
  onClose: () => void;
}

export const GroundingDrawer: React.FC<GroundingDrawerProps> = ({ message, onClose }) => {
  const [copied, setCopied] = React.useState(false);

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
    <div className="flex h-full w-96 flex-col border-l border-white/[0.08] bg-[#0A0E17]">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-white/[0.08] px-4 py-3 bg-[#0D121D]">
        <div className="flex items-center gap-2">
          {isRelational ? (
            <Database className="h-4 w-4 text-purple-400" />
          ) : isDocument ? (
            <FileText className="h-4 w-4 text-emerald-400" />
          ) : (
            <Cpu className="h-4 w-4 text-blue-400" />
          )}
          <span className="text-xs font-bold uppercase tracking-wider text-slate-200">
            Grounding Audit Drawer
          </span>
        </div>

        <div className="flex items-center gap-1">
          <button
            onClick={handleCopy}
            title="Copy raw context"
            className="rounded p-1 text-slate-400 hover:bg-white/[0.06] hover:text-white transition-colors"
          >
            {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
          </button>
          <button
            onClick={onClose}
            title="Close drawer"
            className="rounded p-1 text-slate-400 hover:bg-white/[0.06] hover:text-white transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Metadata Overview */}
      <div className="border-b border-white/[0.06] bg-[#0E1420] px-4 py-2.5 text-[11px] font-mono space-y-1 text-slate-400">
        <div className="flex justify-between">
          <span>Route:</span>
          <span className="font-semibold uppercase text-slate-200">{message.route_taken}</span>
        </div>
        <div className="flex justify-between">
          <span>Confidence:</span>
          <span className="text-slate-200">
            {message.confidence_score !== undefined ? `${(message.confidence_score * 100).toFixed(1)}%` : 'N/A'}
          </span>
        </div>
        <div className="flex justify-between">
          <span>Latency:</span>
          <span className="text-slate-200">
            {message.latency_ms !== undefined ? `${message.latency_ms.toFixed(1)} ms` : 'N/A'}
          </span>
        </div>
        <div className="flex justify-between">
          <span>Trace ID:</span>
          <span className="text-slate-400">{message.trace_id || 'N/A'}</span>
        </div>
      </div>

      {/* Raw Context View */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
          Retrieved Grounding Records:
        </div>

        {message.context_used ? (
          <pre className="whitespace-pre-wrap rounded-lg border border-white/[0.08] bg-[#070A0F] p-3 text-xs leading-relaxed text-slate-300 font-mono select-text">
            {message.context_used}
          </pre>
        ) : (
          <div className="rounded-lg border border-white/[0.06] bg-white/[0.02] p-4 text-center text-xs text-slate-500">
            No grounding context was injected for this turn (e.g. direct response).
          </div>
        )}

        {message.escalated && (
          <div className="rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-xs text-red-300 flex items-start gap-2">
            <ShieldAlert className="h-4 w-4 shrink-0 text-red-400 mt-0.5" />
            <div>
              <div className="font-semibold">Human Escalation Triggered</div>
              <p className="mt-0.5 text-[11px] text-red-400/90 leading-relaxed">
                Incident queued into the zero-loss escalation repository and dispatched to n8n webhook.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
