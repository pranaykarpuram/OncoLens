interface HeaderProps {
  title: string;
  subtitle?: string;
}

export function Header({ title, subtitle }: HeaderProps) {
  return (
    <div className="bg-white border-b border-[#E2E8F0] px-8 py-4 sticky top-0 z-10">
      <div>
        <h1 className="text-lg font-semibold text-[#0F172A]">{title}</h1>
        {subtitle && <p className="text-sm text-[#64748B] mt-0.5">{subtitle}</p>}
      </div>
    </div>
  );
}
