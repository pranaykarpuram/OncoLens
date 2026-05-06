interface SourceChipProps {
  type: string;
  date: string;
}

export function SourceChip({ type, date }: SourceChipProps) {
  return (
    <span className="inline-flex items-center px-2 py-0.5 bg-[#F1F5F9] text-[#64748B] text-xs rounded">
      {type} · {date}
    </span>
  );
}
