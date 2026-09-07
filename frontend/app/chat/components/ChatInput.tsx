"use client";

import { useRef } from "react";

interface ChatInputProps {
  value: string;
  onChange: (v: string) => void;
  onSend: () => void;
  disabled?: boolean;
}

export default function ChatInput({ value, onChange, onSend, disabled }: ChatInputProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (value.trim() && !disabled) onSend();
    }
  };

  return (
    <div className="border-t border-gray-200 bg-white p-3 md:p-4">
      <div className="flex items-end gap-2 max-w-3xl mx-auto">
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={1}
          placeholder="Ask MediBot a question…"
          disabled={disabled}
          className="flex-1 resize-none max-h-32 border border-gray-300 rounded-xl px-4 py-2.5 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-400 disabled:bg-gray-50"
        />
        <button
          onClick={onSend}
          disabled={disabled || !value.trim()}
          className="shrink-0 bg-indigo-600 text-white rounded-xl px-4 py-2.5 text-sm font-medium hover:bg-indigo-700 disabled:opacity-40 transition"
        >
          Send
        </button>
      </div>
      <p className="text-[11px] text-gray-400 text-center mt-2">
        MediBot answers only from documents your role can access. Enter to send, Shift+Enter for a new line.
      </p>
    </div>
  );
}
