"use client";

import { COLLECTION_META, ROLE_META, SUGGESTED_PROMPTS, type Role } from "../../lib/constants";
import type { HealthResponse } from "../../lib/api";

interface SidebarProps {
  username: string;
  role: Role;
  collections: string[];
  collectionsLoading: boolean;
  health: HealthResponse | null;
  onPromptClick: (text: string) => void;
  onLogout: () => void;
  open: boolean;
  onClose: () => void;
}

export default function Sidebar({
  username,
  role,
  collections,
  collectionsLoading,
  health,
  onPromptClick,
  onLogout,
  open,
  onClose,
}: SidebarProps) {
  const meta = ROLE_META[role];
  const allCollections = Object.keys(COLLECTION_META);
  const deniedCollections = allCollections.filter((c) => !collections.includes(c));
  const prompts = SUGGESTED_PROMPTS[role] ?? [];

  return (
    <>
      {/* mobile overlay */}
      {open && (
        <div
          className="fixed inset-0 bg-black/30 z-20 md:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      <aside
        className={`fixed md:static inset-y-0 left-0 z-30 w-72 shrink-0 bg-white border-r border-gray-200 flex flex-col transform transition-transform md:transform-none ${
          open ? "translate-x-0" : "-translate-x-full md:translate-x-0"
        }`}
      >
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center gap-2">
            <span className="text-2xl">🏥</span>
            <div>
              <p className="font-semibold text-gray-800 leading-tight">MediBot</p>
              <p className="text-xs text-gray-400 leading-tight">MediAssist Health Network</p>
            </div>
          </div>
        </div>

        {/* user / role card */}
        <div className="p-4 border-b border-gray-200">
          <p className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-2">
            Signed in as
          </p>
          <p className="text-sm font-medium text-gray-800 truncate">{username}</p>
          <span
            className={`mt-2 inline-flex items-center gap-1 text-xs font-medium px-2 py-1 rounded-full border ${meta.color}`}
          >
            <span>{meta.icon}</span>
            {meta.label}
          </span>
        </div>

        {/* accessible collections */}
        <div className="p-4 border-b border-gray-200">
          <p className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-2">
            Accessible collections
          </p>
          {collectionsLoading ? (
            <p className="text-xs text-gray-400">Loading…</p>
          ) : (
            <ul className="space-y-1.5">
              {collections.map((c) => {
                const cm = COLLECTION_META[c] ?? { label: c, icon: "📁" };
                return (
                  <li
                    key={c}
                    className="flex items-center gap-2 text-sm text-gray-700 bg-emerald-50 border border-emerald-200 rounded-lg px-2.5 py-1.5"
                  >
                    <span>{cm.icon}</span>
                    <span className="truncate">{cm.label}</span>
                    <span className="ml-auto text-emerald-600">✓</span>
                  </li>
                );
              })}
              {deniedCollections.map((c) => {
                const cm = COLLECTION_META[c] ?? { label: c, icon: "📁" };
                return (
                  <li
                    key={c}
                    className="flex items-center gap-2 text-sm text-gray-400 bg-gray-50 border border-gray-200 rounded-lg px-2.5 py-1.5"
                    title="Not accessible to your role"
                  >
                    <span className="opacity-50">{cm.icon}</span>
                    <span className="truncate line-through decoration-gray-300">{cm.label}</span>
                    <span className="ml-auto">🔒</span>
                  </li>
                );
              })}
            </ul>
          )}
        </div>

        {/* suggested prompts */}
        {prompts.length > 0 && (
          <div className="p-4 border-b border-gray-200 overflow-y-auto">
            <p className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-2">
              Try asking
            </p>
            <div className="space-y-2">
              {prompts.map((p) => (
                <button
                  key={p.text}
                  onClick={() => onPromptClick(p.text)}
                  className={`w-full text-left text-xs rounded-lg px-2.5 py-2 border transition ${
                    p.adversarial
                      ? "bg-red-50 border-red-200 text-red-700 hover:bg-red-100"
                      : "bg-gray-50 border-gray-200 text-gray-600 hover:bg-indigo-50 hover:border-indigo-300"
                  }`}
                >
                  {p.adversarial && <span className="mr-1">🧪</span>}
                  {p.text}
                </button>
              ))}
            </div>
            <p className="text-[11px] text-gray-400 mt-2">
              🧪 = adversarial RBAC test — asks for a collection outside this role&apos;s access.
            </p>
          </div>
        )}

        <div className="mt-auto p-4 space-y-3">
          <div className="flex items-center gap-2 text-xs text-gray-400">
            <span
              className={`h-2 w-2 rounded-full ${
                health?.status === "ok" ? "bg-emerald-500" : "bg-red-400"
              }`}
            />
            <span>
              Backend {health?.status === "ok" ? "connected" : "unreachable"}
              {health && ` · Qdrant ${health.qdrant} · DB ${health.database}`}
            </span>
          </div>
          <button
            onClick={onLogout}
            className="w-full text-sm font-medium text-gray-600 hover:text-red-600 border border-gray-200 hover:border-red-300 rounded-lg py-2 transition"
          >
            Log out
          </button>
        </div>
      </aside>
    </>
  );
}
