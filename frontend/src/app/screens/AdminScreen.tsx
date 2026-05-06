import { Users, BarChart3, Shield, Database } from 'lucide-react';
import { useEffect, useState } from 'react';

import { fetchAdminSummary } from '../api/client';

const teamMembers = [
  { name: 'Dr. Alex Morgan', role: 'Doctor', access: 'Full clinical access', lastActive: '2 hours ago', initials: 'AM' },
  { name: 'Jamie Lee', role: 'Nurse', access: 'Upload + notes', lastActive: '5 hours ago', initials: 'JL' },
  { name: 'Priya Shah', role: 'Admin', access: 'Patient management', lastActive: '1 day ago', initials: 'PS' },
];

export function AdminScreen() {
  const [summary, setSummary] = useState<{
    user_total: number;
    patient_total: number;
    reports_parsed: number;
    unconfirmed_extractions: number;
    active_observations: number;
    disclaimer?: string;
  } | null>(null);
  const [summaryError, setSummaryError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchAdminSummary()
      .then((data) => {
        if (!cancelled) {
          setSummary(data);
          setSummaryError(null);
        }
      })
      .catch((e: Error) => {
        if (!cancelled) setSummaryError(e.message);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="space-y-6">
      {summaryError && (
        <p className="text-sm text-amber-800 bg-amber-50 border border-amber-100 rounded-lg px-3 py-2">
          Operational summary unavailable ({summaryError}). Sign in as an admin demo user (e.g. priya.shah.demo) to load
          live counts.
        </p>
      )}

      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border border-[#E2E8F0] p-5">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center">
              <Database className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-xs text-[#94A3B8] uppercase tracking-wide font-medium">Reports parsed</p>
              <p className="text-2xl font-semibold text-[#0F172A]">
                {summary ? summary.reports_parsed : '—'}
              </p>
            </div>
          </div>
          <p className="text-xs text-[#64748B]">From API when authorized</p>
        </div>

        <div className="bg-white rounded-lg border border-[#E2E8F0] p-5">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-lg bg-amber-50 flex items-center justify-center">
              <BarChart3 className="w-5 h-5 text-amber-600" />
            </div>
            <div>
              <p className="text-xs text-[#94A3B8] uppercase tracking-wide font-medium">Need confirmation</p>
              <p className="text-2xl font-semibold text-[#0F172A]">
                {summary ? summary.unconfirmed_extractions : '—'}
              </p>
            </div>
          </div>
          <p className="text-xs text-[#64748B]">Unconfirmed extractions</p>
        </div>

        <div className="bg-white rounded-lg border border-[#E2E8F0] p-5">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-lg bg-purple-50 flex items-center justify-center">
              <BarChart3 className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <p className="text-xs text-[#94A3B8] uppercase tracking-wide font-medium">Confirmed observations</p>
              <p className="text-2xl font-semibold text-[#0F172A]">{summary ? summary.active_observations : '—'}</p>
            </div>
          </div>
          <p className="text-xs text-[#64748B]">Observation rows marked confirmed</p>
        </div>

        <div className="bg-white rounded-lg border border-[#E2E8F0] p-5">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-lg bg-green-50 flex items-center justify-center">
              <Users className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-xs text-[#94A3B8] uppercase tracking-wide font-medium">Users / patients</p>
              <p className="text-2xl font-semibold text-[#0F172A]">
                {summary ? `${summary.user_total} / ${summary.patient_total}` : '—'}
              </p>
            </div>
          </div>
          <p className="text-xs text-[#64748B]">Django counts</p>
        </div>
      </div>

      {summary?.disclaimer && (
        <p className="text-xs text-[#64748B] bg-[#F8FAFC] border border-[#E2E8F0] rounded-lg px-3 py-2">{summary.disclaimer}</p>
      )}

      <div className="bg-white rounded-lg border border-[#E2E8F0] p-6">
        <div className="flex items-center justify-between mb-5">
          <div>
            <h3 className="font-semibold text-[#0F172A] text-sm">Team access</h3>
            <p className="text-xs text-[#64748B] mt-0.5">Static demo roster (user management not exposed via API yet)</p>
          </div>
          <button
            type="button"
            className="px-3 py-2 text-sm bg-[#2563EB] text-white rounded-lg hover:bg-[#1d4ed8] transition-colors"
          >
            Add member
          </button>
        </div>

        <div className="space-y-2">
          {teamMembers.map((member) => (
            <div
              key={member.name}
              className="flex items-center gap-4 p-4 rounded-lg border border-[#E2E8F0] hover:bg-[#F8FAFC] transition-colors"
            >
              <div className="w-9 h-9 rounded-lg bg-[#64748B] flex items-center justify-center text-white text-xs font-medium">
                {member.initials}
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-[#0F172A]">{member.name}</p>
                <p className="text-xs text-[#64748B]">
                  {member.role} · {member.access}
                </p>
              </div>
              <div className="text-right">
                <p className="text-xs text-[#64748B]">Last active</p>
                <p className="text-xs font-medium text-[#0F172A]">{member.lastActive}</p>
              </div>
              <button
                type="button"
                className="px-3 py-1.5 text-xs text-[#64748B] border border-[#E2E8F0] rounded hover:bg-[#F8FAFC] transition-colors"
              >
                Edit
              </button>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-lg border border-[#E2E8F0] p-6">
        <h3 className="font-semibold text-[#0F172A] mb-4 text-sm">Access levels</h3>

        <div className="space-y-3">
          <div className="p-4 rounded-lg bg-green-50 border border-green-100">
            <div className="flex items-start gap-3">
              <Shield className="w-4 h-4 text-green-600 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm font-semibold text-green-700 mb-1">Full clinical access</p>
                <p className="text-sm text-green-600">
                  View all patient data, upload reports, add notes, export summaries, manage evidence flags
                </p>
              </div>
            </div>
          </div>

          <div className="p-4 rounded-lg bg-blue-50 border border-blue-100">
            <div className="flex items-start gap-3">
              <Shield className="w-4 h-4 text-blue-600 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm font-semibold text-blue-700 mb-1">Upload + notes</p>
                <p className="text-sm text-blue-600">Upload reports, add clinical notes, view assigned patients</p>
              </div>
            </div>
          </div>

          <div className="p-4 rounded-lg bg-purple-50 border border-purple-100">
            <div className="flex items-start gap-3">
              <Shield className="w-4 h-4 text-purple-600 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm font-semibold text-purple-700 mb-1">Patient management</p>
                <p className="text-sm text-purple-600">Manage patient records, team members, system settings</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
