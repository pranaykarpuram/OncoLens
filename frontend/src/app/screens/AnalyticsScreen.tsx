import { Users, AlertCircle, FileText, FlaskConical } from 'lucide-react';
import { MetricCard } from '../components/MetricCard';
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const statusData = [
  { name: 'Stable', value: 18, color: '#16A34A' },
  { name: 'Watch', value: 6, color: '#F59E0B' },
  { name: 'Needs Review', value: 4, color: '#DC2626' },
];

const reportTypeData = [
  { id: 'lab', type: 'Lab', count: 52 },
  { id: 'pathology', type: 'Pathology', count: 28 },
  { id: 'imaging', type: 'Imaging', count: 31 },
  { id: 'notes', type: 'Notes', count: 15 },
];

const biomarkerData = [
  { id: 'kras', marker: 'KRAS', count: 18 },
  { id: 'tp53', marker: 'TP53', count: 14 },
  { id: 'smad4', marker: 'SMAD4', count: 8 },
  { id: 'cdkn2a', marker: 'CDKN2A', count: 6 },
  { id: 'brca2', marker: 'BRCA2', count: 4 },
];

const missingData = [
  { patient: 'Sarah Johnson', missing: 'Follow-up imaging', lastAvailable: '04/20/2026', action: 'Schedule CT' },
  { patient: 'Michael Chen', missing: 'Lab panel', lastAvailable: '03/15/2026', action: 'Order labs' },
  { patient: 'Emma Wilson', missing: 'Tumor markers', lastAvailable: '04/01/2026', action: 'CA 19-9 pending' },
];

export function AnalyticsScreen() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-4 gap-6">
        <MetricCard icon={Users} label="Total Patients" value="28" trend="Active panel" />
        <MetricCard icon={AlertCircle} label="Active Insight Flags" value="14" trend="Across all patients" iconColor="text-amber-600" />
        <MetricCard icon={FileText} label="Reports Parsed" value="126" trend="98% success rate" iconColor="text-green-600" />
        <MetricCard icon={FlaskConical} label="Missing Recent Labs" value="3" trend="Requires follow-up" iconColor="text-red-600" />
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="bg-white rounded-3xl p-6 border border-[#E2E8F0]">
          <h3 className="font-semibold text-[#0F172A] mb-2">Patient Status Distribution</h3>
          <p className="text-sm text-[#64748B] mb-6">Current panel overview</p>

          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={statusData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value, percent }) => `${name}: ${value} (${(percent * 100).toFixed(0)}%)`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {statusData.map((entry) => (
                  <Cell key={`cell-${entry.name}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>

          <div className="grid grid-cols-3 gap-3 mt-6">
            {statusData.map((item) => (
              <div key={item.name} className="p-4 rounded-2xl" style={{ backgroundColor: item.color + '15' }}>
                <p className="text-xs text-[#64748B] mb-1">{item.name}</p>
                <p className="text-2xl font-semibold" style={{ color: item.color }}>{item.value}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-3xl p-6 border border-[#E2E8F0]">
          <h3 className="font-semibold text-[#0F172A] mb-2">Reports by Type</h3>
          <p className="text-sm text-[#64748B] mb-6">Document distribution</p>

          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={reportTypeData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
              <XAxis dataKey="type" stroke="#94A3B8" style={{ fontSize: '12px' }} />
              <YAxis stroke="#94A3B8" style={{ fontSize: '12px' }} />
              <Tooltip contentStyle={{ borderRadius: '12px', border: '1px solid #E2E8F0' }} />
              <Bar dataKey="count" fill="#2563EB" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>

          <p className="text-xs text-[#94A3B8] mt-4">Total: {reportTypeData.reduce((sum, item) => sum + item.count, 0)} reports processed</p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="bg-white rounded-3xl p-6 border border-[#E2E8F0]">
          <h3 className="font-semibold text-[#0F172A] mb-2">Most Common Biomarkers</h3>
          <p className="text-sm text-[#64748B] mb-6">Detected across patient panel</p>

          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={biomarkerData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
              <XAxis type="number" stroke="#94A3B8" style={{ fontSize: '12px' }} />
              <YAxis dataKey="marker" type="category" stroke="#94A3B8" style={{ fontSize: '12px' }} />
              <Tooltip contentStyle={{ borderRadius: '12px', border: '1px solid #E2E8F0' }} />
              <Bar dataKey="count" fill="#7C3AED" radius={[0, 8, 8, 0]} />
            </BarChart>
          </ResponsiveContainer>

          <p className="text-xs text-[#94A3B8] mt-4">Total unique biomarkers detected: {biomarkerData.length}</p>
        </div>

        <div className="bg-white rounded-3xl p-6 border border-[#E2E8F0]">
          <h3 className="font-semibold text-[#0F172A] mb-2">Missing Data Worklist</h3>
          <p className="text-sm text-[#64748B] mb-6">Follow-up items required</p>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-[#E2E8F0]">
                  <th className="text-left py-3 px-2 text-xs uppercase text-[#94A3B8] font-medium">Patient</th>
                  <th className="text-left py-3 px-2 text-xs uppercase text-[#94A3B8] font-medium">Missing</th>
                  <th className="text-left py-3 px-2 text-xs uppercase text-[#94A3B8] font-medium">Last</th>
                  <th className="text-left py-3 px-2 text-xs uppercase text-[#94A3B8] font-medium">Action</th>
                </tr>
              </thead>
              <tbody>
                {missingData.map((row, i) => (
                  <tr key={i} className="border-b border-[#E2E8F0] last:border-0">
                    <td className="py-3 px-2 text-sm font-medium text-[#0F172A]">{row.patient}</td>
                    <td className="py-3 px-2 text-sm text-[#64748B]">{row.missing}</td>
                    <td className="py-3 px-2 text-sm text-[#94A3B8]">{row.lastAvailable}</td>
                    <td className="py-3 px-2">
                      <button className="text-xs font-medium text-blue-600 hover:underline">{row.action}</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="flex gap-3 mt-6">
            <button className="flex-1 px-4 py-2 bg-[#F6FAFF] border border-[#E2E8F0] text-[#0F172A] rounded-xl text-sm font-medium hover:bg-[#EAF4FF] transition-colors">
              Export CSV
            </button>
            <button className="flex-1 px-4 py-2 bg-[#F6FAFF] border border-[#E2E8F0] text-[#0F172A] rounded-xl text-sm font-medium hover:bg-[#EAF4FF] transition-colors">
              Export JSON
            </button>
          </div>
        </div>
      </div>

      <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-3xl p-6 border border-blue-100">
        <h3 className="font-semibold text-[#0F172A] mb-3">System Performance</h3>
        <div className="grid grid-cols-4 gap-4">
          <div className="p-4 rounded-2xl bg-white/80">
            <p className="text-xs uppercase text-[#94A3B8] mb-1">Parse Success Rate</p>
            <p className="text-2xl font-semibold text-green-600">98%</p>
          </div>
          <div className="p-4 rounded-2xl bg-white/80">
            <p className="text-xs uppercase text-[#94A3B8] mb-1">Avg Extraction Time</p>
            <p className="text-2xl font-semibold text-blue-600">2.3s</p>
          </div>
          <div className="p-4 rounded-2xl bg-white/80">
            <p className="text-xs uppercase text-[#94A3B8] mb-1">Avg Confidence</p>
            <p className="text-2xl font-semibold text-purple-600">94%</p>
          </div>
          <div className="p-4 rounded-2xl bg-white/80">
            <p className="text-xs uppercase text-[#94A3B8] mb-1">Manual Review Rate</p>
            <p className="text-2xl font-semibold text-amber-600">12%</p>
          </div>
        </div>
      </div>
    </div>
  );
}
