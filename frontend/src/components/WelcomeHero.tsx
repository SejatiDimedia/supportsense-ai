import React from 'react';

export const WelcomeHero: React.FC = () => {
  return (
    <div className="text-center pt-8 pb-4">
      <h1 className="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
        Hello, Support Specialist
      </h1>
      <p className="mt-2 text-2xl font-light text-slate-400 sm:text-3xl">
        Let's make customer resolution effortless.
      </p>
      <p className="mt-3 text-xs text-slate-400 max-w-md mx-auto">
        Your personal AI assistant for orders, shipping tracking, warranty, and return policies.
      </p>
    </div>
  );
};
