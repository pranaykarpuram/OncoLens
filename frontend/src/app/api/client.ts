/** Fetch JSON from Django `/api/*` — Vite dev server proxies `/api` to :8000. */

export async function apiJson<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (init.body && typeof init.body === 'string' && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }
  const res = await fetch(path, {
    ...init,
    credentials: 'include',
    headers,
  });
  const text = await res.text();
  let data: unknown = null;
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      throw new Error(`Non-JSON response (${res.status}): ${text.slice(0, 200)}`);
    }
  }
  if (!res.ok) {
    const detail =
      typeof data === 'object' && data !== null && 'detail' in data
        ? String((data as { detail: unknown }).detail)
        : res.statusText;
    throw new Error(detail || `Request failed (${res.status})`);
  }
  return data as T;
}

export async function apiLogin(username: string, password: string) {
  return apiJson<{
    ok: boolean;
    username?: string;
    role?: string;
    disclaimer?: string;
  }>('/api/auth/login/', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  });
}

export async function apiSession() {
  return apiJson<{ authenticated: boolean; username?: string; role?: string }>('/api/auth/session/', {});
}

export type ReviewQueuePatientQueueCounts = {
  unreviewed_source_flags: number;
  unconfirmed_observations: number;
  pending_reports: number;
  new_since_last_review: number | null;
};

export type ReviewQueueResponse = {
  metrics: {
    new_reports_count: number;
    needs_confirmation_count: number;
    patients_with_new_evidence_count: number;
    missing_recent_labs_count: number;
    patients_pending_chart_review?: number;
  };
  patients: Array<{
    id: number;
    name: string;
    mrn: string;
    diagnosis?: string;
    stage?: string;
    treatment?: string;
    status?: string;
    reasons?: string[];
    newestEvidence?: { type: string; title: string } | null;
    last_chart_review_at?: string | null;
    queue_counts?: ReviewQueuePatientQueueCounts;
  }>;
};

export async function fetchReviewQueue() {
  return apiJson<ReviewQueueResponse>('/api/review-queue/');
}

export type PatientsApiResponse = {
  patients: Array<{
    id: number;
    name: string;
    mrn: string;
    age?: number;
    sex?: string;
    diagnosis?: string;
    stage?: string;
    treatment?: string;
    status?: string;
    ca199?: number | null;
    trend?: string;
    biomarkers?: string;
    updated?: string;
  }>;
};

export async function fetchPatients(q?: string) {
  const qs = q?.trim() ? `?q=${encodeURIComponent(q.trim())}` : '';
  return apiJson<PatientsApiResponse>(`/api/patients/${qs}`);
}

export type WorkspaceLinkedEvidenceItem = {
  id: number;
  title: string;
  snippet: string;
  evidence_date?: string | null;
  source_type: string;
  source_id?: number | null;
  confidence?: number;
};

export type WorkspaceObservationRow = {
  id: number;
  observation_type: string;
  name: string;
  value_text?: string;
  value_number?: number | null;
  unit?: string;
  observed_at?: string | null;
  source_snippet?: string;
  confidence?: number;
  confirmation_status?: string;
  report_id?: number | null;
};

export type WorkspaceSourceBackedObservation = {
  id: number;
  title: string;
  explanation: string;
  status: string;
  reason: string;
  reviewed: boolean;
  evidence_json?: Record<string, unknown>;
  linked_evidence_items?: WorkspaceLinkedEvidenceItem[];
  created_at?: string;
};

export type WorkspaceWhatChangedSource = {
  kind?: string;
  label?: string;
  id?: number;
};

export type WorkspaceWhatChangedBullet = {
  text: string;
  sources: WorkspaceWhatChangedSource[];
};

export type WorkspaceEvidenceSummaryTheme = {
  key: string;
  label: string;
  count: number;
};

export type WorkspaceEvidenceSummary = {
  summary_text: string;
  themes: WorkspaceEvidenceSummaryTheme[];
  source_count: number;
  source_ids: number[];
  profile_id?: string;
};

export type WorkspaceWhatChangedWindow = {
  start: string;
  end: string;
  label: string;
  mode: string;
};

export type WorkspaceEvidenceResponse = {
  patient: {
    id: number;
    name: string;
    mrn: string;
    review_status: string;
    primary_diagnosis?: string;
    cancer_stage?: string;
    disclaimer?: string;
    last_chart_review_at?: string | null;
  };
  observations: WorkspaceObservationRow[];
  source_backed_observations: WorkspaceSourceBackedObservation[];
  timeline: Array<{ date?: string; type?: string; title?: string; detail?: string }>;
  what_changed_window?: WorkspaceWhatChangedWindow;
  what_changed_summary?: WorkspaceWhatChangedBullet[];
  evidence_summary?: WorkspaceEvidenceSummary;
  missing_data_summary?: string | null;
};

export async function fetchPatientEvidence(patientId: string | number) {
  return apiJson<WorkspaceEvidenceResponse>(`/api/patients/${patientId}/evidence/`);
}

export async function markPatientReviewed(patientId: string | number) {
  return apiJson<{
    ok: boolean;
    patient: {
      id: number;
      name: string;
      mrn: string;
      review_status: string;
      primary_diagnosis?: string;
      cancer_stage?: string;
      last_chart_review_at: string;
    };
  }>(`/api/patients/${patientId}/mark-reviewed/`, { method: 'POST', body: '{}' });
}

export type EvidenceSearchHit = {
  patient: { id: number; name: string; mrn: string };
  source_kind?: string;
  source_type?: string;
  matched_snippet?: string;
  extracted_value?: string;
  why_matched?: string;
  confidence?: number;
  source_url?: string;
  workspace_url?: string;
  rank_hint?: number;
  similarity_score?: number | null;
  source_date?: string | null;
  result_kind?: string;
  source_id?: number | null;
  chunk_index?: number | null;
};

export type EvidenceSearchResponse = {
  results: EvidenceSearchHit[];
  q: string;
  disclaimer?: string;
  suggested_terms?: string[];
};

export async function fetchEvidenceSearch(
  q: string,
  patient?: string,
  options?: { top_k?: number },
): Promise<EvidenceSearchResponse> {
  const params = new URLSearchParams({ q });
  if (patient) params.set('patient', patient);
  if (options?.top_k != null) params.set('top_k', String(options.top_k));
  return apiJson<EvidenceSearchResponse>(`/api/evidence/search/?${params}`);
}

export async function submitReportIntake(body: {
  patient: number;
  report_type: string;
  report_date?: string;
  title?: string;
  raw_text: string;
}) {
  return apiJson<{
    report_id: number;
    parse_status: string;
    extraction_count: number;
    review_extraction_url_hint?: string;
  }>('/api/reports/intake/', {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

export async function generateBrief(patientId: number) {
  return apiJson<{ brief: Record<string, unknown>; patient_id: number; disclaimer?: string }>(
    `/api/patients/${patientId}/brief/`,
    {
      method: 'POST',
      body: JSON.stringify({}),
    },
  );
}

export async function fetchLatestBrief(patientId: number) {
  return apiJson<{ brief: Record<string, unknown> | null; patient_id: number }>(`/api/patients/${patientId}/brief/`, {});
}

export async function fetchAdminSummary() {
  return apiJson<{
    user_total: number;
    patient_total: number;
    reports_parsed: number;
    unconfirmed_extractions: number;
    active_observations: number;
    disclaimer?: string;
  }>('/api/admin/summary/');
}
