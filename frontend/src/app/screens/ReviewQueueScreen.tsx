import { Search, FileText, Upload, Presentation } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router';

import { fetchReviewQueue } from '../api/client';
import type { ReviewQueueResponse } from '../api/client';

function formatQueueTimestamp(iso: string): string {
  try {
    return new Date(iso).toLocaleString(undefined, {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    });
  } catch {
    return iso;
  }
}

function reviewStatusLabel(status?: string): string {
  switch (status) {
    case 'needs-review':
      return 'Needs review';
    case 'watch':
      return 'Watch';
    case 'stable':
      return 'Stable';
    default:
      return status ? status.replace(/-/g, ' ') : 'Unknown';
  }
}

export function ReviewQueueScreen() {
  const navigate = useNavigate();
  const [panelQuery, setPanelQuery] = useState('');
  const [data, setData] = useState<ReviewQueueResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchReviewQueue()
      .then((d) => {
        if (!cancelled) setData(d);
      })
      .catch((e: Error) => {
        if (!cancelled) setError(e.message);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const metrics = data?.metrics;

  const runPanelSearch = () => {
    const q = panelQuery.trim();
    if (!q) return;
    navigate(`/search?q=${encodeURIComponent(q)}`);
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg border border-[#E2E8F0] p-5">
        <div className="flex items-center gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[#94A3B8]" />
            <input
              type="text"
              value={panelQuery}
              onChange={(e) => setPanelQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') runPanelSearch();
              }}
              placeholder="Ask across your panel: rising CA 19-9, missing labs, KRAS mutation…"
              className="pl-12 pr-4 py-3 w-full rounded-lg bg-[#F8FAFC] border border-[#E2E8F0] text-sm focus:outline-none focus:ring-2 focus:ring-[#2563EB] focus:border-transparent"
            />
          </div>
          <button
            type="button"
            onClick={runPanelSearch}
            className="px-3 py-2 text-sm border border-[#E2E8F0] rounded-xl hover:bg-[#F8FAFC] transition-colors whitespace-nowrap"
          >
            Search
          </button>
          <button
            type="button"
            onClick={() => navigate('/search?q=' + encodeURIComponent('CA 19-9'))}
            className="px-3 py-2 text-sm border border-[#E2E8F0] rounded-xl hover:bg-[#F8FAFC] transition-colors whitespace-nowrap"
          >
            New Evidence
          </button>
          <button
            type="button"
            onClick={() => navigate('/search?q=' + encodeURIComponent('labs'))}
            className="px-3 py-2 text-sm border border-[#E2E8F0] rounded-xl hover:bg-[#F8FAFC] transition-colors whitespace-nowrap"
          >
            Missing Data
          </button>
          <button
            type="button"
            onClick={() => navigate('/queue')}
            className="px-3 py-2 text-sm border border-[#E2E8F0] rounded-xl hover:bg-[#F8FAFC] transition-colors whitespace-nowrap"
          >
            Needs Confirmation
          </button>
          <button
            type="button"
            onClick={() => navigate('/intake')}
            className="px-3 py-2 text-sm border border-[#E2E8F0] rounded-xl hover:bg-[#F8FAFC] transition-colors whitespace-nowrap"
          >
            Unreviewed Sources
          </button>
        </div>
      </div>

      {error && (
        <p className="text-sm text-red-600 bg-red-50 border border-red-100 rounded-lg px-3 py-2">
          {error}
        </p>
      )}

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2 space-y-4">
          {!data && !error && (
            <p className="text-sm text-[#64748B]">Loading review queue…</p>
          )}
          {data?.patients?.length === 0 && (
            <p className="text-sm text-[#64748B]">No patients currently match the review queue rules.</p>
          )}
          {data?.patients?.map((patient) => (
            <div
              key={patient.id}
              className="bg-white rounded-2xl border border-[#E2E8F0] p-5 hover:border-[#2563EB] transition-colors"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-1">
                    <h3 className="font-semibold text-[#0F172A]">{patient.name}</h3>
                    <span className="text-xs text-[#94A3B8]">MRN {patient.mrn}</span>
                  </div>
                  <p className="text-sm text-[#64748B] mb-2">
                    {patient.diagnosis || '—'} · {patient.stage || '—'} · {patient.treatment || '—'}
                  </p>
                  <p className="text-xs text-[#64748B] mb-2">
                    Last OncoLens chart review:{' '}
                    <span className="font-semibold text-[#475569]">
                      {patient.last_chart_review_at ? formatQueueTimestamp(patient.last_chart_review_at) : '—'}
                    </span>
                  </p>
                  {patient.queue_counts ? (
                    <div className="flex flex-wrap gap-1.5 mb-2">
                      {patient.queue_counts.unreviewed_source_flags > 0 ? (
                        <span className="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-rose-50 text-rose-800 border border-rose-100">
                          Unreviewed flags · {patient.queue_counts.unreviewed_source_flags}
                        </span>
                      ) : null}
                      {patient.queue_counts.unconfirmed_observations > 0 ? (
                        <span className="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-amber-50 text-amber-900 border border-amber-100">
                          Needs confirmation · {patient.queue_counts.unconfirmed_observations}
                        </span>
                      ) : null}
                      {patient.queue_counts.pending_reports > 0 ? (
                        <span className="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-indigo-50 text-indigo-900 border border-indigo-100">
                          Pending parse · {patient.queue_counts.pending_reports}
                        </span>
                      ) : null}
                      {patient.queue_counts.new_since_last_review != null ? (
                        <span className="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-slate-50 text-slate-800 border border-slate-200">
                          New since last review · {patient.queue_counts.new_since_last_review}
                        </span>
                      ) : null}
                    </div>
                  ) : null}
                  <div className="inline-flex">
                    <span className="px-2 py-0.5 bg-amber-50 text-amber-700 text-xs rounded-full font-medium">
                      Review status: {reviewStatusLabel(patient.status)}
                    </span>
                  </div>
                </div>
              </div>

              <div className="mb-4 p-3 bg-amber-50 rounded-xl border border-amber-100">
                <p className="text-xs uppercase tracking-wide text-amber-700 mb-2 font-semibold">
                  Why this chart is in queue
                </p>
                <ul className="space-y-1">
                  {(patient.reasons && patient.reasons.length > 0
                    ? patient.reasons
                    : ['Listed by queue rules']
                  ).map((reason, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-amber-900">
                      <span className="w-1 h-1 rounded-full bg-amber-600 mt-1.5 flex-shrink-0"></span>
                      <span>{reason}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="flex items-center justify-between pt-3 border-t border-[#E2E8F0]">
                <div className="flex items-center gap-2 text-sm flex-wrap">
                  <FileText className="w-4 h-4 text-[#64748B] flex-shrink-0" />
                  <span className="text-[#64748B]">Newest report:</span>
                  <span className="font-medium text-[#0F172A]">
                    {patient.newestEvidence?.type ?? '—'}
                  </span>
                  {patient.newestEvidence?.title && (
                    <span className="text-[#94A3B8] truncate max-w-[min(280px,50vw)]">
                      · {patient.newestEvidence.title}
                    </span>
                  )}
                </div>
                <button
                  type="button"
                  onClick={() => navigate(`/patient/${patient.id}`)}
                  className="px-4 py-2 bg-[#2563EB] text-white rounded-xl text-sm font-medium hover:bg-[#1d4ed8] transition-colors flex-shrink-0"
                >
                  Open Workspace
                </button>
              </div>
            </div>
          ))}
        </div>

        <div className="space-y-3">
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-4">
            <h3 className="font-semibold text-[#0F172A] mb-3 text-sm">Today&apos;s Evidence Intake</h3>
            <div className="space-y-2.5">
              <div className="flex items-center justify-between">
                <span className="text-sm text-[#64748B]">New reports parsed</span>
                <span className="text-lg font-semibold text-[#0F172A]">
                  {metrics?.new_reports_count ?? '—'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-[#64748B]">Need confirmation</span>
                <span className="text-lg font-semibold text-[#F59E0B]">
                  {metrics?.needs_confirmation_count ?? '—'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-[#64748B]">Patients with new evidence</span>
                <span className="text-lg font-semibold text-[#0F172A]">
                  {metrics?.patients_with_new_evidence_count ?? '—'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-[#64748B]">Patients on review queue</span>
                <span className="text-lg font-semibold text-[#0F172A]">
                  {metrics?.patients_pending_chart_review ?? '—'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-[#64748B]">Missing recent labs</span>
                <span className="text-lg font-semibold text-[#DC2626]">
                  {metrics?.missing_recent_labs_count ?? '—'}
                </span>
              </div>
            </div>
          </div>

          <div className="bg-[#F8FAFC] rounded-2xl border border-[#E2E8F0] p-4">
            <p className="text-xs uppercase tracking-wide text-[#94A3B8] mb-2 font-medium">Review Philosophy</p>
            <p className="text-sm text-[#64748B] leading-relaxed">
              OncoLens surfaces source-backed observations. It does not diagnose, prescribe, or replace clinician
              judgment.
            </p>
          </div>

          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-4">
            <p className="text-xs uppercase tracking-wide text-[#94A3B8] mb-2 font-medium">Quick Actions</p>
            <div className="space-y-1">
              <button
                type="button"
                onClick={() => navigate('/intake')}
                className="w-full px-3 py-2 text-left text-sm text-[#0F172A] hover:bg-[#F8FAFC] rounded-lg transition-colors flex items-center gap-2"
              >
                <Upload className="w-4 h-4 text-[#64748B]" />
                Upload report
              </button>
              <button
                type="button"
                onClick={() => navigate('/search')}
                className="w-full px-3 py-2 text-left text-sm text-[#0F172A] hover:bg-[#F8FAFC] rounded-lg transition-colors flex items-center gap-2"
              >
                <Search className="w-4 h-4 text-[#64748B]" />
                Search evidence
              </button>
              <button
                type="button"
                onClick={() => navigate('/tumor-board')}
                className="w-full px-3 py-2 text-left text-sm text-[#0F172A] hover:bg-[#F8FAFC] rounded-lg transition-colors flex items-center gap-2"
              >
                <Presentation className="w-4 h-4 text-[#64748B]" />
                Generate tumor board brief
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
