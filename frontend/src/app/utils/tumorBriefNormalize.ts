/**
 * Parsing and display helpers for tumor board brief payloads (avoid JSON.stringify in UI).
 */

export const STANDARD_BRIEF_DISCLAIMER =
  'Generated from source documents for clinician review. Not a diagnosis or treatment recommendation.';

export type BriefTimelineEvent = {
  date?: string;
  type?: string;
  kind?: string;
  title?: string;
  detail?: string;
};

export type BriefEvidenceItem = {
  title?: string;
  status?: string;
  explanation_excerpt?: string;
  disclaimer?: string;
};

export type BriefMissingRow = {
  bullet?: string;
  headline?: string;
  explanation?: string;
  disclaimer?: string;
};

export type BriefSourceDocument = {
  type?: string;
  title?: string;
  report_date?: string;
  date?: string;
  snippet?: string;
  note?: string;
};

export type NormalizedBrief = {
  case_summary: string;
  treatment_course: string;
  key_timeline_events: BriefTimelineEvent[];
  evidence_of_change: BriefEvidenceItem[];
  missing_or_unconfirmed_data: BriefMissingRow[];
  source_documents: BriefSourceDocument[];
};

export function safeJsonParse<T>(raw: unknown): T | null {
  if (raw == null || typeof raw === 'object') return (raw as T) ?? null;
  if (typeof raw !== 'string') return null;
  const s = raw.trim();
  if (!(s.startsWith('{') || s.startsWith('['))) return null;
  try {
    return JSON.parse(s) as T;
  } catch {
    return null;
  }
}

export function normalizeBriefArray<T>(val: unknown): T[] {
  if (Array.isArray(val)) return val as T[];
  const nested = safeJsonParse<T[]>(val);
  return Array.isArray(nested) ? nested : [];
}

/** Remove trailing duplicate standard disclaimer so we can show it once in the header. */
export function stripTrailingBriefDisclaimer(text: string): string {
  let t = (text || '').trimEnd();
  const d = STANDARD_BRIEF_DISCLAIMER;
  while (t.endsWith('\n\n' + d) || t.endsWith('\n' + d) || t.endsWith(d)) {
    if (t.endsWith('\n\n' + d)) t = t.slice(0, -(d.length + 2)).trimEnd();
    else if (t.endsWith('\n' + d)) t = t.slice(0, -(d.length + 1)).trimEnd();
    else if (t.endsWith(d)) t = t.slice(0, -d.length).trimEnd();
  }
  return t.trim();
}

export function coerceTimelineEvent(raw: unknown): BriefTimelineEvent | null {
  if (!raw || typeof raw !== 'object') {
    const s = typeof raw === 'string' ? raw.trim() : '';
    return s ? { title: s, detail: '' } : null;
  }
  const o = raw as Record<string, unknown>;
  return {
    date: typeof o.date === 'string' ? o.date : undefined,
    type: typeof o.type === 'string' ? o.type : typeof o.kind === 'string' ? o.kind : undefined,
    kind: typeof o.kind === 'string' ? o.kind : undefined,
    title: typeof o.title === 'string' ? o.title : '',
    detail: typeof o.detail === 'string' ? o.detail : typeof o.desc === 'string' ? (o.desc as string) : '',
  };
}

export function coerceEvidenceRow(raw: unknown): BriefEvidenceItem | null {
  if (!raw || typeof raw !== 'object') return null;
  const o = raw as Record<string, unknown>;
  return {
    title: typeof o.title === 'string' ? o.title : 'Evidence item',
    status: typeof o.status === 'string' ? o.status : 'info',
    explanation_excerpt: typeof o.explanation_excerpt === 'string' ? o.explanation_excerpt : '',
    disclaimer: typeof o.disclaimer === 'string' ? o.disclaimer : undefined,
  };
}

export function coerceMissingRow(raw: unknown): BriefMissingRow | null {
  if (raw == null) return null;
  if (typeof raw === 'string') return { headline: raw, bullet: raw };
  if (typeof raw !== 'object') return { headline: String(raw) };
  const o = raw as Record<string, unknown>;
  const bullet = typeof o.bullet === 'string' ? o.bullet : '';
  const headline = typeof o.headline === 'string' ? o.headline : bullet;
  return {
    bullet: bullet || headline,
    headline: headline || bullet,
    explanation: typeof o.explanation === 'string' ? o.explanation : '',
    disclaimer: typeof o.disclaimer === 'string' ? o.disclaimer : undefined,
  };
}

export function coerceSourceDoc(raw: unknown): BriefSourceDocument | null {
  if (!raw || typeof raw !== 'object') {
    const s = typeof raw === 'string' ? raw.trim() : '';
    return s ? { title: s } : null;
  }
  const o = raw as Record<string, unknown>;
  return {
    type: typeof o.type === 'string' ? o.type : undefined,
    title: typeof o.title === 'string' ? o.title : 'Document',
    report_date: typeof o.report_date === 'string' ? o.report_date : typeof o.date === 'string' ? o.date : undefined,
    snippet: typeof o.snippet === 'string' ? o.snippet : undefined,
    note: typeof o.note === 'string' ? o.note : undefined,
  };
}

export function normalizeBriefPayload(brief: Record<string, unknown> | null | undefined): NormalizedBrief | null {
  if (!brief) return null;

  let case_summary = typeof brief.case_summary === 'string' ? brief.case_summary : '';
  let treatment_course = typeof brief.treatment_course === 'string' ? brief.treatment_course : '';

  case_summary = stripTrailingBriefDisclaimer(case_summary);
  treatment_course = stripTrailingBriefDisclaimer(treatment_course);

  const timelineRaw = normalizeBriefArray<unknown>(brief.key_timeline_events)
    .map(coerceTimelineEvent)
    .filter(Boolean) as BriefTimelineEvent[];

  const evidenceRaw = normalizeBriefArray<unknown>(brief.evidence_of_change)
    .map(coerceEvidenceRow)
    .filter(Boolean) as BriefEvidenceItem[];

  const missingRaw = normalizeBriefArray<unknown>(brief.missing_or_unconfirmed_data)
    .map(coerceMissingRow)
    .filter(Boolean) as BriefMissingRow[];

  const sourcesRaw = normalizeBriefArray<unknown>(brief.source_documents)
    .map(coerceSourceDoc)
    .filter(Boolean) as BriefSourceDocument[];

  return {
    case_summary,
    treatment_course,
    key_timeline_events: timelineRaw,
    evidence_of_change: evidenceRaw,
    missing_or_unconfirmed_data: missingRaw,
    source_documents: sourcesRaw,
  };
}

export function evidenceStatusBadge(
  status: string | undefined,
): { label: string; kind: 'needs-review' | 'watch' | 'info' } {
  const s = (status || 'info').toLowerCase().replace(/-/g, '_');
  if (s === 'needs_review') return { label: 'Needs review', kind: 'needs-review' };
  if (s === 'watch') return { label: 'Watch', kind: 'watch' };
  return { label: 'Info', kind: 'info' };
}

export function formatBriefDate(iso?: string): string {
  if (!iso) return '—';
  try {
    return new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
  } catch {
    return iso.slice(0, 10);
  }
}

export function timelineTypeLabel(ev: BriefTimelineEvent): string {
  const t = ev.type || ev.kind || '';
  if (!t) return 'Event';
  return t.charAt(0).toUpperCase() + t.slice(1).replace(/_/g, ' ');
}
