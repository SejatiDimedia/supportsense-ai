import React from 'react';
import { Play } from 'lucide-react';
import { ScenarioItem } from '../types';

interface ScenarioChipsProps {
  onSelectScenario: (prompt: string) => void;
  disabled?: boolean;
}

const SCENARIOS: ScenarioItem[] = [
  {
    id: 'kag_order_4521',
    title: 'Order #4521 Status',
    category: 'KAG',
    prompt: 'Where is my order #4521?',
    expectedRoute: 'kag',
  },
  {
    id: 'rag_refund',
    title: '30-Day Refund Policy',
    category: 'RAG',
    prompt: 'What is your refund policy and eligibility?',
    expectedRoute: 'rag',
  },
  {
    id: 'kag_lost_transit',
    title: 'Order #4534 Lost in Transit',
    category: 'KAG',
    prompt: 'Where is my order #4534?',
    expectedRoute: 'kag',
  },
  {
    id: 'rag_warranty',
    title: 'Hardware Warranty Length',
    category: 'RAG',
    prompt: 'How long is the warranty for electronics and how to file an RMA claim?',
    expectedRoute: 'rag',
  },
  {
    id: 'security_escalation',
    title: 'Security Alert / Password',
    category: 'Escalation',
    prompt: 'I suspect unauthorized activity on my account and need an immediate password reset.',
    expectedRoute: 'escalated',
  },
  {
    id: 'direct_greeting',
    title: 'General Greeting',
    category: 'Direct',
    prompt: 'Hello, how can you help me today?',
    expectedRoute: 'direct',
  },
];

const ROUTE_BADGE_STYLES: Record<string, string> = {
  RAG: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400',
  KAG: 'border-purple-500/30 bg-purple-500/10 text-purple-400',
  Escalation: 'border-red-500/30 bg-red-500/10 text-red-400',
  Direct: 'border-blue-500/30 bg-blue-500/10 text-blue-400',
};

export const ScenarioChips: React.FC<ScenarioChipsProps> = ({
  onSelectScenario,
  disabled,
}) => {
  return (
    <div className="border-b border-white/[0.06] bg-[#0A0E17]/60 px-6 py-2.5">
      <div className="mx-auto flex max-w-7xl items-center gap-3 overflow-x-auto py-0.5 no-scrollbar">
        <span className="shrink-0 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
          Quick Test Scenarios:
        </span>
        <div className="flex items-center gap-2">
          {SCENARIOS.map((scenario) => (
            <button
              key={scenario.id}
              onClick={() => onSelectScenario(scenario.prompt)}
              disabled={disabled}
              className="group flex shrink-0 items-center gap-2 rounded-full border border-white/[0.08] bg-white/[0.03] px-3 py-1 text-xs text-slate-300 transition-all hover:border-white/[0.2] hover:bg-white/[0.07] hover:text-white disabled:opacity-40"
            >
              <span
                className={`rounded px-1.5 py-0.2 text-[10px] font-semibold uppercase tracking-wider border ${
                  ROUTE_BADGE_STYLES[scenario.category] || 'border-slate-700 bg-slate-800 text-slate-300'
                }`}
              >
                {scenario.category}
              </span>
              <span className="font-medium">{scenario.title}</span>
              <Play className="h-3 w-3 text-slate-500 transition-transform group-hover:translate-x-0.5 group-hover:text-emerald-400" />
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
