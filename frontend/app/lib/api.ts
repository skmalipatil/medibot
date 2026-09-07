// Thin client for the MediBot FastAPI backend.
// Endpoints: POST /login, POST /chat, GET /collections/{role}, GET /health

import type { Role } from "./constants";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") || "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
    });
  } catch {
    throw new ApiError(
      "Cannot reach the MediBot backend. Is it running on " + API_BASE_URL + "?",
      0
    );
  }

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      // response wasn't JSON — keep statusText
    }
    throw new ApiError(detail, res.status);
  }

  return res.json() as Promise<T>;
}

// ── /login ──────────────────────────────────────────────────────────────
export interface LoginResponse {
  token: string;
  role: Role;
}

export function login(username: string, password: string) {
  return request<LoginResponse>("/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
}

// ── /chat ───────────────────────────────────────────────────────────────
// The backend's hybrid_rag chain currently returns each source as a plain
// filename string (doc.metadata.get("source")); the SQL RAG path returns an
// empty sources list. Model it loosely so richer {source_document,
// section_title, collection} objects are also handled if the backend
// evolves toward the full metadata schema.
export type ChatSource =
  | string
  | {
      source_document?: string;
      section_title?: string;
      collection?: string;
    }
  | null;

export interface ChatResponse {
  answer: string;
  sources: ChatSource[];
  retrieval_type: "hybrid_rag" | "sql_rag" | string;
  role: string;
}

export function chat(question: string, role: string, token?: string | null) {
  return request<ChatResponse>("/chat", {
    method: "POST",
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
    body: JSON.stringify({ question, role }),
  });
}

// ── /collections/{role} ────────────────────────────────────────────────
export interface CollectionsResponse {
  role: string;
  collections: string[];
}

export function getCollections(role: string) {
  return request<CollectionsResponse>(`/collections/${encodeURIComponent(role)}`);
}

// ── /health ─────────────────────────────────────────────────────────────
export interface HealthResponse {
  status: string;
  qdrant: "connected" | "disconnected" | string;
  database: "connected" | "disconnected" | string;
}

export function getHealth() {
  return request<HealthResponse>("/health");
}
