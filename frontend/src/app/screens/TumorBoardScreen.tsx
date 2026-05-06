import { AlertTriangle, Clock, Download, FileText } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';

import { fetchLatestBrief, fetchPatients, generateBrief } from '../api/client';
import {
  STANDARD_BRIEF_DISCLAIMER,
  evidenceStatusBadge,
  formatBriefDate,
  normalizeBriefPayload,
  timelineTypeLabel,
  type BriefEvidenceItem,
  type BriefMissingRow,
  type BriefSourceDocument,
  type BriefTimelineEvent,
} from '../utils/tumorBriefNormalize';

type PatientLite = {
  id: number;
  name: string;
  mrn: string;
  diagnosis?: string;
  stage?: string;
  treatment?: string;
  status?: string;
};

type BriefRecord = Record<string, unknown>;

function proseParagraphs(text: string): string[] {
  const t = text.trim();
  if (!t) return [];
  return t.split(/\n\n+/).map((p) => p.trim()).filter(Boolean);
}

export function TumorBoardScreen() {
  const [patients, setPatients] = useState<PatientLite[]>([]);
  const [patientId, setPatientId] = useState('');
  const [brief, setBrief] = useState<BriefRecord | null>(null);
  const [disclaimer, setDisclaimer] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const selectedPatient = useMemo(
    () => patients.find((p) => String(p.id) === patientId),
    [patients, patientId],
  );

  const normalized = useMemo(() => normalizeBriefPayload(brief), [brief]);

  useEffect(() => {
    let cancelled = false;
    fetchPatients()
      .then((res) => {
        if (cancelled) return;
        const rows: PatientLite[] = res.patients.map((p) => ({
          id: p.id,
          name: p.name,
          mrn: p.mrn,
          diagnosis: p.diagnosis,
          stage: p.stage,
          treatment: p.treatment,
          status: p.status,
        }));
        setPatients(rows);
        if (rows.length && !patientId) setPatientId(String(rows[0].id));
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
  }, []);

  useEffect(() => {
    if (!patientId) return;
    let cancelled = false;
    fetchLatestBrief(Number(patientId))
      .then((res) => {
        if (!cancelled) {
          const b = res.brief as BriefRecord | null;
          setBrief(b);
          setDisclaimer((b?.disclaimer as string | undefined) ?? null);
        }
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [patientId]);

  const onGenerate = async () => {
    if (!patientId) return;
    setGenerating(true);
    setError(null);
    try {
      const res = await generateBrief(Number(patientId));
      const b = res.brief as BriefRecord | null;
      setBrief(b);
      setDisclaimer((res.disclaimer as string | undefined) ?? (b?.disclaimer as string | undefined) ?? null);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Generate failed');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6">
        <h3 className="font-semibold text-[#0F172A] mb-4 text-lg">Tumor Board</h3>
        <p className="text-sm text-[#64748B] mb-6">Generate a source-backed case brief for tumor board review.</p>

        {error && (
          <p className="text-sm text-red-600 bg-red-50 border border-red-100 rounded-lg px-3 py-2 mb-3">{error}</p>
        )}

        <div className="mb-6">
          <label htmlFor="tb-patient" className="block text-sm font-medium text-[#0F172A] mb-2">
            Patient
          </label>
          <select
            id="tb-patient"
            value={patientId}
            onChange={(e) => setPatientId(e.target.value)}
            disabled={loading || patients.length === 0}
            className="w-full px-4 py-2.5 rounded-lg border border-[#E2E8F0] bg-white focus:outline-none focus:ring-2 focus:ring-[#2563EB] focus:border-transparent"
          >
            {patients.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name} — MRN {p.mrn}
              </option>
            ))}
          </select>
        </div>

        <button
          type="button"
          onClick={onGenerate}
          disabled={generating || !patientId}
          className="px-4 py-2.5 bg-[#2563EB] text-white rounded-lg font-medium hover:bg-[#1d4ed8] transition-colors disabled:opacity-50"
        >
          {generating ? 'Generating…' : 'Generate brief'}
        </button>
      </div>

      <div className="bg-white rounded-2xl border border-[#E2E8F0]">
        <div className="flex flex-wrap items-center justify-between gap-3 p-6 border-b border-[#E2E8F0]">
          <div>
            <h3 className="font-semibold text-[#0F172A] text-lg">Tumor board brief</h3>
            {selectedPatient && (
              <p className="text-sm text-[#64748B] mt-1">
                {selectedPatient.name} · MRN {selectedPatient.mrn}
              </p>
            )}
          </div>
          <div className="flex gap-2">
            <button
              type="button"
              className="px-3 py-2 text-sm border border-[#E2E8F0] rounded-lg hover:bg-[#F8FAFC] transition-colors flex items-center gap-2"
            >
              <Download className="w-4 h-4" />
              Export PDF
            </button>
            <button
              type="button"
              className="px-3 py-2 text-sm border border-[#E2E8F0] rounded-lg hover:bg-[#F8FAFC] transition-colors flex items-center gap-2"
            >
              <FileText className="w-4 h-4" />
              Export text
            </button>
          </div>
        </div>

        <div className="max-w-4xl mx-auto p-8 space-y-10">
          {!brief && <p className="text-sm text-[#64748B]">No brief yet — select a patient and generate.</p>}

          {normalized && (
            <>
              <section className="rounded-2xl border border-[#E2E8F0] bg-[#FAFBFC] p-6 shadow-sm">
                <h4 className="text-xs font-semibold uppercase tracking-wide text-[#94A3B8] mb-4">
                  Patient summary
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-10 gap-y-3 text-sm">
                  <div>
                    <span className="text-[#94A3B8] block text-xs mb-0.5">Patient</span>
                    <span className="font-semibold text-[#0F172A]">{selectedPatient?.name ?? '—'}</span>
                  </div>
                  <div>
                    <span className="text-[#94A3B8] block text-xs mb-0.5">MRN</span>
                    <span className="text-[#0F172A]">{selectedPatient?.mrn ?? '—'}</span>
                  </div>
                  <div>
                    <span className="text-[#94A3B8] block text-xs mb-0.5">Diagnosis</span>
                    <span className="text-[#0F172A]">{selectedPatient?.diagnosis ?? '—'}</span>
                  </div>
                  <div>
                    <span className="text-[#94A3B8] block text-xs mb-0.5">Stage</span>
                    <span className="text-[#0F172A]">{selectedPatient?.stage ?? '—'}</span>
                  </div>
                  <div className="sm:col-span-2">
                    <span className="text-[#94A3B8] block text-xs mb-0.5">Current treatment narrative</span>
                    <span className="text-[#0F172A] leading-relaxed">{selectedPatient?.treatment ?? '—'}</span>
                  </div>
                  {selectedPatient?.status ? (
                    <div>
                      <span className="text-[#94A3B8] block text-xs mb-0.5">Review status</span>
                      <span className="text-[#0F172A] capitalize">{selectedPatient.status.replace(/_/g, ' ')}</span>
                    </div>
                  ) : null}
                </div>
                <div className="mt-6 pt-4 border-t border-[#E2E8F0]">
                  <p className="text-xs text-[#64748B] leading-relaxed italic">{STANDARD_BRIEF_DISCLAIMER}</p>
                </div>
              </section>

              <section className="space-y-3">
                <h4 className="text-base font-semibold text-[#0F172A] tracking-tight">Case summary</h4>
                <div className="text-sm text-[#0F172A] leading-relaxed space-y-3">
                  {proseParagraphs(normalized.case_summary).map((para, i) => (
                    <p key={i}>{para}</p>
                  ))}
                  {!normalized.case_summary && <p className="text-[#64748B]">—</p>}
                </div>
              </section>

              <section className="space-y-4">
                <h4 className="text-base font-semibold text-[#0F172A] tracking-tight">Current treatment course</h4>
                <div className="rounded-xl border border-[#E2E8F0] bg-white p-6 shadow-sm space-y-4">
                  {proseParagraphs(normalized.treatment_course).map((para, idx) => {
                    const lines = para.split('\n');
                    const first = lines[0]?.trim() ?? para;
                    const rest = lines.slice(1).join('\n').trim();
                    return (
                      <div key={idx}>
                        <p className="text-sm font-semibold text-[#0F172A]">{first}</p>
                        {rest ? (
                          <p className="text-sm text-[#64748B] leading-relaxed mt-2 whitespace-pre-wrap">{rest}</p>
                        ) : null}
                        <div className="mt-3 flex flex-wrap gap-1.5">
                          <span className="text-[11px] px-2 py-0.5 rounded-md bg-[#F1F5F9] text-[#475569] border border-[#E2E8F0]">
                            Chart narrative
                          </span>
                        </div>
                      </div>
                    );
                  })}
                  {!normalized.treatment_course.trim() && <p className="text-sm text-[#64748B]">—</p>}
                </div>
              </section>

              <BriefTimelineSection events={normalized.key_timeline_events} />
              <BriefEvidenceSection items={normalized.evidence_of_change} />
              <BriefMissingSection items={normalized.missing_or_unconfirmed_data} />
              <BriefSourcesSection docs={normalized.source_documents} />

              {(disclaimer || brief?.disclaimer) && (
                <p className="text-xs text-[#64748B] p-4 bg-[#F8FAFC] rounded-xl border border-[#E2E8F0] leading-relaxed">
                  {(disclaimer || brief?.disclaimer) as string}
                </p>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

function BriefTimelineSection({ events }: { events: BriefTimelineEvent[] }) {
  if (!events.length) return null;
  return (
    <section className="space-y-4">
      <h4 className="text-base font-semibold text-[#0F172A] tracking-tight">Key timeline events</h4>
      <div className="relative border-l-2 border-[#E2E8F0] pl-6 space-y-6">
        {events.map((ev, i) => (
          <div key={i} className="relative">
            <div className="absolute -left-[29px] top-1 flex h-7 w-7 items-center justify-center rounded-full bg-white border-2 border-[#2563EB]">
              <Clock className="w-3.5 h-3.5 text-[#2563EB]" />
            </div>
            <p className="text-xs text-[#94A3B8] mb-1">{formatBriefDate(ev.date)}</p>
            <p className="text-sm font-semibold text-[#0F172A] mb-1">{ev.title || 'Event'}</p>
            <p className="text-sm text-[#64748B] leading-relaxed mb-2">{ev.detail || ''}</p>
            <span className="inline-flex px-2 py-0.5 text-[11px] font-medium rounded-md bg-[#F1F5F9] text-[#475569] border border-[#E2E8F0]">
              {timelineTypeLabel(ev)}
            </span>
          </div>
        ))}
      </div>
    </section>
  );
}

function BriefEvidenceSection({ items }: { items: BriefEvidenceItem[] }) {
  if (!items.length) return null;
  return (
    <section className="space-y-4">
      <h4 className="text-base font-semibold text-[#0F172A] tracking-tight">Evidence of change</h4>
      <div className="space-y-3">
        {items.map((it, idx) => {
          const bd = evidenceStatusBadge(it.status);
          const badgeClass =
            bd.kind === 'needs-review'
              ? 'bg-red-50 text-red-800 border-red-100'
              : bd.kind === 'watch'
                ? 'bg-amber-50 text-amber-900 border-amber-100'
                : 'bg-slate-50 text-slate-700 border-slate-200';
          return (
            <div
              key={idx}
              className="rounded-xl border border-[#E2E8F0] border-l-[5px] border-l-[#2563EB] bg-white p-4 shadow-sm"
            >
              <div className="flex flex-wrap items-center gap-2 mb-2">
                <span className={`text-[10px] font-semibold uppercase tracking-wide px-2 py-0.5 rounded-md border ${badgeClass}`}>
                  {bd.label}
                </span>
              </div>
              <p className="text-sm font-semibold text-[#0F172A] mb-2">{it.title}</p>
              {it.explanation_excerpt ? (
                <p className="text-sm text-[#64748B] leading-relaxed">{it.explanation_excerpt}</p>
              ) : null}
              <div className="mt-3 flex flex-wrap gap-1.5">
                <span className="text-[11px] px-2 py-0.5 rounded-md bg-[#F8FAFC] text-[#64748B] border border-[#E2E8F0]">
                  Source-backed flag
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}

function BriefMissingSection({ items }: { items: BriefMissingRow[] }) {
  if (!items.length) return null;
  return (
    <section className="space-y-4">
      <h4 className="text-base font-semibold text-[#0F172A] tracking-tight">Missing or unconfirmed data</h4>
      <div className="space-y-3">
        {items.map((row, idx) => (
          <div
            key={idx}
            className="flex gap-3 rounded-xl border border-amber-100 bg-amber-50/50 p-4"
          >
            <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-semibold text-[#0F172A] mb-1">{row.headline || row.bullet || 'Gap noted'}</p>
              {row.explanation ? (
                <p className="text-sm text-[#64748B] leading-relaxed">{row.explanation}</p>
              ) : (
                row.bullet && row.bullet !== row.headline && (
                  <p className="text-sm text-[#64748B] leading-relaxed">{row.bullet}</p>
                )
              )}
              <p className="text-[11px] text-amber-900/70 mt-2">May warrant clinician review — completeness check.</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function BriefSourcesSection({ docs }: { docs: BriefSourceDocument[] }) {
  if (!docs.length) return null;
  return (
    <section className="space-y-4">
      <h4 className="text-base font-semibold text-[#0F172A] tracking-tight">Source documents used</h4>
      <ul className="divide-y divide-[#E2E8F0] rounded-xl border border-[#E2E8F0] bg-white overflow-hidden">
        {docs.map((doc, idx) => (
          <li key={idx} className="flex gap-4 px-4 py-3.5 hover:bg-[#FAFBFC] transition-colors">
            <FileText className="w-5 h-5 text-[#94A3B8] flex-shrink-0 mt-0.5" />
            <div className="min-w-0 flex-1">
              <p className="text-sm font-semibold text-[#0F172A] truncate">{doc.title}</p>
              <div className="flex flex-wrap items-center gap-2 mt-1">
                {doc.type ? (
                  <span className="text-[11px] px-2 py-0.5 rounded-md bg-[#F1F5F9] text-[#475569]">
                    {doc.type}
                  </span>
                ) : null}
                {doc.report_date ? (
                  <span className="text-[11px] text-[#64748B]">{formatBriefDate(doc.report_date)}</span>
                ) : null}
              </div>
              {doc.snippet || doc.note ? (
                <p className="text-xs text-[#64748B] mt-2 leading-relaxed italic line-clamp-3">{doc.snippet || doc.note}</p>
              ) : null}
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
