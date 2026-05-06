import { Search, Filter, ArrowUpDown } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router';

import { fetchPatients } from '../api/client';
import type { PatientsApiResponse } from '../api/client';
import { StatusBadge } from '../components/StatusBadge';

type RowStatus = 'stable' | 'watch' | 'needs-review';

function statusForBadge(s?: string): RowStatus {
  if (s === 'stable' || s === 'watch' || s === 'needs-review') return s;
  if (s === 'needs_review') return 'needs-review';
  return 'stable';
}

function formatUpdated(iso?: string): string {
  if (!iso) return '—';
  try {
    const d = new Date(iso);
    return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
  } catch {
    return iso.slice(0, 10);
  }
}

export function PatientsScreen() {
  const navigate = useNavigate();
  const [q, setQ] = useState('');
  const [debounced, setDebounced] = useState('');
  const [data, setData] = useState<PatientsApiResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const t = window.setTimeout(() => setDebounced(q.trim()), 350);
    return () => window.clearTimeout(t);
  }, [q]);

  useEffect(() => {
    let cancelled = false;
    fetchPatients(debounced || undefined)
      .then((d) => {
        if (!cancelled) {
          setData(d);
          setError(null);
        }
      })
      .catch((e: Error) => {
        if (!cancelled) setError(e.message);
      });
    return () => {
      cancelled = true;
    };
  }, [debounced]);

  const patients = data?.patients ?? [];

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-2xl p-5 border border-[#E2E8F0]">
        <div className="flex items-center gap-4 mb-4">
          <div className="relative flex-1">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[#94A3B8]" />
            <input
              type="text"
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Search by name, MRN, or diagnosis…"
              className="pl-12 pr-4 py-3 w-full rounded-2xl bg-[#F6FAFF] border border-[#E2E8F0] focus:outline-none focus:ring-2 focus:ring-[#2563EB] focus:border-transparent"
            />
          </div>
          <button
            type="button"
            className="px-4 py-3 rounded-2xl border border-[#E2E8F0] hover:bg-[#F6FAFF] transition-colors flex items-center gap-2"
          >
            <Filter className="w-5 h-5 text-[#64748B]" />
            <span className="text-sm font-medium text-[#0F172A]">Filter</span>
          </button>
          <button
            type="button"
            className="px-4 py-3 rounded-2xl border border-[#E2E8F0] hover:bg-[#F6FAFF] transition-colors flex items-center gap-2"
          >
            <ArrowUpDown className="w-5 h-5 text-[#64748B]" />
            <span className="text-sm font-medium text-[#0F172A]">Sort</span>
          </button>
        </div>

        {error && (
          <p className="text-sm text-red-600 bg-red-50 border border-red-100 rounded-lg px-3 py-2 mb-3">{error}</p>
        )}

        <div className="flex gap-2">
          <span className="px-4 py-2 rounded-full bg-[#2563EB] text-white text-sm font-medium">All</span>
          <span className="text-xs text-[#94A3B8] py-2">Filter chips are cosmetic in this prototype.</span>
        </div>
      </div>

      <div className="space-y-3">
        {!data && !error && <p className="text-sm text-[#64748B]">Loading patients…</p>}
        {data && patients.length === 0 && (
          <p className="text-sm text-[#64748B]">No patients matched this search.</p>
        )}
        {patients.map((patient) => (
          <div
            key={patient.id}
            role="button"
            tabIndex={0}
            onClick={() => navigate(`/patient/${patient.id}`)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') navigate(`/patient/${patient.id}`);
            }}
            className="bg-white rounded-2xl p-5 border border-[#E2E8F0] hover:border-[#2563EB] transition-all cursor-pointer"
          >
            <div className="flex items-center gap-6">
              <div className="w-14 h-14 rounded-full bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center text-white font-semibold text-lg flex-shrink-0">
                {patient.name
                  .split(' ')
                  .map((n) => n[0])
                  .join('')}
              </div>

              <div className="flex-1 grid grid-cols-6 gap-4 items-center">
                <div>
                  <p className="font-semibold text-[#0F172A]">{patient.name}</p>
                  <p className="text-sm text-[#64748B]">MRN: {patient.mrn}</p>
                  <p className="text-xs text-[#94A3B8]">
                    {patient.age != null ? patient.age : '—'}
                    {patient.sex ?? ''}
                  </p>
                </div>

                <div>
                  <p className="text-xs uppercase text-[#94A3B8] mb-1">Diagnosis</p>
                  <p className="text-sm font-medium text-[#0F172A]">{patient.diagnosis || '—'}</p>
                  <p className="text-xs text-[#64748B]">{patient.stage || ''}</p>
                </div>

                <div>
                  <p className="text-xs uppercase text-[#94A3B8] mb-1">Treatment</p>
                  <p className="text-sm text-[#0F172A]">{patient.treatment || '—'}</p>
                </div>

                <div>
                  <p className="text-xs uppercase text-[#94A3B8] mb-1">Biomarkers</p>
                  <p className="text-sm text-[#0F172A]">{patient.biomarkers || '—'}</p>
                </div>

                <div>
                  <p className="text-xs uppercase text-[#94A3B8] mb-1">CA 19-9</p>
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-medium text-[#0F172A]">
                      {patient.ca199 != null ? `${patient.ca199} U/mL` : 'N/A'}
                    </p>
                    {patient.trend === 'up' && <span className="text-red-500">↑</span>}
                    {patient.trend === 'down' && <span className="text-green-500">↓</span>}
                    {patient.trend === 'stable' && <span className="text-gray-400">→</span>}
                  </div>
                  <p className="text-xs text-[#94A3B8]">{formatUpdated(patient.updated)}</p>
                </div>

                <div className="flex items-center justify-end gap-3">
                  <StatusBadge status={statusForBadge(patient.status)} size="sm" />
                  <button
                    type="button"
                    onClick={(ev) => {
                      ev.stopPropagation();
                      navigate(`/patient/${patient.id}`);
                    }}
                    className="px-4 py-2 bg-[#2563EB] text-white rounded-xl text-sm font-medium hover:bg-[#1d4ed8] transition-colors"
                  >
                    Open Workspace
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
