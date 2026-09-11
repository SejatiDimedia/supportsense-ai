import React from 'react';
import { Package, BookOpen, ShieldCheck, ArrowRight } from 'lucide-react';

interface ScenarioCardsProps {
  onSelectScenario: (prompt: string) => void;
  disabled?: boolean;
}

export const ScenarioCards: React.FC<ScenarioCardsProps> = ({
  onSelectScenario,
  disabled,
}) => {
  const cards = [
    {
      id: 'order_tracking',
      title: 'Order & Delivery Tracking',
      description: 'Look up real-time delivery status, FedEx/DHL tracking, transit delays, and assigned agents.',
      prompt: 'Where is my order #4521?',
      icon: Package,
    },
    {
      id: 'refund_policy',
      title: '30-Day Refund Policy',
      description: 'Verify return eligibility, warehouse inspection criteria, and banking transfer timelines.',
      prompt: 'What is your refund policy and eligibility criteria?',
      icon: BookOpen,
    },
    {
      id: 'warranty_claims',
      title: 'Hardware Warranty & RMA',
      description: 'Review 24-month manufacturer coverage, defective item protocols, and prepaid RMA return shipping.',
      prompt: 'How long is the warranty for electronics and how do I file an RMA claim?',
      icon: ShieldCheck,
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-4xl mx-auto px-4 mt-6">
      {cards.map((card) => {
        const IconComponent = card.icon;
        return (
          <button
            key={card.id}
            onClick={() => onSelectScenario(card.prompt)}
            disabled={disabled}
            className="group flex flex-col text-left rounded-2xl border border-slate-200/90 bg-white p-5 shadow-sm transition-all hover:border-slate-300 hover:shadow-md disabled:opacity-40"
          >
            {/* Vibrant Lime Square Icon Box (Matching Reference) */}
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-lime-400 text-black font-bold mb-3.5 transition-transform group-hover:scale-105">
              <IconComponent className="h-4 w-4" />
            </div>

            <div className="flex items-center justify-between w-full">
              <h3 className="text-sm font-bold text-slate-900 tracking-tight">
                {card.title}
              </h3>
              <ArrowRight className="h-3.5 w-3.5 text-slate-400 opacity-0 -translate-x-1 group-hover:opacity-100 group-hover:translate-x-0 transition-all text-slate-900" />
            </div>

            <p className="mt-1.5 text-xs text-slate-500 leading-relaxed">
              {card.description}
            </p>
          </button>
        );
      })}
    </div>
  );
};
