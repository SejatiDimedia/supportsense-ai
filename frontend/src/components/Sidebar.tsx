import React, { useState } from 'react';
import { 
  SquarePen, 
  Search, 
  Layers, 
  HelpCircle, 
  Settings, 
  PanelLeftClose, 
  PanelLeftOpen,
  ArrowUpRight,
  Database
} from 'lucide-react';
import { TelemetryData } from '../types';

interface SidebarProps {
  onNewChat: () => void;
  telemetry: TelemetryData | null;
  onOpenTelemetryModal: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  onNewChat,
  telemetry,
  onOpenTelemetryModal,
}) => {
  const [isCollapsed, setIsCollapsed] = useState(false);

  const recentChats = [
    { id: '1', title: 'Order #4521 shipping status & carrier' },
    { id: '2', title: '30-Day refund policy criteria' },
    { id: '3', title: 'Order #4534 lost package follow-up' },
    { id: '4', title: 'Hardware 24-month warranty RMA' },
  ];

  if (isCollapsed) {
    return (
      <div className="flex h-full w-14 flex-col items-center justify-between border-r border-white/[0.08] bg-[#0E1116] py-4">
        <div className="flex flex-col items-center gap-4">
          <button
            onClick={() => setIsCollapsed(false)}
            title="Expand sidebar"
            className="flex h-9 w-9 items-center justify-center rounded-lg text-slate-400 hover:bg-white/[0.06] hover:text-white transition-colors"
          >
            <PanelLeftOpen className="h-5 w-5" />
          </button>
          <button
            onClick={onNewChat}
            title="New chat"
            className="flex h-9 w-9 items-center justify-center rounded-lg border border-white/[0.1] bg-white/[0.04] text-slate-300 hover:text-white hover:bg-white/[0.08] transition-colors"
          >
            <SquarePen className="h-4 w-4" />
          </button>
        </div>
        <button
          onClick={onOpenTelemetryModal}
          title="Cluster Telemetry"
          className="flex h-8 w-8 items-center justify-center rounded-lg bg-lime-400 text-black font-bold hover:bg-lime-500 transition-colors"
        >
          <Database className="h-4 w-4" />
        </button>
      </div>
    );
  }

  return (
    <aside className="flex h-full w-64 shrink-0 flex-col justify-between border-r border-white/[0.08] bg-[#0E1116] p-4 text-slate-300">
      {/* Top Header & Brand */}
      <div>
        <div className="flex items-center justify-between pb-4">
          <div className="flex items-center gap-2.5">
            <div className="flex h-7 w-7 items-center justify-center rounded-full border border-white/20 bg-white/10 text-white">
              <span className="h-2.5 w-2.5 rounded-full bg-lime-400" />
            </div>
            <span className="font-bold tracking-tight text-white text-base">
              SupportSense AI
            </span>
          </div>

          <button
            onClick={() => setIsCollapsed(true)}
            title="Collapse sidebar"
            className="rounded p-1 text-slate-400 hover:bg-white/[0.06] hover:text-white transition-colors"
          >
            <PanelLeftClose className="h-4 w-4" />
          </button>
        </div>

        {/* New Chat Button */}
        <button
          onClick={onNewChat}
          className="flex w-full items-center justify-between rounded-lg border border-white/[0.12] bg-white/[0.03] px-3 py-2 text-xs font-medium text-slate-200 transition-all hover:bg-white/[0.08] hover:border-white/[0.2]"
        >
          <div className="flex items-center gap-2">
            <SquarePen className="h-4 w-4 text-slate-400" />
            <span>New chat</span>
          </div>
          <kbd className="rounded border border-white/[0.15] bg-white/[0.05] px-1.5 py-0.5 font-mono text-[10px] text-slate-400">
            ⌘ N
          </kbd>
        </button>

        {/* Nav list */}
        <div className="mt-3 space-y-1 text-xs">
          <button className="flex w-full items-center gap-2.5 rounded-md px-2.5 py-1.5 text-slate-400 hover:bg-white/[0.05] hover:text-slate-200 transition-colors">
            <Search className="h-4 w-4" />
            <span>Search chat</span>
          </button>
          <button 
            onClick={onOpenTelemetryModal}
            className="flex w-full items-center gap-2.5 rounded-md px-2.5 py-1.5 text-slate-400 hover:bg-white/[0.05] hover:text-slate-200 transition-colors"
          >
            <Layers className="h-4 w-4" />
            <span>Knowledge Base & KAG</span>
          </button>
        </div>

        {/* Section Recent */}
        <div className="mt-6">
          <div className="px-2.5 text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
            Recent
          </div>
          <div className="mt-2 space-y-0.5">
            {recentChats.map((chat) => (
              <button
                key={chat.id}
                onClick={onNewChat}
                className="w-full truncate rounded-md px-2.5 py-1.5 text-left text-xs text-slate-400 hover:bg-white/[0.05] hover:text-slate-200 transition-colors"
                title={chat.title}
              >
                {chat.title}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom Area: Telemetry Card & Links */}
      <div className="space-y-4 pt-4">
        {/* Cluster Telemetry Card with Vibrant Lime Button (Matching Reference) */}
        <div className="rounded-xl border border-white/[0.08] bg-[#16191E] p-3.5 text-xs">
          <div className="flex items-center justify-between text-white font-semibold">
            <span>Cluster Status</span>
            <span className="flex items-center gap-1 text-[11px] text-emerald-400 font-mono">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 shadow-[0_0_4px_#10B981]" />
              Online
            </span>
          </div>
          <p className="mt-1 text-[11px] leading-relaxed text-slate-400 font-mono">
            {telemetry ? `${telemetry.graph_nodes} KAG nodes · ${telemetry.chroma_count} RAG vectors` : '48 KAG nodes · 14 RAG vectors'}
          </p>
          <button
            onClick={onOpenTelemetryModal}
            className="mt-3 flex w-full items-center justify-center gap-1.5 rounded-lg bg-lime-400 px-3 py-2 text-xs font-bold text-black transition-all hover:bg-lime-300"
          >
            <ArrowUpRight className="h-3.5 w-3.5 stroke-[2.5]" />
            <span>Audit Cluster</span>
          </button>
        </div>

        {/* Bottom utility links */}
        <div className="space-y-0.5 text-xs text-slate-400 border-t border-white/[0.06] pt-3">
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-2.5 rounded-md px-2.5 py-1.5 hover:bg-white/[0.05] hover:text-slate-200 transition-colors"
          >
            <HelpCircle className="h-4 w-4" />
            <span>API Documentation</span>
          </a>
          <button
            onClick={onOpenTelemetryModal}
            className="flex w-full items-center gap-2.5 rounded-md px-2.5 py-1.5 hover:bg-white/[0.05] hover:text-slate-200 transition-colors"
          >
            <Settings className="h-4 w-4" />
            <span>Engine Settings</span>
          </button>
        </div>
      </div>
    </aside>
  );
};
