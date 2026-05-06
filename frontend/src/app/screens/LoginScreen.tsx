import { useState } from 'react';
import { useNavigate } from 'react-router';

import { apiLogin } from '../api/client';

export function LoginScreen() {
  const navigate = useNavigate();
  const [username, setUsername] = useState('alex.morgan.demo');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await apiLogin(username.trim(), password);
      navigate('/queue');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Sign in failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      <div className="flex-1 bg-[#F8FAFC] p-16 flex items-center justify-center border-r border-[#E2E8F0]">
        <div className="max-w-md">
          <div className="mb-12">
            <div className="w-12 h-12 rounded-lg bg-[#2563EB] flex items-center justify-center mb-4">
              <div className="w-7 h-7 rounded-full border-2 border-white"></div>
            </div>
            <h1 className="text-3xl font-semibold text-[#0F172A] mb-3">
              Evidence-first chart review for oncology
            </h1>
            <p className="text-lg text-[#64748B] leading-relaxed">
              OncoLens helps oncologists find and verify information across reports, labs, and timelines—faster.
            </p>
          </div>

          <div className="space-y-6">
            <div className="p-4 bg-white rounded-lg border border-[#E2E8F0]">
              <p className="text-sm text-[#0F172A] font-medium mb-1">Source-backed observations</p>
              <p className="text-sm text-[#64748B]">Every insight links to exact report snippets</p>
            </div>
            <div className="p-4 bg-white rounded-lg border border-[#E2E8F0]">
              <p className="text-sm text-[#0F172A] font-medium mb-1">Built for clinician review</p>
              <p className="text-sm text-[#64748B]">No diagnoses, predictions, or treatment recommendations</p>
            </div>
          </div>
        </div>
      </div>

      <div className="flex-1 bg-white p-16 flex items-center justify-center">
        <div className="w-full max-w-md">
          <div className="bg-white rounded-lg p-8 border border-[#E2E8F0]">
            <div className="mb-8">
              <h3 className="text-xl font-semibold text-[#0F172A] mb-2">Sign in</h3>
              <p className="text-sm text-[#64748B]">Access your chart review workspace</p>
            </div>

            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-[#0F172A] mb-2">Username</label>
                <input
                  type="text"
                  autoComplete="username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-lg border border-[#E2E8F0] bg-white text-sm focus:outline-none focus:ring-2 focus:ring-[#2563EB] focus:border-transparent"
                  placeholder="alex.morgan.demo"
                />
                <p className="text-xs text-[#94A3B8] mt-1">
                  Demo users: alex.morgan.demo, jamie.lee.demo, priya.shah.demo (password: password123)
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-[#0F172A] mb-2">Password</label>
                <input
                  type="password"
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-lg border border-[#E2E8F0] bg-white text-sm focus:outline-none focus:ring-2 focus:ring-[#2563EB] focus:border-transparent"
                  placeholder="••••••••"
                />
              </div>

              {error && (
                <p className="text-sm text-red-600 bg-red-50 border border-red-100 rounded-lg px-3 py-2">
                  {error}
                </p>
              )}
              <button
                type="submit"
                disabled={loading}
                className="w-full py-2.5 bg-[#2563EB] text-white rounded-lg font-medium hover:bg-[#1d4ed8] transition-colors mt-6 disabled:opacity-50"
              >
                {loading ? 'Signing in…' : 'Sign in'}
              </button>
            </form>

            <div className="mt-6 pt-6 border-t border-[#E2E8F0]">
              <p className="text-xs text-center text-[#94A3B8]">
                Prototype system. Not for clinical use.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
