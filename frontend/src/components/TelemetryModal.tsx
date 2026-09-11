import React from 'react';
import { X, Database, Network, ShieldCheck, Cpu, CheckCircle2 } from 'lucide-react';
import { TelemetryData } from '../types';

interface TelemetryModalProps {
  isOpen: boolean;
  onClose: () => void;
  telemetry: TelemetryData | null;
}

export const TelemetryModal: React.FC<TelemetryModalProps> = ({
  isOpen,
  onClose,
  telemetry,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="w-full max-w-lg rounded-2xl border border-slate-200 bg-white p-6 shadow-2xl animate-in fade-in zoom-in-95 duration-150">
        <div className="flex items-center justify-between border-b border-slate-100 pb-4">
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-lime-400 text-black font-bold">
              <Database className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900">Cluster Architecture & Telemetry</h2>
              <p className="text-xs text-slate-500">Live health and topology of SupportSense AI</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-700 transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="mt-5 space-y-3.5 text-xs">
          {/* PostgreSQL KAG */}
          <div className="rounded-xl border border-slate-200/80 bg-slate-50 p-3.5">
            <div className="flex items-center justify-between font-semibold text-slate-900">
              <div className="flex items-center gap-2">
                <Network className="h-4 w-4 text-purple-600" />
                <span>PostgreSQL Relational KAG</span>
              </div>
              <span className="flex items-center gap-1 text-[11px] text-emerald-600 font-mono">
                <CheckCircle2 className="h-3.5 w-3.5" />
                Connected
              </span>
            </div>
            <div className="mt-2 grid grid-cols-2 gap-2 text-slate-600 font-mono">
              <div className="rounded-lg bg-white p-2 border border-slate-200/60">
                <span className="text-[10px] uppercase text-slate-400 block">Graph Nodes</span>
                <span className="text-sm font-bold text-slate-900">{telemetry?.graph_nodes ?? 48} Nodes</span>
              </div>
              <div className="rounded-lg bg-white p-2 border border-slate-200/60">
                <span className="text-[10px] uppercase text-slate-400 block">Directional Edges</span>
                <span className="text-sm font-bold text-slate-900">{telemetry?.graph_edges ?? 46} Edges</span>
              </div>
            </div>
          </div>

          {/* ChromaDB RAG */}
          <div className="rounded-xl border border-slate-200/80 bg-slate-50 p-3.5">
            <div className="flex items-center justify-between font-semibold text-slate-900">
              <div className="flex items-center gap-2">
                <Database className="h-4 w-4 text-emerald-600" />
                <span>ChromaDB Vector Store (RAG)</span>
              </div>
              <span className="text-[11px] text-emerald-600 font-mono font-medium">
                {telemetry?.chroma_count ?? 14} Documents
              </span>
            </div>
            <p className="mt-1 text-[11px] text-slate-500">
              Policies, customer support handbook, FAQs, and product return manuals loaded into persistent vector collection.
            </p>
          </div>

          {/* Escalation Queue */}
          <div className="rounded-xl border border-slate-200/80 bg-slate-50 p-3.5">
            <div className="flex items-center justify-between font-semibold text-slate-900">
              <div className="flex items-center gap-2">
                <ShieldCheck className="h-4 w-4 text-amber-600" />
                <span>Zero-Loss Escalation Queue</span>
              </div>
              <span className="text-[11px] text-slate-700 font-mono font-semibold">
                {telemetry?.pending_escalations ?? 0} Pending
              </span>
            </div>
            <p className="mt-1 text-[11px] text-slate-500">
              Dispatches incidents to n8n webhook with automatic background retries upon network recovery.
            </p>
          </div>

          {/* Local LLM Inference */}
          <div className="rounded-xl border border-slate-200/80 bg-slate-50 p-3.5 flex items-center justify-between">
            <div className="flex items-center gap-2 text-slate-900 font-medium">
              <Cpu className="h-4 w-4 text-blue-600" />
              <span>Ollama Engine</span>
            </div>
            <span className="font-mono text-[11px] text-slate-600">
              {telemetry?.models.llm ?? 'hermes3:latest'}
            </span>
          </div>
        </div>

        <div className="mt-6 flex justify-end">
          <button
            onClick={onClose}
            className="rounded-xl bg-slate-900 px-4 py-2 text-xs font-semibold text-white hover:bg-slate-800 transition-colors"
          >
            Close Audit
          </button>
        </div>
      </div>
    </div>
  );
};
