import { ListChecks, Search, Upload, Presentation, Users, Settings } from 'lucide-react';
import { Link, useLocation } from 'react-router';

const primaryNavItems = [
  { icon: ListChecks, label: 'Review Queue', path: '/queue' },
  { icon: Search, label: 'Evidence Search', path: '/search' },
  { icon: Upload, label: 'Report Intake', path: '/intake' },
  { icon: Presentation, label: 'Tumor Board', path: '/tumor-board' },
];

const secondaryNavItems = [
  { icon: Users, label: 'Patients', path: '/patients' },
  { icon: Settings, label: 'Admin', path: '/admin' },
];

export function Sidebar() {
  const location = useLocation();

  return (
    <div className="w-52 bg-white border-r border-[#E2E8F0] h-screen flex flex-col sticky top-0">
      <div className="p-5 pb-4">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-[#2563EB] flex items-center justify-center">
            <div className="w-4 h-4 rounded-full border-2 border-white"></div>
          </div>
          <div>
            <h1 className="font-semibold text-[#0F172A] text-sm">OncoLens</h1>
            <p className="text-xs text-[#64748B]">Chart Review</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 px-3">
        <div className="mb-4">
          {primaryNavItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-2.5 px-3 py-2 mb-0.5 rounded-md transition-all text-sm ${
                  isActive
                    ? 'bg-[#F1F5F9] text-[#0F172A] font-medium'
                    : 'text-[#64748B] hover:bg-[#F8FAFC] hover:text-[#0F172A]'
                }`}
              >
                <item.icon className="w-4 h-4" strokeWidth={2} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </div>

        <div className="pt-3 border-t border-[#E2E8F0]">
          {secondaryNavItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-2.5 px-3 py-2 mb-0.5 rounded-md transition-all text-sm ${
                  isActive
                    ? 'bg-[#F1F5F9] text-[#0F172A] font-medium'
                    : 'text-[#64748B] hover:bg-[#F8FAFC] hover:text-[#0F172A]'
                }`}
              >
                <item.icon className="w-4 h-4" strokeWidth={2} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </div>
      </nav>

      <div className="p-3 border-t border-[#E2E8F0]">
        <div className="flex items-center gap-2 px-2 py-1.5">
          <div className="w-7 h-7 rounded-md bg-[#64748B] flex items-center justify-center text-white text-xs font-medium">
            AM
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-[#0F172A] truncate">Dr. Morgan</p>
            <p className="text-xs text-[#64748B]">Oncologist</p>
          </div>
        </div>
      </div>
    </div>
  );
}
