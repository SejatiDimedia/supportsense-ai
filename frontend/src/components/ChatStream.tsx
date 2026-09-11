import React, { useState, useEffect, useRef } from 'react';
import { Bot, User, Copy, Check, Eye, Clock, ShieldCheck, Zap, Sparkles, Layers, Database, BrainCircuit } from 'lucide-react';
import { ChatMessage, RouteType } from '../types';

interface ChatStreamProps {
  messages: ChatMessage[];
  isLoading: boolean;
  onInspectContext: (message: ChatMessage) => void;
  selectedMessageId?: string;
  onStreamingComplete?: (messageId: string) => void;
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

const getThinkingStep = (seconds: number) => {
  if (seconds < 1.2) {
    return {
      step: 'Step 1/3',
      title: 'Semantic Query Routing',
      detail: 'Analyzing inquiry intent across RAG and KAG pipelines',
      Icon: Layers,
    };
  }
  if (seconds < 3.2) {
    return {
      step: 'Step 2/3',
      title: 'Relational Graph & Vector Retrieval',
      detail: 'Traversing PostgreSQL schema and matching policy chunks',
      Icon: Database,
    };
  }
  return {
    step: 'Step 3/3',
    title: 'Grounded Response Synthesis',
    detail: 'Synthesizing response with Hermes LLM and validating facts',
    Icon: BrainCircuit,
  };
};

const StreamingText: React.FC<{
  text: string;
  isStreaming?: boolean;
  onComplete?: () => void;
}> = ({ text, isStreaming, onComplete }) => {
  const [displayedLength, setDisplayedLength] = useState(isStreaming ? 0 : text.length);

  useEffect(() => {
    if (!isStreaming) {
      setDisplayedLength(text.length);
      return;
    }

    setDisplayedLength(0);
    let current = 0;
    const total = text.length;
    const interval = setInterval(() => {
      current += Math.max(3, Math.floor(Math.random() * 4) + 2);
      if (current >= total) {
        setDisplayedLength(total);
        clearInterval(interval);
        onComplete?.();
      } else {
        setDisplayedLength(current);
      }
    }, 16);

    return () => clearInterval(interval);
  }, [text, isStreaming, onComplete]);

  if (!isStreaming || displayedLength >= text.length) {
    return <div className="whitespace-pre-wrap leading-relaxed font-sans">{text}</div>;
  }

  return (
    <div className="whitespace-pre-wrap leading-relaxed font-sans">
      {text.slice(0, displayedLength)}
      <span className="inline-block w-1.5 h-3.5 ml-0.5 bg-slate-800 animate-pulse align-middle" />
    </div>
  );
};

export const ChatStream: React.FC<ChatStreamProps> = ({
  messages,
  isLoading,
  onInspectContext,
  selectedMessageId,
  onStreamingComplete,
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
    <div className="flex-1 overflow-y-auto px-4 md:px-8 py-6 space-y-5 max-w-4xl w-full mx-auto">
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
              className={`max-w-[85%] md:max-w-2xl rounded-2xl p-4 text-sm transition-all ${
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

              {/* Text content with progressive streaming support */}
              <StreamingText
                text={msg.text}
                isStreaming={msg.isStreaming}
                onComplete={() => onStreamingComplete?.(msg.id)}
              />

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

      {/* Loading & Reasoning State */}
      {isLoading && (() => {
        const step = getThinkingStep(elapsedSeconds);
        const StepIcon = step.Icon;
        return (
          <div className="flex gap-3.5 justify-start">
            <div className="relative flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-slate-900 text-white shadow-sm">
              <Bot className="h-4 w-4" />
              <span className="absolute -top-0.5 -right-0.5 flex h-2.5 w-2.5">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-lime-400 opacity-75" />
                <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-lime-400" />
              </span>
            </div>

            <div className="max-w-xl w-full rounded-2xl border border-slate-200 bg-white p-4 shadow-sm space-y-3">
              {/* Header row: Sparkles + Thinking text + animated typing dots + elapsed time pill */}
              <div className="flex items-center justify-between border-b border-slate-100 pb-2.5">
                <div className="flex items-center gap-2">
                  <Sparkles className="h-3.5 w-3.5 text-slate-700" />
                  <span className="text-xs font-semibold text-slate-900 tracking-tight">
                    SupportSense is thinking
                  </span>
                  <div className="flex items-center gap-1 pl-1">
                    <span className="h-1.5 w-1.5 rounded-full bg-slate-400 dot-1" />
                    <span className="h-1.5 w-1.5 rounded-full bg-slate-400 dot-2" />
                    <span className="h-1.5 w-1.5 rounded-full bg-slate-400 dot-3" />
                  </div>
                </div>
                <span className="font-mono text-[11px] text-slate-600 bg-slate-50 px-2 py-0.5 rounded-md border border-slate-200">
                  {elapsedSeconds.toFixed(1)}s
                </span>
              </div>

              {/* Active progressive pipeline step */}
              <div className="flex items-start gap-2.5">
                <div className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-lg bg-slate-100 text-slate-700">
                  <StepIcon className="h-3.5 w-3.5" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-medium text-slate-900">
                      {step.title}
                    </span>
                    <span className="text-[10px] font-mono uppercase tracking-wider text-slate-600">
                      {step.step}
                    </span>
                  </div>
                  <p className="mt-0.5 text-[11px] text-slate-600">
                    {step.detail}
                  </p>
                </div>
              </div>

              {/* Shimmer skeleton lines */}
              <div className="space-y-1.5 pt-1">
                <div className="h-1.5 w-4/5 rounded-full bg-slate-200/80 animate-pulse" />
                <div className="h-1.5 w-3/5 rounded-full bg-slate-200/50 animate-pulse" />
              </div>
            </div>
          </div>
        );
      })()}

      <div ref={bottomRef} />
    </div>
  );
};
