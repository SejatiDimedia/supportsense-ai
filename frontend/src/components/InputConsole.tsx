import React, { useState, useRef, useEffect } from 'react';
import { Send, CornerDownLeft } from 'lucide-react';

interface InputConsoleProps {
  onSendMessage: (text: string) => void;
  isLoading: boolean;
  disabled?: boolean;
}

export const InputConsole: React.FC<InputConsoleProps> = ({
  onSendMessage,
  isLoading,
  disabled,
}) => {
  const [inputText, setInputText] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (!isLoading && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [isLoading]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSend = () => {
    if (!inputText.trim() || isLoading || disabled) return;
    onSendMessage(inputText.trim());
    setInputText('');
  };

  return (
    <div className="border-t border-white/[0.08] bg-[#0A0E17] p-4">
      <div className="mx-auto max-w-7xl">
        <div className="relative rounded-xl border border-white/[0.1] bg-[#0F1522] focus-within:border-emerald-500/50 transition-colors">
          <textarea
            ref={textareaRef}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your inquiry (e.g. 'Where is my order #4521?' or 'What is the return policy?')..."
            rows={2}
            disabled={isLoading || disabled}
            className="w-full resize-none bg-transparent px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none disabled:opacity-50"
          />

          <div className="flex items-center justify-between border-t border-white/[0.04] px-3.5 py-2">
            <div className="flex items-center gap-2 text-[11px] text-slate-500 font-mono">
              <span className="flex items-center gap-1 rounded bg-white/[0.04] px-1.5 py-0.5 border border-white/[0.06]">
                Enter <CornerDownLeft className="h-3 w-3 inline" />
              </span>
              <span>to send</span>
              <span className="text-slate-600">·</span>
              <span className="flex items-center gap-1 rounded bg-white/[0.04] px-1.5 py-0.5 border border-white/[0.06]">
                Shift+Enter
              </span>
              <span>for newline</span>
            </div>

            <button
              onClick={handleSend}
              disabled={!inputText.trim() || isLoading || disabled}
              className="flex items-center gap-1.5 rounded-lg bg-emerald-500 px-3 py-1.5 text-xs font-semibold text-emerald-950 transition-all hover:bg-emerald-400 disabled:opacity-30 disabled:hover:bg-emerald-500"
            >
              <span>{isLoading ? 'Processing...' : 'Send Message'}</span>
              <Send className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
