import { Search } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router';

import { fetchEvidenceSearch } from '../api/client';

const suggestedSearches = [
  'Rising CA 19-9',
  'KRAS mutation',
  'Possible progression',
  'Missing labs',
  'FOLFIRINOX',
  'Fatigue',
];

type Hit = {
  patient: { id: number; name: string; mrn: string };
  source_type?: string;
  matched_snippet?: string;
  extracted_value?: string;
  why_matched?: string;
  confidence?: number;
};

export function SearchScreen() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const patientFilter = searchParams.get('patient') ?? '';
  const urlQ = searchParams.get('q') ?? '';

  const [query, setQuery] = useState(urlQ);
  const [debounced, setDebounced] = useState(urlQ);

  useEffect(() => {
    setQuery(urlQ);
    setDebounced(urlQ);
  }, [urlQ]);

  useEffect(() => {
    const t = window.setTimeout(() => setDebounced(query), 300);
    return () => window.clearTimeout(t);
  }, [query]);

  const [results, setResults] = useState<Hit[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const q = debounced.trim();
    if (!q) {
      setResults([]);
      return;
    }
    let cancelled = false;
    setLoading(true);
    fetchEvidenceSearch(q, patientFilter || undefined)
      .then((res) => {
        if (!cancelled) {
          setResults(res.results as Hit[]);
          setError(null);
        }
      })
      .catch((e: Error) => {
        if (!cancelled) setError(e.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [debounced, patientFilter]);

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-2xl p-5 border border-[#E2E8F0]">
        <div className="relative mb-4">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[#94A3B8]" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search evidence across reports, notes, labs, and biomarkers…"
            className="pl-12 pr-4 py-3 w-full rounded-lg bg-[#F8FAFC] border border-[#E2E8F0] focus:outline-none focus:ring-2 focus:ring-[#2563EB] focus:border-transparent"
          />
        </div>

        <div>
          <p className="text-xs uppercase text-[#94A3B8] mb-2 font-medium">Suggested</p>
          <div className="flex flex-wrap gap-2">
            {suggestedSearches.map((search) => (
              <button
                key={search}
                type="button"
                onClick={() => setQuery(search)}
                className="px-3 py-1.5 rounded-lg bg-[#F1F5F9] text-[#64748B] text-sm hover:bg-[#E2E8F0] hover:text-[#0F172A] transition-colors"
              >
                {search}
              </button>
            ))}
          </div>
        </div>
      </div>

      {patientFilter && (
        <p className="text-sm text-[#64748B]">
          Scoped to patient id <span className="font-medium text-[#0F172A]">{patientFilter}</span> (from workspace
          link).
        </p>
      )}

      {error && (
        <p className="text-sm text-red-600 bg-red-50 border border-red-100 rounded-lg px-3 py-2">{error}</p>
      )}

      <div className="grid grid-cols-4 gap-6">
        <div className="bg-white rounded-lg p-5 border border-[#E2E8F0]">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-[#0F172A] text-sm">Filters</h3>
            <span className="text-xs text-[#94A3B8]">Client-side filters are not wired yet.</span>
          </div>
        </div>

        <div className="col-span-3 space-y-4">
          <div className="flex items-center justify-between">
            <p className="text-sm text-[#64748B]">
              {loading
                ? 'Searching…'
                : `Found ${results.length} evidence match${results.length === 1 ? '' : 'es'}${debounced.trim() ? ` for “${debounced.trim()}”` : ''}`}
            </p>
          </div>

          {!debounced.trim() && (
            <p className="text-sm text-[#64748B]">Type a query or choose a suggested search.</p>
          )}

          {results.map((result, i) => (
            <div
              key={`${result.patient.id}-${i}`}
              className="bg-white rounded-2xl p-5 border border-[#E2E8F0] hover:border-[#2563EB] transition-all"
            >
              {result.matched_snippet && (
                <div className="mb-3 p-3 bg-[#F8FAFC] rounded-xl">
                  <p className="text-xs uppercase tracking-wide text-[#94A3B8] mb-1 font-medium">Matched snippet</p>
                  <p className="text-sm text-[#0F172A] leading-relaxed">{result.matched_snippet}</p>
                </div>
              )}

              <div className="mb-3 pb-3 border-b border-[#E2E8F0]">
                <p className="text-sm font-semibold text-[#0F172A] mb-0.5">{result.patient.name}</p>
                <p className="text-xs text-[#64748B]">MRN {result.patient.mrn}</p>
              </div>

              <div className="mb-3">
                <p className="text-xs text-[#64748B] mb-1">
                  Source type:{' '}
                  <span className="font-medium text-[#0F172A]">{result.source_type ?? 'Unknown'}</span>
                </p>
              </div>

              <div className="grid grid-cols-2 gap-2 mb-3">
                {result.extracted_value && (
                  <div className="p-2 bg-blue-50 rounded-lg border border-blue-100">
                    <p className="text-xs uppercase text-[#94A3B8] mb-0.5 font-medium">Extracted Value</p>
                    <p className="text-xs font-medium text-[#0F172A]">{result.extracted_value}</p>
                  </div>
                )}
                {result.why_matched && (
                  <div className="p-2 bg-[#F8FAFC] rounded-lg border border-[#E2E8F0]">
                    <p className="text-xs uppercase text-[#94A3B8] mb-0.5 font-medium">Why This Matched</p>
                    <p className="text-xs text-[#0F172A]">{result.why_matched}</p>
                  </div>
                )}
              </div>

              <div className="flex items-center justify-between">
                <span className="text-xs text-[#64748B]">
                  Confidence:{' '}
                  <span className="font-medium text-[#0F172A]">
                    {result.confidence != null ? `${Math.round(Number(result.confidence) * 100)}%` : '—'}
                  </span>
                </span>
                <button
                  type="button"
                  onClick={() => navigate(`/patient/${result.patient.id}`)}
                  className="px-3 py-1.5 bg-[#2563EB] text-white rounded-xl text-sm font-medium hover:bg-[#1d4ed8] transition-colors"
                >
                  Open Workspace
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
