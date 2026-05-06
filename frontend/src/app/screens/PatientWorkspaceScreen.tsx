import { useCallback, useEffect, useMemo, useState } from 'react';
import { ArrowLeft, Upload, Plus, Download, FileText, Search, CheckCircle2 } from 'lucide-react';
import { useNavigate, useParams } from 'react-router';

import { fetchPatientEvidence, fetchEvidenceSearch, markPatientReviewed } from '../api/client';
import type {
  WorkspaceEvidenceResponse,
  EvidenceSearchHit,
  WorkspaceObservationRow,
  WorkspaceSourceBackedObservation,
} from '../api/client';
import { EvidenceCard } from '../components/EvidenceCard';
import { SourceVisualization } from '../components/SourceVisualization';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../components/ui/tabs';

function timelineCategory(kind: string | undefined): string {
  const u = (kind || '').toLowerCase();
  if (u.includes('lab')) return 'Labs';
  if (u.includes('imag')) return 'Imaging';
  if (u.includes('path')) return 'Pathology';
  if (u === 'treatment') return 'Treatment';
  if (u.includes('note') || u.includes('encounter') || u.includes('clinical')) return 'Notes';
  return 'Notes';
}

function formatTimelineDate(iso?: string): string {
  if (!iso) return '—';
  try {
    return new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
  } catch {
    return iso.slice(0, 10);
  }
}

/** Display API window boundary (ISO date or datetime). */
function formatReviewWindowBoundary(iso?: string): string {
  if (!iso) return '—';
  if (iso.includes('T')) {
    try {
      return new Date(iso).toLocaleString(undefined, { month: 'short', day: 'numeric', year: 'numeric', hour: 'numeric', minute: '2-digit' });
    } catch {
      return iso;
    }
  }
  return formatTimelineDate(iso);
}

function severityFromStatus(status: string | undefined): 'info' | 'watch' | 'needs-review' {
  if (status === 'needs_review' || status === 'needs-review') return 'needs-review';
  if (status === 'watch') return 'watch';
  return 'info';
}

const quickQuestions = [
  'tumor marker getting worse',
  'neuroendocrine marker rising',
  'possible progression',
  'missing liver labs',
];

function resultKindLabel(kind?: string): string {
  const k = (kind || 'keyword').toLowerCase();
  if (k === 'semantic') return 'Semantic';
  if (k === 'hybrid') return 'Hybrid';
  return 'Keyword';
}

function resultKindPillClass(kind?: string): string {
  const k = (kind || 'keyword').toLowerCase();
  if (k === 'semantic') return 'bg-violet-50 text-violet-800 border-violet-100';
  if (k === 'hybrid') return 'bg-indigo-50 text-indigo-800 border-indigo-100';
  return 'bg-slate-100 text-slate-700 border-slate-200';
}

function hitsSame(a: EvidenceSearchHit, b: EvidenceSearchHit): boolean {
  return (
    a.source_kind === b.source_kind &&
    a.source_id === b.source_id &&
    a.chunk_index === b.chunk_index &&
    (a.matched_snippet || '') === (b.matched_snippet || '')
  );
}

type ClinicalCardRow = {
  id: number;
  raw: WorkspaceSourceBackedObservation;
  severity: 'info' | 'watch' | 'needs-review';
  statusBadge: string;
  headline: string;
  keyFact?: string;
  whySurfaced: string;
  sourceChips: string[];
  priority: number;
};

const RULE_PRIORITY: Record<string, number> = {
  marker_trend: 0,
  imaging_language: 1,
  symptom_language: 2,
  missing_data: 3,
  biomarker_documentation: 4,
};

function patientReviewLabel(rs: string | undefined): string {
  const u = (rs || '').replace(/-/g, '_').toLowerCase();
  if (u === 'needs_review') return 'Needs review';
  if (u === 'watch') return 'Watch';
  if (u === 'stable') return 'Stable';
  return rs || '—';
}

function observationStatusBadge(status: string): string {
  if (status === 'needs_review') return 'Needs review';
  if (status === 'watch') return 'Monitor / Follow Up';
  return 'Informational';
}

function inferRuleKind(ej: Record<string, unknown> | undefined): string {
  if (!ej) return '';
  const rk = ej.rule_kind;
  if (typeof rk === 'string') return rk;
  if (ej.marker != null && (ej.values != null || ej.data_points != null)) return 'marker_trend';
  if (ej.needle != null) return 'missing_data';
  if (Array.isArray(ej.biomarkers)) return 'biomarker_documentation';
  if (ej.primary_phrase != null && Array.isArray(ej.terms)) return 'imaging_language';
  if (Array.isArray(ej.terms)) return 'symptom_language';
  return '';
}

function priorityFromEj(ej: Record<string, unknown> | undefined): number {
  const k = inferRuleKind(ej);
  return k in RULE_PRIORITY ? RULE_PRIORITY[k]! : 50;
}

function formatEvidenceChip(it: { title: string; evidence_date?: string | null }): string {
  const d = it.evidence_date ? formatTimelineDate(it.evidence_date) : '';
  return d ? `${it.title} · ${d}` : it.title;
}

function buildKeyFact(so: WorkspaceSourceBackedObservation): string | undefined {
  const ej = so.evidence_json;
  if (!ej) return undefined;
  const rk = inferRuleKind(ej);
  if (rk === 'marker_trend') {
    if (typeof ej.data_points === 'string') return ej.data_points;
    if (typeof ej.values === 'string') return ej.values;
  }
  if (rk === 'symptom_language' && Array.isArray(ej.terms) && ej.terms.length) {
    return (ej.terms as string[]).slice(0, 6).join(', ');
  }
  if (rk === 'imaging_language' && typeof ej.primary_phrase === 'string') return ej.primary_phrase;
  if (rk === 'missing_data') {
    const needle = typeof ej.needle === 'string' ? ej.needle : '';
    const w = ej.window_days;
    const wd = typeof w === 'number' ? w : 30;
    return needle ? `No confirmed ${needle} in trailing ${wd}-day window` : undefined;
  }
  if (rk === 'biomarker_documentation' && typeof ej.primary_biomarker === 'string') return ej.primary_biomarker;
  return typeof ej.data_points === 'string' ? ej.data_points : undefined;
}

function buildSourceChips(so: WorkspaceSourceBackedObservation): string[] {
  const linked = so.linked_evidence_items ?? [];
  if (linked.length > 0) return linked.slice(0, 8).map(formatEvidenceChip);
  const ej = so.evidence_json;
  const raw = ej?.sources;
  if (Array.isArray(raw)) return raw.map((x) => String(x)).filter(Boolean).slice(0, 8);
  return ['Source trail available — select to review'];
}

function mapSoToClinical(so: WorkspaceSourceBackedObservation): ClinicalCardRow {
  return {
    id: so.id,
    raw: so,
    severity: severityFromStatus(so.status),
    statusBadge: observationStatusBadge(so.status),
    headline: so.title,
    keyFact: buildKeyFact(so),
    whySurfaced: so.explanation,
    sourceChips: buildSourceChips(so),
    priority: priorityFromEj(so.evidence_json),
  };
}

function sortClinicalGroup(rows: ClinicalCardRow[]): ClinicalCardRow[] {
  return [...rows].sort((a, b) => {
    if (a.priority !== b.priority) return a.priority - b.priority;
    return (b.raw.created_at || '').localeCompare(a.raw.created_at || '');
  });
}

function latestEvidenceIso(soList: WorkspaceSourceBackedObservation[]): string | null {
  let max = '';
  for (const s of soList) {
    const c = s.created_at || '';
    if (c > max) max = c;
  }
  return max || null;
}

function deriveThemeChips(rows: ClinicalCardRow[]): string[] {
  const themes: string[] = [];
  const seen = new Set<string>();
  const push = (t: string) => {
    const x = t.trim();
    if (!x || seen.has(x)) return;
    seen.add(x);
    themes.push(x);
  };
  for (const r of rows) {
    const ej = r.raw.evidence_json;
    const rk = inferRuleKind(ej);
    const marker = ej?.marker;
    if (rk === 'marker_trend' && typeof marker === 'string') push(`${marker} trend`);
    if (rk === 'imaging_language') push('Imaging language');
    if (rk === 'symptom_language') push('Symptoms');
    if (rk === 'missing_data' && typeof ej?.needle === 'string') push(`Missing ${ej.needle}`);
    if (rk === 'biomarker_documentation') push('Biomarker mention');
  }
  return themes.slice(0, 4);
}

function sourceTypeLabel(st: string): string {
  const map: Record<string, string> = {
    report: 'Report',
    observation: 'Observation',
    note: 'Clinical note',
    clinical_note: 'Clinical note',
    treatment: 'Treatment',
    timeline: 'Timeline',
  };
  return map[st] || st.replace(/_/g, ' ');
}

export function PatientWorkspaceScreen() {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const patientId = id ?? '';

  const [payload, setPayload] = useState<WorkspaceEvidenceResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!patientId) return;
    let cancelled = false;
    fetchPatientEvidence(patientId)
      .then((d) => {
        if (!cancelled) {
          setPayload(d);
          setError(null);
        }
      })
      .catch((e: Error) => {
        if (!cancelled) setError(e.message);
      });
    return () => {
      cancelled = true;
    };
  }, [patientId]);

  const [chartQuery, setChartQuery] = useState('');
  const [suggestedTerms, setSuggestedTerms] = useState<string[]>([]);
  const [chartHits, setChartHits] = useState<EvidenceSearchHit[]>([]);
  const [chartSearchLoading, setChartSearchLoading] = useState(false);
  const [chartSearchError, setChartSearchError] = useState<string | null>(null);
  const [chartSearchRan, setChartSearchRan] = useState(false);
  const [chartDisclaimer, setChartDisclaimer] = useState<string | null>(null);
  const [markReviewBusy, setMarkReviewBusy] = useState(false);

  const [selectedEvidence, setSelectedEvidence] = useState<number | null>(null);
  const [selectedChartHit, setSelectedChartHit] = useState<EvidenceSearchHit | null>(null);
  const [sourceViewerTab, setSourceViewerTab] = useState<"trail" | "viz">("trail");
  const [timelineFilter, setTimelineFilter] = useState('All');

  useEffect(() => {
    if (!patientId) return;
    let cancelled = false;
    fetchEvidenceSearch('', patientId, { top_k: 1 })
      .then((r) => {
        if (cancelled) return;
        if (r.suggested_terms?.length) setSuggestedTerms(r.suggested_terms);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [patientId]);

  const onMarkChartReviewed = useCallback(async () => {
    if (!patientId) return;
    setMarkReviewBusy(true);
    try {
      await markPatientReviewed(patientId);
      const next = await fetchPatientEvidence(patientId);
      setPayload(next);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not mark chart reviewed');
    } finally {
      setMarkReviewBusy(false);
    }
  }, [patientId]);

  const runChartSearch = useCallback(
    async (raw: string) => {
      const q = raw.trim();
      if (!q || !patientId) return;
      setChartSearchRan(true);
      setChartSearchLoading(true);
      setChartSearchError(null);
      try {
        const res = await fetchEvidenceSearch(q, patientId, { top_k: 8 });
        setChartHits(res.results);
        setChartDisclaimer(res.disclaimer ?? null);
        if (res.suggested_terms?.length) setSuggestedTerms(res.suggested_terms);
        setChartQuery(q);
      } catch (e) {
        setChartHits([]);
        setChartSearchError(e instanceof Error ? e.message : 'Search failed');
      } finally {
        setChartSearchLoading(false);
      }
    },
    [patientId],
  );

  const selectObservation = (id: number) => {
    setSelectedChartHit(null);
    setSelectedEvidence(id);
    setSourceViewerTab('trail');
  };

  const selectChartHit = (hit: EvidenceSearchHit) => {
    setSelectedEvidence(null);
    setSelectedChartHit(hit);
    setSourceViewerTab('trail');
  };

  const timeline = payload?.timeline ?? [];
  const sourceObs = payload?.source_backed_observations ?? [];
  const observations = payload?.observations ?? [];

  const filteredTimeline = useMemo(() => {
    if (timelineFilter === 'All') return timeline;
    return timeline.filter((item) => timelineCategory(item.type) === timelineFilter);
  }, [timeline, timelineFilter]);

  const clinicalGrouped = useMemo(() => {
    const mapped = sourceObs.map(mapSoToClinical);
    return {
      needs_review: sortClinicalGroup(mapped.filter((x) => x.raw.status === 'needs_review')),
      watch: sortClinicalGroup(mapped.filter((x) => x.raw.status === 'watch')),
      info: sortClinicalGroup(
        mapped.filter((x) => x.raw.status !== 'needs_review' && x.raw.status !== 'watch'),
      ),
    };
  }, [sourceObs]);

  const flatClinical = useMemo(
    () => [...clinicalGrouped.needs_review, ...clinicalGrouped.watch, ...clinicalGrouped.info],
    [clinicalGrouped],
  );

  const selectedClinical = useMemo(() => {
    if (selectedEvidence == null) return undefined;
    return flatClinical.find((c) => c.id === selectedEvidence);
  }, [flatClinical, selectedEvidence]);

  const atGlance = useMemo(() => {
    const total = sourceObs.length;
    const highPriority = sourceObs.filter((s) => s.status === 'needs_review').length;
    const latestIso = latestEvidenceIso(sourceObs);
    const themes = deriveThemeChips(sourceObs.map(mapSoToClinical));
    return {
      total,
      highPriority,
      latestIso,
      themes,
      reviewStatus: payload?.patient?.review_status,
    };
  }, [sourceObs, payload?.patient?.review_status]);

  const chipPrompts = suggestedTerms.length > 0 ? suggestedTerms : quickQuestions;

  function renderClinicalSection(label: string, rows: ClinicalCardRow[], emphasizeFirst: number) {
    if (rows.length === 0) return null;
    return (
      <div className="space-y-2 mb-5 last:mb-0">
        <h4 className="text-[11px] font-semibold uppercase tracking-wide text-[#64748B]">{label}</h4>
        <div className="space-y-3">
          {rows.map((card, idx) => (
            <EvidenceCard
              key={card.id}
              statusBadge={card.statusBadge}
              headline={card.headline}
              keyFact={card.keyFact}
              whySurfaced={card.whySurfaced}
              sourceChips={card.sourceChips}
              severity={card.severity}
              emphasized={emphasizeFirst > 0 && idx < emphasizeFirst}
              selected={selectedEvidence === card.id && !selectedChartHit}
              onClick={() => selectObservation(card.id)}
            />
          ))}
        </div>
      </div>
    );
  }

  const p = payload?.patient;
  const reviewLine = p
    ? `${p.name} · MRN ${p.mrn}${p.primary_diagnosis ? ` · ${p.primary_diagnosis}` : ''}${p.cancer_stage ? ` · ${p.cancer_stage}` : ''}`
    : 'Loading…';

  return (
    <div className="space-y-4">
      <div className="bg-white rounded-2xl border border-[#E2E8F0] p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-4 min-w-0">
            <button
              type="button"
              onClick={() => navigate('/queue')}
              className="p-1.5 hover:bg-[#F8FAFC] rounded-lg transition-colors flex-shrink-0"
            >
              <ArrowLeft className="w-4 h-4 text-[#64748B]" />
            </button>
            <div className="min-w-0">
              <h2 className="font-semibold text-[#0F172A] truncate">{p?.name ?? 'Patient'}</h2>
              <p className="text-sm text-[#64748B] truncate">{reviewLine}</p>
            </div>
          </div>
          <div className="flex items-center gap-2 flex-shrink-0">
            <button
              type="button"
              onClick={() => navigate(`/intake?patient=${encodeURIComponent(patientId)}`)}
              className="px-3 py-1.5 text-sm border border-[#E2E8F0] rounded-xl hover:bg-[#F8FAFC] transition-colors flex items-center gap-1.5"
            >
              <Upload className="w-3.5 h-3.5" />
              Upload Report
            </button>
            <button
              type="button"
              onClick={() => void onMarkChartReviewed()}
              disabled={markReviewBusy || !patientId}
              className="px-3 py-1.5 text-sm border border-[#E2E8F0] rounded-xl hover:bg-emerald-50 hover:border-emerald-200 transition-colors flex items-center gap-1.5 disabled:opacity-50"
            >
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
              {markReviewBusy ? 'Saving…' : 'Mark reviewed'}
            </button>
            <button
              type="button"
              className="px-3 py-1.5 text-sm border border-[#E2E8F0] rounded-xl hover:bg-[#F8FAFC] transition-colors flex items-center gap-1.5"
            >
              <Plus className="w-3.5 h-3.5" />
              Add Note
            </button>
            <button
              type="button"
              onClick={() => navigate('/tumor-board')}
              className="px-3 py-1.5 text-sm bg-[#2563EB] text-white rounded-xl hover:bg-[#1d4ed8] transition-colors flex items-center gap-1.5"
            >
              <Download className="w-3.5 h-3.5" />
              Tumor board
            </button>
          </div>
        </div>

        <div className="flex items-center gap-4 text-sm text-[#64748B] mb-3 flex-wrap">
          <div className="flex items-center gap-2">
            <span>Review status:</span>
            <span className="font-medium text-[#0F172A]">{p?.review_status ?? '—'}</span>
          </div>
          {p?.last_chart_review_at ? (
            <div className="flex items-center gap-2">
              <span>Last chart review:</span>
              <span className="font-medium text-[#0F172A]">{formatReviewWindowBoundary(p.last_chart_review_at)}</span>
            </div>
          ) : null}
        </div>

        {error && (
          <p className="text-sm text-red-600 bg-red-50 border border-red-100 rounded-lg px-3 py-2 mb-2">{error}</p>
        )}
        {p?.disclaimer && <p className="text-xs text-[#94A3B8] mb-2">{p.disclaimer}</p>}

        <form
          className="relative mb-2"
          onSubmit={(e) => {
            e.preventDefault();
            void runChartSearch(chartQuery);
          }}
        >
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#94A3B8] pointer-events-none" />
          <input
            type="text"
            value={chartQuery}
            onChange={(e) => setChartQuery(e.target.value)}
            placeholder="Ask this chart…"
            className="w-full pl-9 pr-24 py-2.5 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] text-sm text-[#0F172A] placeholder:text-[#94A3B8] focus:outline-none focus:ring-2 focus:ring-[#2563EB]/25 focus:border-[#2563EB]"
            aria-label="Ask this chart"
          />
          <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
            <button
              type="submit"
              disabled={chartSearchLoading || !chartQuery.trim()}
              className="px-3 py-1.5 text-xs font-medium bg-[#2563EB] text-white rounded-lg hover:bg-[#1d4ed8] disabled:opacity-50 disabled:pointer-events-none transition-colors"
            >
              {chartSearchLoading ? '…' : 'Search'}
            </button>
          </div>
        </form>
        <p className="text-[11px] text-[#94A3B8] mb-2">
          Evidence retrieval from this patient&apos;s chart text only; findings are source-backed excerpts where
          indicated.{' '}
          <button
            type="button"
            className="text-[#2563EB] hover:underline"
            onClick={() => navigate(`/search?patient=${encodeURIComponent(patientId)}`)}
          >
            Open full evidence search
          </button>
        </p>

        <div className="flex flex-wrap gap-1.5">
          {chipPrompts.map((q) => (
            <button
              key={q}
              type="button"
              onClick={() => {
                setChartQuery(q);
                void runChartSearch(q);
              }}
              className="px-2.5 py-1 text-xs bg-[#F1F5F9] text-[#64748B] rounded-lg hover:bg-[#E2E8F0] hover:text-[#0F172A] transition-colors"
            >
              {q}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-12 gap-4">
        <div className="col-span-3 bg-white rounded-2xl border border-[#E2E8F0] p-4">
          <h3 className="font-semibold text-[#0F172A] mb-3 text-sm">Timeline</h3>

          <div className="flex flex-wrap gap-1.5 mb-4">
            {['All', 'Labs', 'Imaging', 'Notes', 'Treatment', 'Pathology'].map((filter) => (
              <button
                key={filter}
                type="button"
                onClick={() => setTimelineFilter(filter)}
                className={`px-2 py-1 text-xs rounded transition-colors ${
                  timelineFilter === filter
                    ? 'bg-[#2563EB] text-white'
                    : 'bg-[#F8FAFC] text-[#64748B] hover:bg-[#E2E8F0]'
                }`}
              >
                {filter}
              </button>
            ))}
          </div>

          <div className="space-y-3">
            {filteredTimeline.map((event, i) => (
              <div
                key={i}
                className="relative pl-4 pb-3 border-l-2 border-[#E2E8F0] last:border-0 last:pb-0 cursor-pointer"
                onClick={() => {
                  setSelectedEvidence(null);
                  setSelectedChartHit(null);
                }}
                role="presentation"
              >
                <div className="absolute -left-1.5 top-0 w-3 h-3 rounded-full bg-white border-2 border-[#2563EB]" />
                <p className="text-xs text-[#94A3B8] mb-1">{formatTimelineDate(event.date)}</p>
                <p className="text-sm font-medium text-[#0F172A] mb-0.5">{event.title || event.type || 'Event'}</p>
                <p className="text-xs text-[#64748B]">{event.detail || ''}</p>
              </div>
            ))}
            {!payload && !error && <p className="text-xs text-[#64748B]">Loading timeline…</p>}
          </div>
        </div>

        <div className="col-span-5 space-y-3">
          {payload?.what_changed_window ? (
            <div className="bg-white rounded-2xl border border-[#E2E8F0] p-4">
              <h3 className="font-semibold text-[#0F172A] text-sm">{payload.what_changed_window.label}</h3>
              <p className="text-xs text-[#64748B] mt-0.5 mb-2">
                Review window:{' '}
                <span className="font-medium text-[#334155]">
                  {formatReviewWindowBoundary(payload.what_changed_window.start)} →{' '}
                  {formatReviewWindowBoundary(payload.what_changed_window.end)}
                </span>
              </p>
              <p className="text-[11px] text-[#94A3B8] mb-3 leading-relaxed">
                Comparison of dated reports, observations, notes, treatments, and source-backed flags within this window.
                Language is documentary only — not diagnosis or treatment guidance.
              </p>
              <p className="text-[11px] font-medium text-[#64748B] mb-3">
                Generated from source-backed evidence. Clinician review required.
              </p>
              {(payload.what_changed_summary?.length ?? 0) > 0 ? (
                <ul className="space-y-2.5">
                  {payload.what_changed_summary!.map((b, idx) => (
                    <li key={idx} className="text-sm text-[#334155] leading-snug flex flex-col gap-1.5">
                      <span>
                        <span className="font-semibold text-[#0F172A]">{idx + 1}.</span> {b.text}
                      </span>
                      {(b.sources?.length ?? 0) > 0 ? (
                        <div className="flex flex-wrap gap-1">
                          {b.sources!.slice(0, 6).map((s, j) => (
                            <span
                              key={j}
                              className="text-[10px] font-medium px-2 py-0.5 rounded-md bg-[#F8FAFC] border border-[#E2E8F0] text-[#475569]"
                              title={[s.kind, s.label, s.id != null ? `#${s.id}` : ''].filter(Boolean).join(' · ')}
                            >
                              {(s.kind ? `${String(s.kind).replace(/_/g, ' ')} · ` : '') + (s.label || 'Source')}
                            </span>
                          ))}
                        </div>
                      ) : null}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-[#64748B]">No condensed highlights matched this window.</p>
              )}
            </div>
          ) : null}

          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-4">
            <h3 className="font-semibold text-[#0F172A] text-sm">Evidence Board</h3>
            <p className="text-xs text-[#64748B] mt-0.5 mb-1 font-medium">
              Prioritized source-backed observations from this chart.
            </p>
            <p className="text-xs text-[#64748B] mb-3 leading-relaxed">
              These findings summarize what changed and what may warrant review. Click any item to inspect the exact
              source trail.
            </p>

            {payload?.evidence_summary ? (
              <div className="mb-4 rounded-xl border border-[#E8EDF5] bg-gradient-to-br from-[#FAFBFD] to-[#F8FAFC] px-3 py-2.5">
                <div className="flex flex-wrap items-center justify-between gap-2 mb-1.5">
                  <span className="text-[10px] font-semibold uppercase tracking-wide text-[#64748B]">
                    Evidence summary
                  </span>
                  <span className="text-[10px] font-medium text-[#475569]">
                    {payload.evidence_summary.source_count} linked source
                    {payload.evidence_summary.source_count === 1 ? '' : 's'}
                  </span>
                </div>
                <p className="text-xs text-[#334155] leading-relaxed">{payload.evidence_summary.summary_text}</p>
                {(payload.evidence_summary.themes?.length ?? 0) > 0 ? (
                  <div className="mt-2 flex flex-wrap gap-1.5">
                    {payload.evidence_summary.themes.map((th) => (
                      <span
                        key={th.key}
                        className="text-[11px] font-medium px-2 py-0.5 rounded-md bg-white border border-[#E2E8F0] text-[#475569]"
                      >
                        {th.label} ×{th.count}
                      </span>
                    ))}
                  </div>
                ) : null}
              </div>
            ) : null}

            {payload?.missing_data_summary ? (
              <p className="text-[11px] text-[#64748B] mb-3 leading-relaxed border-l-2 border-[#E2E8F0] pl-2">
                {payload.missing_data_summary}
              </p>
            ) : null}

            {(chartSearchRan || chartSearchLoading) && (
              <div className="mb-6 pb-6 border-b border-[#E2E8F0]">
                <h4 className="font-semibold text-[#0F172A] text-sm mb-1">Search results from this chart</h4>
                <p className="text-xs text-[#64748B] mb-3">
                  Results from semantic and keyword retrieval over this chart. Source-backed excerpts only — clinician
                  review required.
                </p>
                {chartDisclaimer && (
                  <p className="text-[11px] text-[#94A3B8] mb-2 border-l-2 border-[#E2E8F0] pl-2">{chartDisclaimer}</p>
                )}
                {chartSearchLoading && <p className="text-sm text-[#64748B]">Searching…</p>}
                {chartSearchError && (
                  <p className="text-sm text-red-600 bg-red-50 border border-red-100 rounded-lg px-3 py-2">{chartSearchError}</p>
                )}
                {!chartSearchLoading && !chartSearchError && chartHits.length === 0 && (
                  <p className="text-sm text-[#64748B]">No matching excerpts for this question.</p>
                )}
                <div className="space-y-3 mt-3">
                  {chartHits.map((hit, idx) => {
                    const selected = selectedChartHit !== null && hitsSame(hit, selectedChartHit);
                    const rk = resultKindLabel(hit.result_kind);
                    const sim =
                      hit.similarity_score != null && hit.similarity_score !== undefined
                        ? Number(hit.similarity_score).toFixed(4)
                        : null;
                    return (
                      <div
                        key={`${hit.source_kind}-${hit.source_id}-${hit.chunk_index}-${idx}`}
                        role="button"
                        tabIndex={0}
                        onClick={() => selectChartHit(hit)}
                        onKeyDown={(ke) => {
                          if (ke.key === 'Enter' || ke.key === ' ') {
                            ke.preventDefault();
                            selectChartHit(hit);
                          }
                        }}
                        className={`p-4 rounded-lg border cursor-pointer transition-all border-l-4 border-l-[#64748B] ${
                          selected
                            ? 'border-[#2563EB] bg-[#F8FAFC]'
                            : 'border-[#E2E8F0] hover:border-[#94A3B8]'
                        }`}
                      >
                        <div className="flex flex-wrap items-center gap-2 mb-2">
                          <span
                            className={`text-[10px] font-semibold uppercase tracking-wide px-2 py-0.5 rounded-full border ${resultKindPillClass(hit.result_kind)}`}
                          >
                            {rk}
                          </span>
                          <span className="text-xs font-medium text-[#0F172A]">
                            {hit.source_type ?? hit.source_kind ?? 'Source'}
                          </span>
                          {hit.source_date ? (
                            <span className="text-xs text-[#64748B]">{formatTimelineDate(hit.source_date)}</span>
                          ) : null}
                        </div>
                        <p className="text-sm text-[#0F172A] leading-relaxed mb-2">{hit.matched_snippet ?? '—'}</p>
                        {hit.extracted_value ? (
                          <p className="text-xs font-semibold text-[#0F172A] mb-2">
                            Extracted: {hit.extracted_value}
                          </p>
                        ) : null}
                        {hit.why_matched ? (
                          <p className="text-xs text-[#64748B] mb-3">
                            <span className="font-medium text-[#475569]">Why matched: </span>
                            {hit.why_matched}
                          </p>
                        ) : null}
                        <div className="flex flex-wrap items-center justify-between gap-2">
                          {sim != null ? (
                            <span className="text-[11px] text-[#94A3B8]">Similarity {sim}</span>
                          ) : (
                            <span />
                          )}
                          <button
                            type="button"
                            className="text-xs text-[#2563EB] hover:underline font-semibold"
                            onClick={(e) => {
                              e.stopPropagation();
                              selectChartHit(hit);
                            }}
                          >
                            View Source Trail →
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {payload && sourceObs.length > 0 && (
              <div className="mb-4 rounded-xl border border-[#E2E8F0] bg-[#FAFBFC] px-3 py-2.5">
                <p className="text-[10px] font-semibold uppercase tracking-wide text-[#94A3B8] mb-2">At a glance</p>
                <div className="flex flex-wrap gap-x-5 gap-y-2 text-xs text-[#334155]">
                  <div>
                    <span className="text-[#94A3B8] block">Review status</span>
                    <span className="font-semibold text-[#0F172A]">{patientReviewLabel(atGlance.reviewStatus)}</span>
                  </div>
                  <div>
                    <span className="text-[#94A3B8] block">Source-backed items</span>
                    <span className="font-semibold text-[#0F172A]">{atGlance.total}</span>
                  </div>
                  <div>
                    <span className="text-[#94A3B8] block">High priority</span>
                    <span className="font-semibold text-[#0F172A]">{atGlance.highPriority}</span>
                    <span className="text-[10px] text-[#94A3B8] ml-1">(needs review)</span>
                  </div>
                  <div>
                    <span className="text-[#94A3B8] block">Latest finding</span>
                    <span className="font-semibold text-[#0F172A]">
                      {atGlance.latestIso ? formatTimelineDate(atGlance.latestIso) : '—'}
                    </span>
                  </div>
                </div>
                {atGlance.themes.length > 0 && (
                  <div className="mt-2.5 flex flex-wrap gap-1.5">
                    {atGlance.themes.map((t) => (
                      <span
                        key={t}
                        className="px-2 py-0.5 rounded-md bg-white border border-[#E2E8F0] text-[11px] font-medium text-[#475569]"
                      >
                        {t}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            )}

            {sourceObs.length === 0 && payload && (
              <p className="text-sm text-[#64748B]">No source-backed observations for this patient yet.</p>
            )}

            {renderClinicalSection('Needs Review', clinicalGrouped.needs_review, 2)}
            {renderClinicalSection('Monitor / Follow Up', clinicalGrouped.watch, 0)}
            {renderClinicalSection('Informational', clinicalGrouped.info, 0)}
          </div>
        </div>

        <div className="col-span-4 bg-white rounded-2xl border border-[#E2E8F0] p-4">
          <h3 className="font-semibold text-[#0F172A] mb-4 text-sm">Source Viewer</h3>

          {!selectedClinical && !selectedChartHit ? (
            <div className="flex flex-col items-center justify-center py-16 text-center">
              <FileText className="w-12 h-12 text-[#E2E8F0] mb-3" />
              <p className="text-sm text-[#64748B] max-w-xs leading-relaxed">
                Select an evidence card or a chart search result to view rationale, excerpts, and source metadata.
                Clinician review required.
              </p>
            </div>
          ) : (
            <Tabs value={sourceViewerTab} onValueChange={(v) => setSourceViewerTab(v as "trail" | "viz")}>
              <TabsList className="mb-3" aria-label="Source viewer modes">
                <TabsTrigger value="trail">Source Trail</TabsTrigger>
                <TabsTrigger value="viz">Visualization</TabsTrigger>
              </TabsList>

              <TabsContent value="trail">
                {selectedChartHit ? (
                  <div className="space-y-4">
                    <div className="pb-3 border-b border-[#E2E8F0]">
                      <div className="flex flex-wrap items-center gap-2 mb-1">
                        <span
                          className={`text-[10px] font-semibold uppercase tracking-wide px-2 py-0.5 rounded-full border ${resultKindPillClass(selectedChartHit.result_kind)}`}
                        >
                          {resultKindLabel(selectedChartHit.result_kind)}
                        </span>
                        <p className="font-medium text-[#0F172A] text-sm">
                          {selectedChartHit.source_type ?? selectedChartHit.source_kind ?? 'Chart excerpt'}
                        </p>
                      </div>
                      <p className="text-xs text-[#64748B]">
                        Source date:{' '}
                        {selectedChartHit.source_date ? formatTimelineDate(selectedChartHit.source_date) : '—'}
                        {selectedChartHit.similarity_score != null && selectedChartHit.similarity_score !== undefined
                          ? ` · Similarity ${Number(selectedChartHit.similarity_score).toFixed(4)}`
                          : ''}
                      </p>
                    </div>

                    <div className="bg-[#F8FAFC] rounded-lg p-4 border border-[#E2E8F0]">
                      <p className="text-xs uppercase tracking-wide text-[#94A3B8] mb-2 font-medium">Evidence excerpt</p>
                      <p className="text-sm text-[#0F172A] leading-relaxed whitespace-pre-wrap">
                        {selectedChartHit.matched_snippet ?? '—'}
                      </p>
                    </div>

                    {selectedChartHit.extracted_value ? (
                      <div>
                        <p className="text-xs uppercase tracking-wide text-[#94A3B8] mb-2 font-medium">Extracted value</p>
                        <p className="text-sm font-semibold text-[#0F172A]">{selectedChartHit.extracted_value}</p>
                      </div>
                    ) : null}

                    <div>
                      <p className="text-xs uppercase tracking-wide text-[#94A3B8] mb-2 font-medium">Why this matched</p>
                      <p className="text-sm text-[#64748B] leading-relaxed">{selectedChartHit.why_matched ?? '—'}</p>
                    </div>

                    <div className="flex flex-wrap gap-2">
                      {selectedChartHit.source_url ? (
                        <a
                          href={selectedChartHit.source_url}
                          className="inline-flex items-center px-3 py-1.5 text-xs font-medium text-[#2563EB] border border-[#E2E8F0] rounded-lg hover:bg-[#F8FAFC]"
                        >
                          Open linked record
                        </a>
                      ) : null}
                      <button
                        type="button"
                        onClick={() =>
                          navigate(
                            `/search?patient=${encodeURIComponent(patientId)}&q=${encodeURIComponent(chartQuery)}`,
                          )
                        }
                        className="inline-flex items-center px-3 py-1.5 text-xs font-medium text-[#64748B] border border-[#E2E8F0] rounded-lg hover:bg-[#F8FAFC]"
                      >
                        View in evidence search
                      </button>
                    </div>

                    <div className="p-2.5 bg-blue-50 rounded-lg border border-blue-100">
                      <p className="text-xs text-blue-800 leading-relaxed">
                        Evidence found in chart text; excerpt shown for clinician review only. Source-backed where tied to an
                        indexed record. Does not replace independent clinical judgment.
                      </p>
                    </div>
                  </div>
                ) : selectedClinical ? (
                  <div className="space-y-4">
                    <div className="pb-3 border-b border-[#E2E8F0]">
                      <span
                        className={`inline-flex mb-2 text-[10px] font-semibold uppercase tracking-wide px-2 py-0.5 rounded-md border ${
                          selectedClinical.raw.status === 'needs_review'
                            ? 'bg-red-50 text-red-800 border-red-100'
                            : selectedClinical.raw.status === 'watch'
                              ? 'bg-amber-50 text-amber-900 border-amber-100'
                              : 'bg-slate-50 text-slate-700 border-slate-200'
                        }`}
                      >
                        {selectedClinical.statusBadge}
                      </span>
                      <p className="font-semibold text-[#0F172A] mb-1 text-sm leading-snug">{selectedClinical.headline}</p>
                      <p className="text-[11px] text-[#64748B]">
                        Chart review status: {patientReviewLabel(p?.review_status)} · Evidence found in source documents
                      </p>
                    </div>

                    {selectedClinical.keyFact ? (
                      <div>
                        <p className="text-xs uppercase tracking-wide text-[#94A3B8] mb-2 font-medium">
                          Key extracted detail
                        </p>
                        <p className="text-sm font-semibold text-[#0F172A] tracking-tight">{selectedClinical.keyFact}</p>
                      </div>
                    ) : null}

                    <div className="bg-[#F8FAFC] rounded-lg p-4 border border-[#E2E8F0]">
                      <p className="text-xs uppercase tracking-wide text-[#94A3B8] mb-2 font-medium">
                        Why this surfaced
                      </p>
                      <p className="text-sm text-[#0F172A] leading-relaxed">{selectedClinical.whySurfaced}</p>
                    </div>

                    <div>
                      <p className="text-xs uppercase tracking-wide text-[#94A3B8] mb-2 font-medium">
                        Exact source excerpts
                      </p>
                      {(selectedClinical.raw.linked_evidence_items ?? []).length === 0 ? (
                        <p className="text-xs text-[#64748B]">
                          Linked excerpts will appear here when evidence items are attached. May warrant clinician review.
                        </p>
                      ) : (
                        <ul className="space-y-3">
                          {(selectedClinical.raw.linked_evidence_items ?? []).map((item) => {
                            const linkedObs: WorkspaceObservationRow | undefined =
                              item.source_type === 'observation' && item.source_id != null
                                ? observations.find((o) => o.id === item.source_id)
                                : undefined;
                            return (
                              <li key={item.id} className="text-xs bg-[#F8FAFC] rounded-lg p-3 border border-[#E2E8F0]">
                                <p className="font-semibold text-[#0F172A] text-sm mb-1">{item.title}</p>
                                <p className="text-[11px] text-[#64748B] mb-2">
                                  {sourceTypeLabel(item.source_type)}
                                  {item.evidence_date ? ` · ${formatTimelineDate(item.evidence_date)}` : ''}
                                  {item.confidence != null ? ` · Confidence ${item.confidence}` : ''}
                                </p>
                                <p className="text-sm text-[#0F172A] leading-relaxed whitespace-pre-wrap">{item.snippet}</p>
                                {linkedObs ? (
                                  <div className="mt-2 pt-2 border-t border-[#E2E8F0] text-[11px] text-[#475569] space-y-0.5">
                                    <p>
                                      <span className="font-medium text-[#0F172A]">Observation:</span> {linkedObs.name}{' '}
                                      {linkedObs.value_text ??
                                        (linkedObs.value_number != null ? String(linkedObs.value_number) : '')}{' '}
                                      {linkedObs.unit ?? ''}
                                    </p>
                                    <p>
                                      Confirmation: <span className="font-medium">{linkedObs.confirmation_status}</span>
                                      {linkedObs.observed_at
                                        ? ` · Observed ${formatTimelineDate(linkedObs.observed_at)}`
                                        : ''}
                                    </p>
                                    {linkedObs.source_snippet ? (
                                      <p className="text-[#64748B] italic mt-1">&quot;{linkedObs.source_snippet}&quot;</p>
                                    ) : null}
                                  </div>
                                ) : null}
                              </li>
                            );
                          })}
                        </ul>
                      )}
                    </div>

                    {selectedClinical.raw.reason?.startsWith('__rule__:') ? (
                      <details className="text-[11px] text-[#94A3B8]">
                        <summary className="cursor-pointer hover:text-[#64748B]">Technical reference</summary>
                        <pre className="mt-1 whitespace-pre-wrap font-mono text-[10px]">{selectedClinical.raw.reason}</pre>
                      </details>
                    ) : null}

                    <div className="p-2.5 bg-blue-50 rounded-lg border border-blue-100">
                      <p className="text-xs text-blue-800 leading-relaxed">
                        Source-backed observation extracted from this chart. May warrant clinician review. Not a diagnosis or
                        treatment recommendation.
                      </p>
                    </div>
                  </div>
                ) : null}
              </TabsContent>

              <TabsContent value="viz">
                {selectedClinical ? (
                  <div className="space-y-3">
                    <SourceVisualization
                      sourceObservation={selectedClinical.raw}
                      observations={observations}
                      timeline={timeline}
                    />
                    <div className="p-2.5 bg-blue-50 rounded-lg border border-blue-100">
                      <p className="text-xs text-blue-800 leading-relaxed">
                        Generated from source-backed evidence. Clinician review required.
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="p-4 rounded-lg border border-[#E2E8F0] bg-[#F8FAFC]">
                    <p className="text-sm text-[#64748B]">No visualization available for this observation yet.</p>
                  </div>
                )}
              </TabsContent>
            </Tabs>
          )}
        </div>
      </div>
    </div>
  );
}
