"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { login, ApiError } from "./lib/api";
import { saveSession, loadSession } from "./lib/session";
import { DEMO_USERS, ROLE_META } from "./lib/constants";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // already logged in? skip straight to the chat.
  useEffect(() => {
    if (loadSession()) router.replace("/chat");
  }, [router]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const data = await login(username, password);
      saveSession({ token: data.token, role: data.role, username });
      router.push("/chat");
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        setError("Invalid username or password.");
      } else if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Something went wrong. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  const fillDemo = (user: (typeof DEMO_USERS)[number]) => {
    setUsername(user.username);
    setPassword(user.password);
    setError("");
  };

  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-md p-8">
        <div className="text-center mb-8">
          <div className="text-5xl mb-3">🏥</div>
          <h1 className="text-3xl font-bold text-gray-800">MediBot</h1>
          <p className="text-gray-500 mt-1">MediAssist Health Network</p>
          <p className="text-xs text-gray-400 mt-1">Role-based clinical knowledge assistant</p>
        </div>

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-4 py-2 text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-400"
              placeholder="Enter username"
              autoComplete="username"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-4 py-2 text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-400"
              placeholder="Enter password"
              autoComplete="current-password"
              required
            />
          </div>

          {error && (
            <p className="text-red-600 text-sm bg-red-50 border border-red-200 rounded-lg px-3 py-2">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 text-white py-2 rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-50 transition"
          >
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>

        <div className="mt-6">
          <p className="text-xs text-gray-400 text-center mb-3">— Demo accounts (click to fill) —</p>
          <div className="space-y-2">
            {DEMO_USERS.map((user) => {
              const meta = ROLE_META[user.role];
              return (
                <button
                  key={user.username}
                  type="button"
                  onClick={() => fillDemo(user)}
                  className="w-full flex items-center justify-between text-left px-3 py-2 rounded-lg bg-gray-50 hover:bg-indigo-50 border border-gray-200 hover:border-indigo-300 transition"
                >
                  <span className="flex items-center gap-2">
                    <span>{meta.icon}</span>
                    <span className="text-sm font-medium text-gray-700">{meta.label}</span>
                  </span>
                  <span className="text-xs text-gray-400">{user.username}</span>
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
