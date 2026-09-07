// Tiny localStorage-backed session helper. All access is guarded for SSR
// (Next.js renders this on the server first, where `window` doesn't exist).

import type { Role } from "./constants";

export interface Session {
  token: string;
  role: Role;
  username: string;
}

const KEYS = { token: "medibot_token", role: "medibot_role", username: "medibot_username" } as const;

export function saveSession(session: Session) {
  if (typeof window === "undefined") return;
  localStorage.setItem(KEYS.token, session.token);
  localStorage.setItem(KEYS.role, session.role);
  localStorage.setItem(KEYS.username, session.username);
}

export function loadSession(): Session | null {
  if (typeof window === "undefined") return null;
  const token = localStorage.getItem(KEYS.token);
  const role = localStorage.getItem(KEYS.role) as Role | null;
  const username = localStorage.getItem(KEYS.username);
  if (!token || !role || !username) return null;
  return { token, role, username };
}

export function clearSession() {
  if (typeof window === "undefined") return;
  localStorage.removeItem(KEYS.token);
  localStorage.removeItem(KEYS.role);
  localStorage.removeItem(KEYS.username);
}
