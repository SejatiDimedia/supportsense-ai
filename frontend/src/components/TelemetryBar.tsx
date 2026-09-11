import React from 'react';
import { Database, Network, ShieldAlert, Sparkles } from 'lucide-react';
import { TelemetryData } from '../types';

interface TelemetryBarProps {
  telemetry: TelemetryData | null;
  isLoading: boolean;
}

export const TelemetryBar: React.FC<TelemetryBarProps> = ({ telemetry, isLoading }) => {
  return (
    <div className="border-b border-white/[0.06] bg-[#0D121D] px-6 py-2.5">
      <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-1.5 text-slate-300 font-mono">
            <Database className="h-3.5 w-3.5 text-emerald-400" />
            <span className="text-slate-500">ChromaDB (RAG):</span>
            <span className="font-semibold text-emerald-400">
              {isLoading ? '...' : `${telemetry?.chroma_count ?? 14} vectors`}
            </span>
          </div>

          <div className="h-3 w-px bg-white/[0.1]" />

          <div className="flex items-center gap-1.5 text-slate-300 font-mono">
            <Network className="h-3.5 w-3.5 text-purple-400" />
            <span className="text-slate-500">PostgreSQL (KAG):</span>
            <span className="font-semibold text-purple-400">
              {isLoading ? '...' : `${telemetry?.graph_nodes ?? 48} nodes · ${telemetry?.graph_edges ?? 46} edges`}
            </span>
          </div>

          <div className="h-3 w-px bg-white/[0.1]" />

          <div className="flex items-center gap-1.5 text-slate-300 font-mono">
            <ShieldAlert className="h-3.5 w-3.5 text-amber-400" />
            <span className="text-slate-500">Escalation Queue:</span>
            <span className={`font-semibold ${telemetry?.pending_escalations ? 'text-amber-400' : 'text-slate-300'}`}>
              {isLoading ? '...' : `${telemetry?.pending_escalations ?? 0} pending`}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2 text-slate-400">
          <Sparkles className="h-3.5 w-3.5 text-blue-400" />
          <span className="text-slate-500">Models:</span>
          <span className="font-mono text-slate-300">
            {telemetry?.models.llm ?? 'hermes3:latest'}
          </span>
          <span className="text-slate-600">/</span>
          <span className="font-mono text-slate-400">
            {telemetry?.models.embedding ?? 'nomic-embed-text'}
          </span>
        </div>
      </div>
    </div>
  );
};
