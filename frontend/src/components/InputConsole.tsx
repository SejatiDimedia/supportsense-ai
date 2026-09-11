import React, { useState, useRef, useEffect } from 'react';
import { Plus, ArrowUp, AudioWaveform } from 'lucide-react';

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
    <div className="w-full max-w-3xl mx-auto px-4 mt-6">
      <div className="rounded-2xl border border-slate-200/90 bg-white p-3.5 shadow-sm transition-all focus-within:border-slate-400 focus-within:shadow-md">
        <textarea
          ref={textareaRef}
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask Anything..."
          rows={2}
          disabled={isLoading || disabled}
          className="w-full resize-none bg-transparent px-2 text-sm text-slate-800 placeholder-slate-400 focus:outline-none disabled:opacity-50"
        />

        <div className="mt-2 flex items-center justify-between pt-1 border-t border-slate-100">
          {/* Left Plus Action Button */}
          <button
            type="button"
            title="Attach or select preset query"
            className="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-100 text-slate-700 hover:bg-slate-200 transition-colors"
          >
            <Plus className="h-4 w-4" />
          </button>

          {/* Right Action Icons: Audio & Upward Submit Arrow (Matching Reference) */}
          <div className="flex items-center gap-2">
            <button
              type="button"
              title="Voice prompt feature"
              className="flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors"
            >
              <AudioWaveform className="h-4 w-4" />
            </button>

            <button
              onClick={handleSend}
              disabled={!inputText.trim() || isLoading || disabled}
              className="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-950 text-white transition-all hover:bg-slate-800 disabled:opacity-20 disabled:hover:bg-slate-950"
              title="Send inquiry"
            >
              <ArrowUp className="h-4 w-4 stroke-[2.5]" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
