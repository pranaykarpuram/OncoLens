import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  icon: LucideIcon;
  label: string;
  value: string | number;
  trend?: string;
  iconColor?: string;
}

export function MetricCard({ icon: Icon, label, value, trend, iconColor = 'text-blue-600' }: MetricCardProps) {
  return (
    <div className="bg-white rounded-3xl p-6 border border-[#E2E8F0] shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs uppercase tracking-wide text-[#94A3B8] mb-2">{label}</p>
          <p className="text-3xl font-semibold text-[#0F172A] mb-1">{value}</p>
          {trend && <p className="text-sm text-[#64748B]">{trend}</p>}
        </div>
        <div className={`p-3 rounded-2xl bg-blue-50`}>
          <Icon className={`w-6 h-6 ${iconColor}`} />
        </div>
      </div>
    </div>
  );
}
