"use client";

import React from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type {
  WorkspaceLinkedEvidenceItem,
  WorkspaceObservationRow,
  WorkspaceSourceBackedObservation,
} from "../api/client";

function formatTimelineDate(iso?: string): string {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
  } catch {
    return iso.slice(0, 10);
  }
}

function parseIsoToMs(iso?: string | null): number | null {
  if (!iso) return null;
  const t = Date.parse(iso);
  if (!Number.isFinite(t)) return null;
  return t;
}

function escapeRegExp(s: string): string {
  return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function highlightText(text: string, phrases: string[]): React.ReactNode {
  const cleanPhrases = phrases
    .map((p) => String(p || "").trim())
    .filter((p) => p.length >= 3);
  if (!text || cleanPhrases.length === 0) return text;

  const uniq = Array.from(new Set(cleanPhrases));
  const sorted = uniq.sort((a, b) => b.length - a.length).slice(0, 10);
  const pattern = sorted.map(escapeRegExp).join("|");
  if (!pattern) return text;

  let re: RegExp;
  try {
    re = new RegExp(`(${pattern})`, "gi");
  } catch {
    return text;
  }

  const parts = text.split(re);
  return (
    <>
      {parts.map((part, idx) => {
        const isMatch = sorted.some((p) => part.toLowerCase() === p.toLowerCase());
        if (isMatch) {
          return (
            <mark
              key={idx}
              className="bg-yellow-100 text-yellow-900 px-0.5 rounded"
            >
              {part}
            </mark>
          );
        }
        return <React.Fragment key={idx}>{part}</React.Fragment>;
      })}
    </>
  );
}

type VizKind = "marker_trend" | "imaging_language" | "symptom_language" | "missing_data" | "other";

function inferRuleKind(ej: Record<string, unknown> | undefined): VizKind {
  if (!ej) return "other";
  const rk = ej.rule_kind;
  if (typeof rk === "string") {
    if (rk === "marker_trend" || rk === "imaging_language" || rk === "symptom_language" || rk === "missing_data") return rk;
    return rk as VizKind;
  }
  if (ej.marker != null) return "marker_trend";
  if (ej.needle != null) return "missing_data";
  if (Array.isArray(ej.terms)) return "imaging_language";
  return "other";
}

function pickPhrasesFromEvidenceJson(ej: Record<string, unknown>): string[] {
  const phrases: string[] = [];
  const primary = ej.primary_phrase;
  if (typeof primary === "string" && primary.trim()) phrases.push(primary.trim());
  const terms = ej.terms;
  if (Array.isArray(terms)) {
    for (const t of terms) {
      if (typeof t === "string" && t.trim()) phrases.push(t.trim());
    }
  }
  return phrases.filter((p) => p.length >= 3);
}

function buildMarkerSeriesFromLinkedObs(
  so: WorkspaceSourceBackedObservation,
  linked: WorkspaceLinkedEvidenceItem[] | undefined,
  observations: WorkspaceObservationRow[],
): Array<{ t: number; iso: string; value: number; unit: string; highlighted: boolean }> {
  const ej = (so.evidence_json || {}) as Record<string, unknown>;
  const markerName =
    typeof ej.marker === "string" && ej.marker.trim() ? ej.marker.trim() : undefined;

  const linkedObsIds = (linked || [])
    .filter((it) => it.source_type === "observation" && it.source_id != null)
    .map((it) => it.source_id as number);

  const linkedObsRows = observations
    .filter((o) => linkedObsIds.includes(o.id))
    .filter((o) => o.observed_at && o.value_number != null);

  const usable = linkedObsRows
    .map((o) => {
      const t = parseIsoToMs(o.observed_at);
      if (t == null) return null;
      const unit = (o.unit || "").trim();
      return { t, iso: o.observed_at as string, value: Number(o.value_number), unit };
    })
    .filter((x): x is NonNullable<typeof x> => x != null)
    .sort((a, b) => a.t - b.t);

  // If markerName is present, filter to observation rows that look like the same marker.
  // (In the seeded demo, linked evidence items usually already correspond to the marker run.)
  const filtered = markerName
    ? usable.filter((p) =>
        linkedObsRows.some(
          (o) =>
            o.name.toLowerCase().includes(markerName.toLowerCase()) &&
            o.observed_at === p.iso,
        ),
      )
    : usable;

  const highlightCount =
    typeof ej.measurement_count === "number"
      ? Math.min(2, Math.max(1, Math.min(filtered.length, ej.measurement_count as number)))
      : Math.min(2, filtered.length);

  const highlightedSet = new Set(filtered.slice(Math.max(0, filtered.length - highlightCount)).map((p) => p.iso));
  return filtered.map((p) => ({ ...p, highlighted: highlightedSet.has(p.iso) }));
}

function MarkerTrendView({
  so,
  linked,
  observations,
  timeline,
}: {
  so: WorkspaceSourceBackedObservation;
  linked: WorkspaceLinkedEvidenceItem[] | undefined;
  observations: WorkspaceObservationRow[];
  timeline: Array<{ date?: string; type?: string; title?: string; detail?: string }>;
}) {
  const ej = (so.evidence_json || {}) as Record<string, unknown>;
  const series = buildMarkerSeriesFromLinkedObs(so, linked, observations);
  if (!series.length) {
    return (
      <div className="p-4 rounded-lg border border-[#E2E8F0] bg-[#F8FAFC]">
        <p className="text-sm text-[#64748B]">No trend data points were found for this source-backed observation.</p>
      </div>
    );
  }

  const markerName = typeof ej.marker === "string" && ej.marker.trim() ? ej.marker.trim() : "Marker";
  const unit = series[series.length - 1].unit || "";

  const minT = Math.min(...series.map((p) => p.t));
  const maxT = Math.max(...series.map((p) => p.t));

  const treatmentEvents = (timeline || [])
    .filter((e) => e.type === "treatment" && e.date)
    .map((e) => ({ ...e, t: parseIsoToMs(e.date) }))
    .filter((e) => e.t != null)
    .map((e) => ({ ...e, t: e.t as number }))
    .filter((e) => e.t >= minT && e.t <= maxT)
    .slice(0, 5);

  const showRangeLabel = `${formatTimelineDate(new Date(minT).toISOString())} → ${formatTimelineDate(new Date(maxT).toISOString())}`;

  const CustomDot = (props: any) => {
    const payload = props?.payload;
    const highlighted = Boolean(payload?.highlighted);
    const fill = highlighted ? "#2563EB" : "#93C5FD";
    const r = highlighted ? 4 : 3;
    return <circle cx={props.cx} cy={props.cy} r={r} fill={fill} stroke="#ffffff" strokeWidth={1} />;
  };

  return (
    <div className="space-y-3">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="font-semibold text-[#0F172A] text-sm">{`${markerName} trend over time`}</p>
          <p className="text-xs text-[#64748B] mt-1">Time series (source-backed). {unit ? `Unit: ${unit}. ` : ""}Range: {showRangeLabel}</p>
        </div>
      </div>

      <div className="bg-[#F8FAFC] rounded-lg border border-[#E2E8F0] p-3">
        <ResponsiveContainer width="100%" height={220}>
          <LineChart
            data={series.map((p) => ({ t: p.t, date: p.iso, value: p.value, highlighted: p.highlighted }))}
            margin={{ top: 8, right: 12, bottom: 0, left: 0 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
            <XAxis
              dataKey="t"
              type="number"
              domain={["dataMin", "dataMax"]}
              tickFormatter={(t) => formatTimelineDate(new Date(t).toISOString())}
              stroke="#94A3B8"
              tick={{ fontSize: 12 }}
            />
            <YAxis stroke="#94A3B8" tick={{ fontSize: 12 }} unit={unit ? unit : undefined} />
            <Tooltip
              labelFormatter={(t: any) => formatTimelineDate(new Date(Number(t)).toISOString())}
              formatter={(v: any) => [`${v}`, markerName]}
              contentStyle={{ borderRadius: 12, border: "1px solid #E2E8F0" }}
            />
            {treatmentEvents.map((e) => (
              <ReferenceLine key={e.t} x={e.t} stroke="#94A3B8" strokeDasharray="4 4" />
            ))}
            <Line
              type="monotone"
              dataKey="value"
              stroke="#2563EB"
              strokeWidth={2}
              dot={<CustomDot />}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {treatmentEvents.length > 0 ? (
        <div className="text-xs text-[#475569]">
          <span className="font-medium text-[#0F172A]">Treatment touchpoints within this evidence window:</span>{" "}
          {treatmentEvents.map((e, i) => (
            <span key={e.t}>
              {i > 0 ? " · " : ""}
              {e.title ? `${e.title}` : "Treatment"} ({formatTimelineDate(e.date)})
            </span>
          ))}
        </div>
      ) : null}
    </div>
  );
}

function ImagingComparisonView({
  so,
  linked,
}: {
  so: WorkspaceSourceBackedObservation;
  linked: WorkspaceLinkedEvidenceItem[] | undefined;
}) {
  const ej = (so.evidence_json || {}) as Record<string, unknown>;
  const phrases = pickPhrasesFromEvidenceJson(ej);

  const linkedReports = (linked || [])
    .filter((it) => it.source_type === "report" && it.evidence_date)
    .map((it) => ({ ...it, t: parseIsoToMs(it.evidence_date || undefined) }))
    .filter((it) => it.t != null)
    .map((it) => ({ ...it, t: it.t as number }))
    .sort((a, b) => b.t - a.t);

  if (linkedReports.length === 0) {
    return (
      <div className="p-4 rounded-lg border border-[#E2E8F0] bg-[#F8FAFC]">
        <p className="text-sm text-[#64748B]">No linked imaging report excerpts were attached to this source-backed observation.</p>
      </div>
    );
  }

  const latest = linkedReports[0];
  const prior = linkedReports[1] || linkedReports[0];

  return (
    <div className="space-y-3">
      <div>
        <p className="font-semibold text-[#0F172A] text-sm">Imaging language comparison</p>
        <p className="text-xs text-[#64748B] mt-1">Source-backed report excerpts; highlights are based on evidence JSON matched phrases.</p>
      </div>

      {phrases.length > 0 ? (
        <div className="flex flex-wrap gap-1.5">
          {phrases.slice(0, 6).map((p) => (
            <span key={p} className="text-[11px] font-medium px-2 py-0.5 rounded-md bg-white border border-[#E2E8F0] text-[#475569]">
              {p}
            </span>
          ))}
        </div>
      ) : null}

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <div className="bg-[#F8FAFC] rounded-lg border border-[#E2E8F0] p-3">
          <p className="text-xs uppercase tracking-wide text-[#94A3B8] mb-2 font-medium">Prior imaging report</p>
          <p className="font-semibold text-[#0F172A] text-sm">{prior.title || "Imaging report"}</p>
          <p className="text-xs text-[#64748B] mt-1">{prior.evidence_date ? formatTimelineDate(prior.evidence_date) : "—"}</p>
          <div className="mt-2 text-sm text-[#0F172A] whitespace-pre-wrap leading-relaxed">
            {highlightText(prior.snippet || "", phrases)}
          </div>
        </div>

        <div className="bg-[#F8FAFC] rounded-lg border border-[#E2E8F0] p-3">
          <p className="text-xs uppercase tracking-wide text-[#94A3B8] mb-2 font-medium">Latest imaging report</p>
          <p className="font-semibold text-[#0F172A] text-sm">{latest.title || "Imaging report"}</p>
          <p className="text-xs text-[#64748B] mt-1">{latest.evidence_date ? formatTimelineDate(latest.evidence_date) : "—"}</p>
          <div className="mt-2 text-sm text-[#0F172A] whitespace-pre-wrap leading-relaxed">
            {highlightText(latest.snippet || "", phrases)}
          </div>
        </div>
      </div>

      {typeof ej.primary_phrase === "string" && ej.primary_phrase.trim() ? (
        <div className="p-3 rounded-lg border border-[#E2E8F0] bg-white text-xs text-[#475569]">
          <span className="font-medium text-[#0F172A]">Matched phrase (source-backed):</span> {ej.primary_phrase}
        </div>
      ) : null}
    </div>
  );
}

function SymptomTimelineView({
  so,
  timeline,
}: {
  so: WorkspaceSourceBackedObservation;
  timeline: Array<{ date?: string; type?: string; title?: string; detail?: string }>;
}) {
  const ej = (so.evidence_json || {}) as Record<string, unknown>;
  const terms =
    Array.isArray(ej.terms) ? (ej.terms.filter((t) => typeof t === "string") as string[]) : [];
  const primarySymptoms =
    Array.isArray(ej.primary_symptoms) ? (ej.primary_symptoms.filter((t) => typeof t === "string") as string[]) : [];
  const allTerms = (terms.length ? terms : primarySymptoms).map((t) => String(t).trim()).filter(Boolean);

  const termLower = allTerms.map((t) => t.toLowerCase());
  const matchedTimeline = (timeline || [])
    .filter((e) => e.date && e.detail)
    .map((e) => ({ ...e, detailLower: (e.detail || "").toLowerCase() }))
    .filter((e) => termLower.some((t) => e.detailLower.includes(t)))
    .sort((a, b) => Number(Date.parse(a.date || "")) - Number(Date.parse(b.date || "")))
    .slice(0, 8);

  return (
    <div className="space-y-3">
      <div>
        <p className="font-semibold text-[#0F172A] text-sm">Symptom mentions over time</p>
        <p className="text-xs text-[#64748B] mt-1">Compact note/report mentions where symptom vocabulary terms were detected in source text excerpts.</p>
      </div>

      {allTerms.length > 0 ? (
        <div className="flex flex-wrap gap-1.5">
          {allTerms.slice(0, 6).map((t) => (
            <span key={t} className="text-[11px] font-medium px-2 py-0.5 rounded-md bg-white border border-[#E2E8F0] text-[#475569]">
              {t}
            </span>
          ))}
        </div>
      ) : null}

      {matchedTimeline.length === 0 ? (
        <div className="p-4 rounded-lg border border-[#E2E8F0] bg-[#F8FAFC]">
          <p className="text-sm text-[#64748B]">No note/report excerpts containing the matched symptom terms were found in the workspace timeline.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {matchedTimeline.map((e, i) => {
            const label = e.title || e.type || "Clinical note";
            const dateIso = e.date as string;
            return (
              <div key={`${dateIso}-${i}`} className="bg-[#F8FAFC] rounded-lg border border-[#E2E8F0] p-3">
                <p className="text-xs text-[#94A3B8]">{formatTimelineDate(dateIso)} · {label}</p>
                <div className="mt-1 text-sm text-[#0F172A] whitespace-pre-wrap leading-relaxed">
                  {highlightText((e.detail || "").slice(0, 320), allTerms)}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

function MissingDataReviewView({
  so,
  observations,
}: {
  so: WorkspaceSourceBackedObservation;
  observations: WorkspaceObservationRow[];
}) {
  const ej = (so.evidence_json || {}) as Record<string, unknown>;
  const needle = typeof ej.needle === "string" && ej.needle.trim() ? ej.needle.trim() : "lab";
  const windowDays = typeof ej.window_days === "number" ? ej.window_days : 30;

  // Mirror the missing-data rule heuristic relative to “today”.
  const now = new Date();
  const end = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate(), 0, 0, 0));
  const start = new Date(end.getTime() - windowDays * 24 * 60 * 60 * 1000);

  const startIso = start.toISOString().slice(0, 10);
  const endIso = end.toISOString().slice(0, 10);

  const needleLower = needle.toLowerCase();
  const candidates = observations
    .filter((o) => o.confirmation_status === "confirmed")
    .filter((o) => o.observed_at && (o.name || "").toLowerCase().includes(needleLower))
    .filter((o) => o.value_number != null || (o.value_text || "").trim().length > 0)
    .map((o) => ({ ...o, t: parseIsoToMs(o.observed_at) }))
    .filter((o) => o.t != null)
    .map((o) => ({ ...o, t: o.t as number }))
    .sort((a, b) => b.t - a.t);

  const last = candidates[0];
  const lastIso = last?.observed_at ? String(last.observed_at).slice(0, 10) : null;
  const lastInWindow = lastIso ? lastIso >= startIso : false;

  return (
    <div className="space-y-3">
      <div>
        <p className="font-semibold text-[#0F172A] text-sm">Missing data review</p>
        <p className="text-xs text-[#64748B] mt-1">Source-backed completeness heuristic (chart gaps), requiring clinician review.</p>
      </div>

      <div className="bg-[#F8FAFC] rounded-lg border border-[#E2E8F0] p-3">
        <div className="space-y-1.5 text-sm text-[#0F172A]">
          <p>
            <span className="text-[#94A3B8]">Expected item:</span> <span className="font-semibold">{needle}</span>
          </p>
          <p>
            <span className="text-[#94A3B8]">Review window checked:</span>{" "}
            <span className="font-semibold">
              {startIso} → {endIso} ({windowDays} days)
            </span>
          </p>
          <p>
            <span className="text-[#94A3B8]">Last available result:</span>{" "}
            <span className="font-semibold">{lastIso ? lastIso : "—"}</span>
          </p>
        </div>

        <div className="mt-3 text-xs text-[#475569]">
          <div className="flex items-center gap-2">
            <span className="inline-flex w-5 h-5 items-center justify-center rounded border border-[#E2E8F0] bg-white">
              {lastInWindow ? "✓" : "·"}
            </span>
            <span>
              {lastInWindow ? "A confirmed recent result appears to exist within the window." : "No confirmed recent result was found within the window."}
            </span>
          </div>
          <p className="mt-2">
            {lastIso ? "The chart contains older results, but the heuristic window had no confirmed matches." : "The chart had no confirmed matching observations to extract within the heuristic window."}
          </p>
        </div>
      </div>
    </div>
  );
}

export function SourceVisualization({
  sourceObservation,
  observations,
  timeline,
}: {
  sourceObservation: WorkspaceSourceBackedObservation;
  observations: WorkspaceObservationRow[];
  timeline: Array<{ date?: string; type?: string; title?: string; detail?: string }>;
}) {
  const linked = sourceObservation.linked_evidence_items;
  const ej = (sourceObservation.evidence_json || {}) as Record<string, unknown>;
  const kind = inferRuleKind(ej);

  if (kind === "marker_trend") {
    return (
      <MarkerTrendView so={sourceObservation} linked={linked} observations={observations} timeline={timeline} />
    );
  }
  if (kind === "imaging_language") {
    return <ImagingComparisonView so={sourceObservation} linked={linked} />;
  }
  if (kind === "symptom_language") {
    return <SymptomTimelineView so={sourceObservation} timeline={timeline} />;
  }
  if (kind === "missing_data") {
    return <MissingDataReviewView so={sourceObservation} observations={observations} />;
  }

  return (
    <div className="p-4 rounded-lg border border-[#E2E8F0] bg-[#F8FAFC]">
      <p className="text-sm text-[#64748B]">No visualization available for this observation yet.</p>
    </div>
  );
}

