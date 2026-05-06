import { AlertCircle, TrendingUp } from 'lucide-react';

export interface EvidenceCardProps {
  statusBadge: string;
  headline: string;
  keyFact?: string;
  whySurfaced: string;
  sourceChips: string[];
  severity?: 'info' | 'watch' | 'needs-review';
  emphasized?: boolean;
  onClick?: () => void;
  selected?: boolean;
}

export function EvidenceCard({
  statusBadge,
  headline,
  keyFact,
  whySurfaced,
  sourceChips,
  severity = 'info',
  emphasized = false,
  onClick,
  selected = false,
}: EvidenceCardProps) {
  const borderAccent =
    severity === 'needs-review'
      ? 'border-l-red-500'
      : severity === 'watch'
        ? 'border-l-amber-400'
        : 'border-l-slate-300';

  const badgeStyles =
    severity === 'needs-review'
      ? 'bg-red-50 text-red-800 border-red-100'
      : severity === 'watch'
        ? 'bg-amber-50 text-amber-900 border-amber-100'
        : 'bg-slate-50 text-slate-700 border-slate-200';

  const Icon = severity === 'needs-review' || severity === 'watch' ? AlertCircle : TrendingUp;
  const iconColor =
    severity === 'needs-review' ? 'text-red-600' : severity === 'watch' ? 'text-amber-600' : 'text-slate-500';

  const pad = emphasized ? 'p-5' : 'p-4';
  const ring = emphasized && severity === 'needs-review' ? 'ring-1 ring-red-100 shadow-sm' : '';

  return (
    <div
      onClick={onClick}
      className={`${pad} rounded-xl border border-l-[5px] cursor-pointer transition-all ${borderAccent} ${ring} ${
        selected ? 'border-[#2563EB] bg-[#F8FAFC] ring-0 shadow-none' : 'border-[#E2E8F0] hover:border-[#94A3B8]'
      }`}
    >
      <div className="flex items-start justify-between gap-2 mb-2.5">
        <span
          className={`inline-flex items-center text-[10px] font-semibold uppercase tracking-wide px-2 py-0.5 rounded-md border ${badgeStyles}`}
        >
          {statusBadge}
        </span>
        <Icon className={`w-4 h-4 ${iconColor} flex-shrink-0`} />
      </div>

      <h4 className={`font-semibold text-[#0F172A] mb-2 leading-snug ${emphasized ? 'text-[15px]' : 'text-sm'}`}>
        {headline}
      </h4>

      {keyFact ? (
        <p className="text-sm font-semibold text-[#0F172A] mb-2 tracking-tight tabular-nums">{keyFact}</p>
      ) : null}

      <p className="text-sm text-[#64748B] mb-3 leading-relaxed">{whySurfaced}</p>

      {sourceChips.length > 0 ? (
        <div className="flex flex-wrap gap-1.5 mb-3">
          {sourceChips.map((chip, i) => (
            <span key={i} className="px-2 py-0.5 bg-[#F1F5F9] text-[#475569] text-[11px] rounded-md border border-[#E2E8F0]">
              {chip}
            </span>
          ))}
        </div>
      ) : null}

      <button
        type="button"
        onClick={(e) => {
          e.stopPropagation();
          onClick?.();
        }}
        className="text-xs text-[#2563EB] hover:underline font-semibold"
      >
        View Source Trail →
      </button>
    </div>
  );
}
