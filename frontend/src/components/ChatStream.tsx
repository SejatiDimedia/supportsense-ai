import React, { useState, useEffect, useRef } from 'react';
import { Bot, User, Copy, Check, Eye, Clock, ShieldCheck, Zap } from 'lucide-react';
import { ChatMessage, RouteType } from '../types';

interface ChatStreamProps {
  messages: ChatMessage[];
  isLoading: boolean;
  onInspectContext: (message: ChatMessage) => void;
  selectedMessageId?: string;
}

const ROUTE_CONFIG: Record<RouteType, { label: string; style: string; desc: string }> = {
  rag: {
    label: 'RAG (Docs)',
    style: 'border-emerald-500/35 bg-emerald-500/10 text-emerald-400',
    desc: 'Semantic retrieval from ChromaDB vector knowledge base',
  },
  kag: {
    label: 'KAG (Graph)',
    style: 'border-purple-500/35 bg-purple-500/10 text-purple-400',
    desc: 'Relational knowledge graph traversal from PostgreSQL',
  },
  hybrid: {
    label: 'Hybrid (RAG+KAG)',
    style: 'border-amber-500/35 bg-amber-500/10 text-amber-400',
    desc: 'Combined document retrieval and relational order synthesis',
  },
  direct: {
    label: 'Direct (<5ms)',
    style: 'border-blue-500/35 bg-blue-500/10 text-blue-400',
    desc: 'Pre-filtered sub-millisecond intent handler',
  },
  escalated: {
    label: 'Escalated',
    style: 'border-red-500/40 bg-red-500/15 text-red-400',
    desc: 'Zero-loss human escalation dispatched to webhook queue',
  },
};

export const ChatStream: React.FC<ChatStreamProps> = ({
  messages,
  isLoading,
  onInspectContext,
  selectedMessageId,
}) => {
  const bottomRef = useRef<HTMLDivElement>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  // Reasoning timer during model inference
  useEffect(() => {
    let timer: any;
    if (isLoading) {
      setElapsedSeconds(0);
      timer = setInterval(() => {
        setElapsedSeconds((prev) => prev + 0.1);
      }, 100);
    }
    return () => clearInterval(timer);
  }, [isLoading]);

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6">
      {messages.length === 0 && (
        <div className="flex h-full min-h-[360px] flex-col items-center justify-center text-center">
          <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-xl border border-white/[0.08] bg-white/[0.03] text-slate-400">
            <Bot className="h-6 w-6" />
          </div>
          <h2 className="text-base font-semibold text-slate-200">
            SupportSense AI Ready
          </h2>
          <p className="mt-1 max-w-md text-xs text-slate-400 leading-relaxed">
            Ask any question about order status, tracking numbers, warranty, or return policies.
            Or pick a pre-canned scenario chip above to run multi-path routing tests.
          </p>
        </div>
      )}

      {messages.map((msg) => {
        const isUser = msg.sender === 'user';
        const isSelected = msg.id === selectedMessageId;

        return (
          <div
            key={msg.id}
            className={`flex gap-3.5 ${isUser ? 'justify-end' : 'justify-start'}`}
          >
            {!isUser && (
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-white/[0.1] bg-white/[0.04] text-emerald-400">
                <Bot className="h-4 w-4" />
              </div>
            )}

            <div
              className={`max-w-2xl rounded-xl border transition-all ${
                isUser
                  ? 'border-emerald-500/20 bg-emerald-950/20 text-slate-100'
                  : isSelected
                  ? 'border-emerald-500/40 bg-[#121824] shadow-lg shadow-black/40'
                  : 'border-white/[0.08] bg-[#0E1420] text-slate-200'
              } p-4`}
            >
              {/* Telemetry & Routing Badges for Assistant */}
              {!isUser && msg.route_taken && (
                <div className="mb-3 flex flex-wrap items-center gap-2 border-b border-white/[0.06] pb-2.5 text-[11px]">
                  <span
                    className={`inline-flex items-center gap-1 rounded px-2 py-0.5 font-semibold uppercase tracking-wider border ${
                      ROUTE_CONFIG[msg.route_taken]?.style || 'border-slate-700 bg-slate-800 text-slate-300'
                    }`}
                    title={ROUTE_CONFIG[msg.route_taken]?.desc}
                  >
                    <Zap className="h-3 w-3" />
                    {ROUTE_CONFIG[msg.route_taken]?.label || msg.route_taken}
                  </span>

                  {msg.confidence_score !== undefined && (
                    <span className="inline-flex items-center gap-1 rounded border border-white/[0.08] bg-white/[0.03] px-2 py-0.5 font-mono text-slate-300">
                      <ShieldCheck className="h-3 w-3 text-slate-400" />
                      Conf: {(msg.confidence_score * 100).toFixed(0)}%
                    </span>
                  )}

                  {msg.latency_ms !== undefined && (
                    <span className="inline-flex items-center gap-1 rounded border border-white/[0.08] bg-white/[0.03] px-2 py-0.5 font-mono text-slate-400">
                      <Clock className="h-3 w-3" />
                      {msg.latency_ms < 1000
                        ? `${msg.latency_ms.toFixed(0)}ms`
                        : `${(msg.latency_ms / 1000).toFixed(2)}s`}
                    </span>
                  )}

                  {msg.trace_id && (
                    <span className="font-mono text-[10px] text-slate-500">
                      #{msg.trace_id}
                    </span>
                  )}
                </div>
              )}

              {/* Message Content */}
              <div className="whitespace-pre-wrap text-sm leading-relaxed font-sans text-slate-100">
                {msg.text}
              </div>

              {/* Footer Actions for Assistant Messages */}
              {!isUser && (
                <div className="mt-3 flex items-center justify-between border-t border-white/[0.06] pt-2 text-xs text-slate-500">
                  <span className="font-mono text-[11px]">{msg.timestamp}</span>

                  <div className="flex items-center gap-2">
                    {msg.context_used && (
                      <button
                        onClick={() => onInspectContext(msg)}
                        className={`inline-flex items-center gap-1 rounded px-2 py-0.5 font-medium transition-colors ${
                          isSelected
                            ? 'bg-emerald-500/20 text-emerald-400'
                            : 'text-slate-400 hover:bg-white/[0.06] hover:text-slate-200'
                        }`}
                      >
                        <Eye className="h-3 w-3" />
                        Inspect Grounding
                      </button>
                    )}

                    <button
                      onClick={() => handleCopy(msg.text, msg.id)}
                      className="text-slate-400 hover:text-slate-200 p-1 rounded hover:bg-white/[0.06] transition-colors"
                      title="Copy response"
                    >
                      {copiedId === msg.id ? (
                        <Check className="h-3.5 w-3.5 text-emerald-400" />
                      ) : (
                        <Copy className="h-3.5 w-3.5" />
                      )}
                    </button>
                  </div>
                </div>
              )}
            </div>

            {isUser && (
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-white/[0.1] bg-white/[0.04] text-slate-300">
                <User className="h-4 w-4" />
              </div>
            )}
          </div>
        );
      })}

      {/* Reasoning Shimmer State */}
      {isLoading && (
        <div className="flex gap-3.5 justify-start">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-emerald-500/30 bg-emerald-500/10 text-emerald-400">
            <Bot className="h-4 w-4 animate-spin" />
          </div>
          <div className="max-w-xl rounded-xl border border-white/[0.08] bg-[#0E1420] p-4 text-xs text-slate-300">
            <div className="flex items-center gap-2.5">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
              </span>
              <span className="font-semibold text-white tracking-wide">
                Agent Routing & Knowledge Synthesis in Progress
              </span>
              <span className="font-mono text-slate-400">
                ({elapsedSeconds.toFixed(1)}s)
              </span>
            </div>
            <p className="mt-2 text-slate-400 leading-relaxed font-mono text-[11px]">
              Inspecting intent - evaluating RAG vectors, PostgreSQL graph entities, and confidence thresholds...
            </p>
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
};
