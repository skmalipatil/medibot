"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { chat, getCollections, getHealth, ApiError, type HealthResponse } from "../lib/api";
import { clearSession, loadSession, type Session } from "../lib/session";
import { ROLE_META } from "../lib/constants";
import Sidebar from "./components/Sidebar";
import MessageBubble, { detectNoInfo, type ChatMessage } from "./components/MessageBubble";
import ChatInput from "./components/ChatInput";

let idCounter = 0;
const nextId = () => `${Date.now()}-${idCounter++}`;

export default function ChatPage() {
  const router = useRouter();
  const [session, setSession] = useState<Session | null | undefined>(undefined); // undefined = not checked yet
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [collections, setCollections] = useState<string[]>([]);
  const [collectionsLoading, setCollectionsLoading] = useState(true);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  // auth gate
  useEffect(() => {
    const s = loadSession();
    if (!s) {
      router.replace("/");
      return;
    }
    setSession(s);
  }, [router]);

  // load accessible collections + backend health once we know the role
  useEffect(() => {
    if (!session) return;
    let cancelled = false;

    setCollectionsLoading(true);
    getCollections(session.role)
      .then((res) => {
        if (!cancelled) setCollections(res.collections);
      })
      .catch(() => {
        if (!cancelled) setCollections([]);
      })
      .finally(() => {
        if (!cancelled) setCollectionsLoading(false);
      });

    getHealth()
      .then((res) => !cancelled && setHealth(res))
      .catch(() => !cancelled && setHealth(null));

    return () => {
      cancelled = true;
    };
  }, [session]);

  // auto-scroll on new messages
  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, sending]);

  const handleLogout = useCallback(() => {
    clearSession();
    router.replace("/");
  }, [router]);

  const send = useCallback(
    async (text: string) => {
      if (!session || !text.trim() || sending) return;

      const userMsg: ChatMessage = { id: nextId(), sender: "user", text: text.trim() };
      setMessages((prev) => [...prev, userMsg]);
      setInput("");
      setSending(true);

      try {
        const res = await chat(text.trim(), session.role, session.token);
        const botMsg: ChatMessage = {
          id: nextId(),
          sender: "bot",
          text: res.answer,
          sources: res.sources,
          retrievalType: res.retrieval_type,
          role: session.role,
          isNoInfo: detectNoInfo(res.answer),
        };
        setMessages((prev) => [...prev, botMsg]);
      } catch (err) {
        const message =
          err instanceof ApiError ? err.message : "Something went wrong. Please try again.";
        setMessages((prev) => [
          ...prev,
          { id: nextId(), sender: "bot", text: message, isError: true },
        ]);
      } finally {
        setSending(false);
      }
    },
    [session, sending]
  );

  if (session === undefined) {
    return (
      <div className="min-h-screen flex items-center justify-center text-gray-400 text-sm">
        Loading…
      </div>
    );
  }
  if (!session) return null; // redirecting

  const meta = ROLE_META[session.role];

  return (
    <div className="h-screen w-full flex bg-gray-50 overflow-hidden">
      <Sidebar
        username={session.username}
        role={session.role}
        collections={collections}
        collectionsLoading={collectionsLoading}
        health={health}
        onPromptClick={(text) => send(text)}
        onLogout={handleLogout}
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      <div className="flex-1 flex flex-col min-w-0">
        {/* header */}
        <header className="flex items-center gap-3 border-b border-gray-200 bg-white px-4 py-3">
          <button
            className="md:hidden text-gray-500 hover:text-gray-700"
            onClick={() => setSidebarOpen(true)}
            aria-label="Open sidebar"
          >
            ☰
          </button>
          <div className="flex-1 min-w-0">
            <p className="font-semibold text-gray-800 truncate">MediBot Assistant</p>
            <p className="text-xs text-gray-400 truncate">
              Ask about clinical protocols, policies, billing, or equipment
            </p>
          </div>
          <span
            className={`hidden sm:inline-flex items-center gap-1 text-xs font-medium px-2.5 py-1 rounded-full border ${meta.color}`}
          >
            <span>{meta.icon}</span>
            {meta.label}
          </span>
        </header>

        {/* messages */}
        <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 py-6">
          <div className="max-w-3xl mx-auto flex flex-col gap-4">
            {messages.length === 0 && (
              <div className="text-center py-16">
                <div className="text-4xl mb-3">{meta.icon}</div>
                <p className="text-gray-700 font-medium">
                  Welcome, {session.username.split(".")[0]} ({meta.label})
                </p>
                <p className="text-sm text-gray-400 mt-1 max-w-sm mx-auto">
                  Ask a question, or try one of the suggested prompts in the sidebar — including
                  the RBAC test prompt marked 🧪.
                </p>
              </div>
            )}

            {messages.map((m) => (
              <MessageBubble key={m.id} message={m} />
            ))}

            {sending && (
              <div className="flex justify-start">
                <div className="flex gap-2.5">
                  <div className="h-8 w-8 rounded-full bg-indigo-100 flex items-center justify-center text-base shrink-0">
                    🤖
                  </div>
                  <div className="bg-white border border-gray-200 rounded-2xl rounded-tl-sm px-4 py-3 flex gap-1 items-center">
                    <span className="h-1.5 w-1.5 rounded-full bg-gray-400 animate-bounce [animation-delay:-0.3s]" />
                    <span className="h-1.5 w-1.5 rounded-full bg-gray-400 animate-bounce [animation-delay:-0.15s]" />
                    <span className="h-1.5 w-1.5 rounded-full bg-gray-400 animate-bounce" />
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        <ChatInput value={input} onChange={setInput} onSend={() => send(input)} disabled={sending} />
      </div>
    </div>
  );
}
