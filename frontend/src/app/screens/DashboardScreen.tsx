import { Users, AlertCircle, FileText, FlaskConical, ArrowRight, TrendingUp } from 'lucide-react';
import { MetricCard } from '../components/MetricCard';
import { StatusBadge } from '../components/StatusBadge';
import { useNavigate } from 'react-router';

const priorityPatients = [
  { name: 'Sarah Johnson', mrn: '1058846', diagnosis: 'Pancreatic adenocarcinoma', treatment: 'FOLFIRINOX', signal: 'CA 19-9 trending up', status: 'needs-review' as const, updated: '2 hours ago' },
  { name: 'Michael Chen', mrn: '1058901', diagnosis: 'Pancreatic NET', treatment: 'Everolimus', signal: 'Imaging shows progression', status: 'needs-review' as const, updated: '5 hours ago' },
  { name: 'Emma Wilson', mrn: '1059023', diagnosis: 'PDAC Stage II', treatment: 'Observation', signal: 'Post-op surveillance', status: 'watch' as const, updated: '1 day ago' },
  { name: 'James Rodriguez', mrn: '1059156', diagnosis: 'Pancreatic cancer', treatment: 'Gemcitabine', signal: 'Stable markers', status: 'stable' as const, updated: '2 days ago' },
  { name: 'Lisa Anderson', mrn: '1059234', diagnosis: 'PDAC Stage III', treatment: 'FOLFIRINOX', signal: 'Weight loss noted', status: 'watch' as const, updated: '3 days ago' },
];

const recentReports = [
  { type: 'Pathology Report', patient: 'Sarah Johnson', status: 'parsed' as const, time: '1 hour ago' },
  { type: 'Imaging Report', patient: 'Michael Chen', status: 'needs-review' as const, time: '3 hours ago' },
  { type: 'Lab Panel', patient: 'Emma Wilson', status: 'parsed' as const, time: '5 hours ago' },
  { type: 'Oncology Note', patient: 'James Rodriguez', status: 'parsed' as const, time: '1 day ago' },
];

export function DashboardScreen() {
  const navigate = useNavigate();

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-br from-blue-600 to-cyan-400 rounded-3xl p-8 text-white relative overflow-hidden">
        <div className="absolute right-0 top-0 w-64 h-64 opacity-20">
          <div className="w-full h-full rounded-full border-8 border-white blur-sm"></div>
        </div>
        <div className="relative z-10">
          <h2 className="text-3xl font-semibold mb-2">Good morning, Dr. Morgan</h2>
          <p className="text-blue-50 mb-6">12 patients updated this week. 4 require review.</p>
          <button
            onClick={() => navigate('/patients')}
            className="px-6 py-3 bg-white text-blue-600 rounded-xl font-semibold hover:bg-blue-50 transition-colors inline-flex items-center gap-2"
          >
            Review flagged patients
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-6">
        <MetricCard icon={Users} label="Total Patients" value="28" trend="Active panel" />
        <MetricCard icon={AlertCircle} label="Needs Review" value="4" trend="Flagged this week" iconColor="text-red-600" />
        <MetricCard icon={FileText} label="Reports Parsed" value="126" trend="+18 this month" iconColor="text-green-600" />
        <MetricCard icon={FlaskConical} label="Missing Recent Labs" value="3" trend="Requires follow-up" iconColor="text-amber-600" />
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2 bg-white rounded-3xl p-6 border border-[#E2E8F0] shadow-sm">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="font-semibold text-[#0F172A]">Priority Patients</h3>
              <p className="text-sm text-[#64748B]">Requiring clinical review</p>
            </div>
          </div>

          <div className="space-y-3">
            {priorityPatients.map((patient) => (
              <div key={patient.mrn} className="flex items-center gap-4 p-4 rounded-2xl border border-[#E2E8F0] hover:border-[#2563EB] hover:bg-[#F6FAFF] transition-all cursor-pointer" onClick={() => navigate('/patient/1')}>
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center text-white font-semibold flex-shrink-0">
                  {patient.name.split(' ').map(n => n[0]).join('')}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-[#0F172A]">{patient.name}</p>
                  <p className="text-sm text-[#64748B]">MRN: {patient.mrn}</p>
                </div>
                <div className="flex-1">
                  <p className="text-sm text-[#0F172A]">{patient.diagnosis}</p>
                  <p className="text-xs text-[#64748B]">{patient.treatment}</p>
                </div>
                <div className="flex-1">
                  <p className="text-sm text-[#0F172A]">{patient.signal}</p>
                  <p className="text-xs text-[#94A3B8]">{patient.updated}</p>
                </div>
                <StatusBadge status={patient.status} size="sm" />
                <button className="px-4 py-2 text-sm font-medium text-[#2563EB] hover:bg-[#EAF4FF] rounded-xl transition-colors">
                  Open
                </button>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-3xl p-6 border border-[#E2E8F0] shadow-sm">
          <h3 className="font-semibold text-[#0F172A] mb-2">Recent Report Activity</h3>
          <p className="text-sm text-[#64748B] mb-6">Latest document processing</p>

          <div className="space-y-4">
            {recentReports.map((report, i) => (
              <div key={i} className="pb-4 border-b border-[#E2E8F0] last:border-0 last:pb-0">
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center flex-shrink-0">
                    <FileText className="w-5 h-5 text-blue-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-sm text-[#0F172A]">{report.type}</p>
                    <p className="text-xs text-[#64748B] mb-2">{report.patient}</p>
                    <StatusBadge status={report.status} size="sm" />
                  </div>
                </div>
                <p className="text-xs text-[#94A3B8] mt-2">{report.time}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-blue-50 rounded-3xl p-6 border border-blue-100">
        <h3 className="font-semibold text-[#0F172A] mb-3">System Notes</h3>
        <ul className="space-y-2 text-sm text-[#64748B]">
          <li className="flex items-start gap-2">
            <div className="w-1.5 h-1.5 rounded-full bg-blue-600 mt-1.5"></div>
            <span>Insight flags are observation-based and require clinician review.</span>
          </li>
          <li className="flex items-start gap-2">
            <div className="w-1.5 h-1.5 rounded-full bg-blue-600 mt-1.5"></div>
            <span>No treatment recommendations are generated.</span>
          </li>
        </ul>
      </div>
    </div>
  );
}
