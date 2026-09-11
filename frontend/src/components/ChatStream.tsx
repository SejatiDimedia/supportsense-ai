import React, { useState, useEffect, useRef } from 'react';
import { Bot, User, Copy, Check, Eye, Clock, ShieldCheck, Zap } from 'lucide-react';
import { ChatMessage, RouteType } from '../types';

interface ChatStreamProps {
  messages: ChatMessage[];
  isLoading: boolean;
  onInspectContext: (message: ChatMessage) => void;
  selectedMessageId?: string;
}

const ROUTE_CONFIG: Record<RouteType, { label: string; style: string }> = {
  rag: {
    label: 'RAG (Docs)',
    style: 'border-emerald-200 bg-emerald-50 text-emerald-700',
  },
  kag: {
    label: 'KAG (Graph)',
    style: 'border-purple-200 bg-purple-50 text-purple-700',
  },
  hybrid: {
    label: 'Hybrid (RAG+KAG)',
    style: 'border-amber-200 bg-amber-50 text-amber-700',
  },
  direct: {
    label: 'Direct (<5ms)',
    style: 'border-blue-200 bg-blue-50 text-blue-700',
  },
  escalated: {
    label: 'Escalated',
    style: 'border-red-200 bg-red-50 text-red-700',
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
    <div className="flex-1 overflow-y-auto px-8 py-6 space-y-5 max-w-4xl w-full mx-auto">
      {messages.map((msg) => {
        const isUser = msg.sender === 'user';
        const isSelected = msg.id === selectedMessageId;

        return (
          <div
            key={msg.id}
            className={`flex gap-3.5 ${isUser ? 'justify-end' : 'justify-start'}`}
          >
            {!isUser && (
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-slate-900 text-white shadow-sm">
                <Bot className="h-4 w-4" />
              </div>
            )}

            <div
              className={`max-w-2xl rounded-2xl p-4 text-sm transition-all ${
                isUser
                  ? 'bg-slate-900 text-white shadow-sm'
                  : isSelected
                  ? 'border border-emerald-400 bg-white shadow-md'
                  : 'border border-slate-200/80 bg-[#F9FAFB] text-slate-800'
              }`}
            >
              {/* Route Attribution Badges */}
              {!isUser && msg.route_taken && (
                <div className="mb-3 flex flex-wrap items-center gap-2 border-b border-slate-200/60 pb-2 text-xs">
                  <span
                    className={`inline-flex items-center gap-1 rounded-md px-2 py-0.5 font-bold uppercase tracking-wider text-[10px] border ${
                      ROUTE_CONFIG[msg.route_taken]?.style || 'border-slate-200 bg-slate-100 text-slate-700'
                    }`}
                  >
                    <Zap className="h-3 w-3" />
                    {ROUTE_CONFIG[msg.route_taken]?.label || msg.route_taken}
                  </span>

                  {msg.confidence_score !== undefined && (
                    <span className="inline-flex items-center gap-1 rounded-md border border-slate-200 bg-white px-2 py-0.5 font-mono text-[11px] text-slate-600">
                      <ShieldCheck className="h-3 w-3 text-emerald-600" />
                      {(msg.confidence_score * 100).toFixed(0)}%
                    </span>
                  )}

                  {msg.latency_ms !== undefined && (
                    <span className="inline-flex items-center gap-1 rounded-md border border-slate-200 bg-white px-2 py-0.5 font-mono text-[11px] text-slate-500">
                      <Clock className="h-3 w-3" />
                      {msg.latency_ms < 1000
                        ? `${msg.latency_ms.toFixed(0)}ms`
                        : `${(msg.latency_ms / 1000).toFixed(2)}s`}
                    </span>
                  )}

                  {msg.trace_id && (
                    <span className="font-mono text-[10px] text-slate-400">
                      #{msg.trace_id}
                    </span>
                  )}
                </div>
              )}

              {/* Text content */}
              <div className="whitespace-pre-wrap leading-relaxed font-sans">
                {msg.text}
              </div>

              {/* Footer Actions */}
              {!isUser && (
                <div className="mt-3 flex items-center justify-between border-t border-slate-200/60 pt-2 text-xs text-slate-400">
                  <span className="font-mono text-[11px]">{msg.timestamp}</span>

                  <div className="flex items-center gap-2">
                    {msg.context_used && (
                      <button
                        onClick={() => onInspectContext(msg)}
                        className={`inline-flex items-center gap-1 rounded px-2 py-0.5 font-medium transition-colors ${
                          isSelected
                            ? 'bg-emerald-100 text-emerald-800'
                            : 'text-slate-600 hover:bg-slate-200/60'
                        }`}
                      >
                        <Eye className="h-3 w-3" />
                        Inspect Grounding
                      </button>
                    )}

                    <button
                      onClick={() => handleCopy(msg.text, msg.id)}
                      className="p-1 rounded text-slate-400 hover:text-slate-700 hover:bg-slate-200/60 transition-colors"
                      title="Copy message"
                    >
                      {copiedId === msg.id ? (
                        <Check className="h-3.5 w-3.5 text-emerald-600" />
                      ) : (
                        <Copy className="h-3.5 w-3.5" />
                      )}
                    </button>
                  </div>
                </div>
              )}
            </div>

            {isUser && (
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-slate-200 text-slate-700">
                <User className="h-4 w-4" />
              </div>
            )}
          </div>
        );
      })}

      {/* Loading & Reasoning Shimmer */}
      {isLoading && (
        <div className="flex gap-3.5 justify-start">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-slate-900 text-white">
            <Bot className="h-4 w-4 animate-spin" />
          </div>
          <div className="max-w-xl rounded-2xl border border-slate-200 bg-white p-4 text-xs text-slate-600 shadow-sm">
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
              <span className="font-semibold text-slate-900">
                Analyzing inquiry across RAG & KAG pipelines...
              </span>
              <span className="font-mono text-slate-400">
                ({elapsedSeconds.toFixed(1)}s)
              </span>
            </div>
            <p className="mt-1.5 text-slate-400 font-mono text-[11px]">
              Querying PostgreSQL relational tables, calculating embedding similarity, and synthesizing response...
            </p>
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
};
