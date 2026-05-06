interface StatusBadgeProps {
  status: 'stable' | 'watch' | 'needs-review' | 'parsed' | 'pending-review' | 'verified' | 'draft';
  size?: 'sm' | 'md';
}

export function StatusBadge({ status, size = 'md' }: StatusBadgeProps) {
  const configs = {
    'stable': { bg: 'bg-green-100', text: 'text-green-700', label: 'Stable' },
    'watch': { bg: 'bg-amber-100', text: 'text-amber-700', label: 'Watch' },
    'needs-review': { bg: 'bg-red-100', text: 'text-red-700', label: 'Needs Review' },
    'parsed': { bg: 'bg-blue-100', text: 'text-blue-700', label: 'Parsed' },
    'pending-review': { bg: 'bg-purple-100', text: 'text-purple-700', label: 'Pending Review' },
    'verified': { bg: 'bg-green-100', text: 'text-green-700', label: 'Verified' },
    'draft': { bg: 'bg-gray-100', text: 'text-gray-700', label: 'Draft' },
  };

  const config = configs[status];
  const padding = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-3 py-1 text-sm';

  return (
    <span className={`inline-flex items-center rounded-full ${config.bg} ${config.text} ${padding} font-medium`}>
      {config.label}
    </span>
  );
}
