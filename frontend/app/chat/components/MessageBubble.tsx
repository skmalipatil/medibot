"use client";

import { COLLECTION_META, ROLE_META, type Role } from "../../lib/constants";
import type { ChatSource } from "../../lib/api";

export interface ChatMessage {
  id: string;
  sender: "user" | "bot";
  text: string;
  sources?: ChatSource[];
  retrievalType?: "hybrid_rag" | "sql_rag" | string;
  role?: Role;
  isNoInfo?: boolean;
  isError?: boolean;
}

const NO_INFO_PATTERN = /i don'?t have that information/i;

export function detectNoInfo(text: string): boolean {
  return NO_INFO_PATTERN.test(text);
}

function RetrievalBadge({ type }: { type?: string }) {
  if (!type) return null;
  if (type === "sql_rag") {
    return (
      <span className="inline-flex items-center gap-1 text-[11px] font-medium px-2 py-0.5 rounded-full bg-purple-100 text-purple-700 border border-purple-200">
        🗄️ SQL RAG
      </span>
    );
  }
  if (type === "hybrid_rag") {
    return (
      <span className="inline-flex items-center gap-1 text-[11px] font-medium px-2 py-0.5 rounded-full bg-blue-100 text-blue-700 border border-blue-200">
        🔎 Hybrid RAG
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 text-[11px] font-medium px-2 py-0.5 rounded-full bg-gray-100 text-gray-600 border border-gray-200">
      {type}
    </span>
  );
}

function SourceChip({ source }: { source: ChatSource }) {
  if (!source) return null;

  if (typeof source === "string") {
    return (
      <span className="inline-flex items-center gap-1 text-xs bg-white border border-gray-200 rounded-full px-2.5 py-1 text-gray-600">
        📄 {source}
      </span>
    );
  }

  const collection = source.collection ? COLLECTION_META[source.collection] : undefined;
  return (
    <span className="inline-flex items-center gap-1 text-xs bg-white border border-gray-200 rounded-full px-2.5 py-1 text-gray-600">
      📄 {source.source_document ?? "Unknown document"}
      {source.section_title && <span className="text-gray-400">· {source.section_title}</span>}
      {collection && <span className="text-gray-400">· {collection.icon}</span>}
    </span>
  );
}

export default function MessageBubble({ message }: { message: ChatMessage }) {
  if (message.sender === "user") {
    return (
      <div className="flex justify-end">
        <div className="max-w-[80%] bg-indigo-600 text-white rounded-2xl rounded-br-sm px-4 py-2.5 text-sm whitespace-pre-wrap break-words">
          {message.text}
        </div>
      </div>
    );
  }

  const validSources = (message.sources ?? []).filter(Boolean);

  return (
    <div className="flex justify-start">
      <div className="max-w-[85%] flex gap-2.5">
        <div className="h-8 w-8 rounded-full bg-indigo-100 flex items-center justify-center text-base shrink-0">
          🤖
        </div>
        <div className="flex flex-col gap-2">
          <div
            className={`rounded-2xl rounded-tl-sm px-4 py-2.5 text-sm whitespace-pre-wrap break-words border ${
              message.isError
                ? "bg-red-50 border-red-200 text-red-700"
                : message.isNoInfo
                ? "bg-amber-50 border-amber-200 text-amber-900"
                : "bg-white border-gray-200 text-gray-800"
            }`}
          >
            {message.isNoInfo && !message.isError && (
              <p className="font-medium text-amber-800 mb-1">⚠️ No accessible information found</p>
            )}
            {message.text}
            {message.isNoInfo && !message.isError && message.role && (
              <p className="text-xs text-amber-700 mt-2">
                MediBot only searched the collections {ROLE_META[message.role].label.toLowerCase()}s
                can access. If you expected an answer from a restricted collection (billing, clinical,
                etc.), that&apos;s RBAC working as intended — not a bug.
              </p>
            )}
          </div>

          {!message.isError && (message.retrievalType || validSources.length > 0) && (
            <div className="flex flex-wrap items-center gap-1.5">
              <RetrievalBadge type={message.retrievalType} />
              {validSources.map((s, i) => (
                <SourceChip key={i} source={s} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
