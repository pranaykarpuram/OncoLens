import { ArrowLeft, Upload, FileText, Plus, Download, AlertCircle, TrendingUp, Clock, Activity } from 'lucide-react';
import { StatusBadge } from '../components/StatusBadge';
import { useNavigate } from 'react-router';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useState } from 'react';

const ca199Data = [
  { id: 1, date: 'Feb 02', value: 120 },
  { id: 2, date: 'Mar 01', value: 310 },
  { id: 3, date: 'Mar 29', value: 780 },
  { id: 4, date: 'Apr 22', value: 910 },
];

const timeline = [
  { date: 'Jan 12, 2026', title: 'Diagnosis recorded', desc: 'Pancreatic adenocarcinoma Stage III', type: 'diagnosis' },
  { date: 'Jan 20, 2026', title: 'Pathology report uploaded', desc: 'KRAS G12D, TP53 mutations detected', type: 'report' },
  { date: 'Feb 02, 2026', title: 'FOLFIRINOX started', desc: 'First cycle administered', type: 'treatment' },
  { date: 'Mar 01, 2026', title: 'Lab report parsed', desc: 'CA 19-9: 310 U/mL', type: 'lab' },
  { date: 'Mar 29, 2026', title: 'CA 19-9 increased', desc: 'Value: 780 U/mL', type: 'lab' },
  { date: 'Apr 20, 2026', title: 'Imaging report uploaded', desc: 'CT scan shows progression', type: 'imaging' },
  { date: 'Apr 27, 2026', title: 'Clinical note added', desc: 'Patient reports fatigue, weight loss', type: 'note' },
];

const documents = [
  { name: 'Pathology Report', date: 'Jan 20, 2026', status: 'parsed' as const },
  { name: 'Lab Panel', date: 'Apr 22, 2026', status: 'parsed' as const },
  { name: 'CT Imaging Impression', date: 'Apr 20, 2026', status: 'needs-review' as const },
  { name: 'Oncology Visit Note', date: 'Apr 27, 2026', status: 'parsed' as const },
];

const extractedData = [
  { date: '02/02/2026', source: 'Lab Report', type: 'Tumor Marker', name: 'CA 19-9', value: '120', unit: 'U/mL', confidence: '94%', verified: true },
  { date: '03/01/2026', source: 'Lab Report', type: 'Tumor Marker', name: 'CA 19-9', value: '310', unit: 'U/mL', confidence: '96%', verified: true },
  { date: '03/29/2026', source: 'Lab Report', type: 'Tumor Marker', name: 'CA 19-9', value: '780', unit: 'U/mL', confidence: '95%', verified: true },
  { date: '04/22/2026', source: 'Lab Report', type: 'Tumor Marker', name: 'CA 19-9', value: '910', unit: 'U/mL', confidence: '97%', verified: true },
  { date: '04/27/2026', source: 'Visit Note', type: 'Vital', name: 'Weight', value: '66', unit: 'kg', confidence: '91%', verified: false },
  { date: '01/20/2026', source: 'Pathology', type: 'Biomarker', name: 'KRAS G12D', value: 'Detected', unit: '', confidence: '88%', verified: true },
];

const insightFlags = [
  { severity: 'needs-review', title: 'CA 19-9 increased across last 3 measurements', desc: 'Consecutive increase pattern detected' },
  { severity: 'watch', title: 'Weight decreased over last 2 visits', desc: '70kg → 66kg over 8 weeks' },
  { severity: 'watch', title: 'Latest note mentions fatigue', desc: 'Symptom flag from clinical documentation' },
  { severity: 'info', title: 'No treatment recommendation generated', desc: 'System provides observation-based insights only' },
];

export function PatientProfileScreen() {
  const navigate = useNavigate();
  const [showEvidence, setShowEvidence] = useState(false);

  return (
    <div className="space-y-6 pb-8">
      <div className="bg-white rounded-3xl p-6 border border-[#E2E8F0]">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button onClick={() => navigate('/patients')} className="p-2 hover:bg-[#F6FAFF] rounded-xl transition-colors">
              <ArrowLeft className="w-5 h-5 text-[#64748B]" />
            </button>
            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center text-white font-semibold text-xl">
              SJ
            </div>
            <div>
              <h2 className="text-2xl font-semibold text-[#0F172A]">Sarah Johnson</h2>
              <p className="text-sm text-[#64748B]">MRN: 1058846 • 62F • Stage III Pancreatic adenocarcinoma</p>
              <p className="text-sm text-[#64748B] mt-1">Current Treatment: FOLFIRINOX</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <StatusBadge status="needs-review" />
            <button className="px-4 py-2 rounded-xl border border-[#E2E8F0] hover:bg-[#F6FAFF] transition-colors flex items-center gap-2">
              <Upload className="w-4 h-4" />
              <span className="text-sm font-medium">Upload Report</span>
            </button>
            <button className="px-4 py-2 rounded-xl border border-[#E2E8F0] hover:bg-[#F6FAFF] transition-colors flex items-center gap-2">
              <Plus className="w-4 h-4" />
              <span className="text-sm font-medium">Add Note</span>
            </button>
            <button className="px-4 py-2 rounded-xl bg-[#2563EB] text-white hover:bg-[#1d4ed8] transition-colors flex items-center gap-2">
              <Download className="w-4 h-4" />
              <span className="text-sm font-medium">Export</span>
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2 bg-white rounded-3xl p-6 border border-[#E2E8F0]">
          <h3 className="font-semibold text-[#0F172A] mb-2">Clinical Snapshot</h3>
          <p className="text-sm text-[#64748B] mb-6">Updated from latest reports and notes</p>

          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="p-4 rounded-2xl bg-[#F6FAFF]">
              <p className="text-xs uppercase text-[#94A3B8] mb-1">Diagnosis</p>
              <p className="font-medium text-[#0F172A]">Pancreatic adenocarcinoma</p>
            </div>
            <div className="p-4 rounded-2xl bg-[#F6FAFF]">
              <p className="text-xs uppercase text-[#94A3B8] mb-1">Stage</p>
              <p className="font-medium text-[#0F172A]">III</p>
            </div>
            <div className="p-4 rounded-2xl bg-[#F6FAFF]">
              <p className="text-xs uppercase text-[#94A3B8] mb-1">Current Therapy</p>
              <p className="font-medium text-[#0F172A]">FOLFIRINOX</p>
            </div>
            <div className="p-4 rounded-2xl bg-[#F6FAFF]">
              <p className="text-xs uppercase text-[#94A3B8] mb-1">Biomarkers</p>
              <p className="font-medium text-[#0F172A]">KRAS G12D, TP53</p>
            </div>
            <div className="p-4 rounded-2xl bg-[#F6FAFF]">
              <p className="text-xs uppercase text-[#94A3B8] mb-1">Latest CA 19-9</p>
              <p className="font-medium text-[#0F172A]">910 U/mL</p>
            </div>
            <div className="p-4 rounded-2xl bg-[#F6FAFF]">
              <p className="text-xs uppercase text-[#94A3B8] mb-1">Last Imaging</p>
              <p className="font-medium text-[#0F172A]">04/20/2026</p>
            </div>
          </div>

          <div className="p-6 rounded-2xl bg-gradient-to-br from-purple-50 to-blue-50 border border-purple-100">
            <div className="flex items-start gap-3 mb-3">
              <div className="w-8 h-8 rounded-lg bg-[#7C3AED] flex items-center justify-center flex-shrink-0">
                <Activity className="w-5 h-5 text-white" />
              </div>
              <div className="flex-1">
                <h4 className="font-semibold text-[#0F172A] mb-2">Generated Clinical Summary</h4>
                <p className="text-sm text-[#0F172A] leading-relaxed">
                  Source documents show the patient is undergoing FOLFIRINOX treatment. CA 19-9 has increased across the last three recorded measurements, and the latest note mentions fatigue and weight loss. This summary is observation-based and requires clinician review.
                </p>
              </div>
            </div>
            <p className="text-xs text-[#7C3AED] font-medium">
              Not a diagnosis or treatment recommendation.
            </p>
          </div>
        </div>

        <div className="bg-white rounded-3xl p-6 border border-[#E2E8F0]">
          <h3 className="font-semibold text-[#0F172A] mb-6">Patient Status</h3>

          <div className="flex items-center justify-center mb-6">
            <div className="relative w-32 h-32">
              <svg className="w-full h-full transform -rotate-90">
                <circle cx="64" cy="64" r="56" fill="none" stroke="#E2E8F0" strokeWidth="8" />
                <circle cx="64" cy="64" r="56" fill="none" stroke="#DC2626" strokeWidth="8" strokeDasharray="352" strokeDashoffset="88" strokeLinecap="round" />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center flex-col">
                <p className="text-xs uppercase text-[#94A3B8]">Priority</p>
                <p className="text-2xl font-bold text-[#DC2626]">High</p>
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <div className="p-4 rounded-2xl bg-red-50 border border-red-100">
              <p className="text-sm font-semibold text-red-700 mb-1">3 active insight flags</p>
              <p className="text-xs text-red-600">Requires clinical review</p>
            </div>
            <div className="p-4 rounded-2xl bg-blue-50 border border-blue-100">
              <p className="text-sm font-semibold text-blue-700 mb-1">2 reports added this month</p>
              <p className="text-xs text-blue-600">Recent activity</p>
            </div>
            <div className="p-4 rounded-2xl bg-amber-50 border border-amber-100">
              <p className="text-sm font-semibold text-amber-700 mb-1">1 missing follow-up item</p>
              <p className="text-xs text-amber-600">Pending lab work</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2 bg-white rounded-3xl p-6 border border-[#E2E8F0]">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="font-semibold text-[#0F172A]">Longitudinal Trends</h3>
              <p className="text-sm text-[#64748B]">Tumor markers over time</p>
            </div>
            <div className="flex gap-2">
              <button className="px-4 py-2 rounded-xl bg-[#2563EB] text-white text-sm font-medium">Tumor Markers</button>
              <button className="px-4 py-2 rounded-xl bg-[#F6FAFF] text-[#64748B] text-sm font-medium hover:bg-[#EAF4FF]">Vitals</button>
              <button className="px-4 py-2 rounded-xl bg-[#F6FAFF] text-[#64748B] text-sm font-medium hover:bg-[#EAF4FF]">Labs</button>
            </div>
          </div>

          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={ca199Data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
              <XAxis dataKey="date" stroke="#94A3B8" style={{ fontSize: '12px' }} />
              <YAxis stroke="#94A3B8" style={{ fontSize: '12px' }} label={{ value: 'CA 19-9 (U/mL)', angle: -90, position: 'insideLeft', style: { fontSize: '12px', fill: '#64748B' } }} />
              <Tooltip contentStyle={{ borderRadius: '12px', border: '1px solid #E2E8F0' }} />
              <Line type="monotone" dataKey="value" stroke="#DC2626" strokeWidth={3} dot={{ fill: '#DC2626', r: 6 }} activeDot={{ r: 8 }} />
            </LineChart>
          </ResponsiveContainer>

          <div className="grid grid-cols-3 gap-4 mt-6">
            <div className="p-4 rounded-2xl bg-[#F6FAFF]">
              <p className="text-xs uppercase text-[#94A3B8] mb-1">Latest Value</p>
              <p className="text-2xl font-semibold text-[#0F172A]">910</p>
              <p className="text-xs text-[#64748B]">U/mL</p>
            </div>
            <div className="p-4 rounded-2xl bg-red-50">
              <p className="text-xs uppercase text-[#94A3B8] mb-1">8-Week Change</p>
              <p className="text-2xl font-semibold text-red-600">+192%</p>
              <p className="text-xs text-[#64748B]">Increasing</p>
            </div>
            <div className="p-4 rounded-2xl bg-[#F6FAFF]">
              <p className="text-xs uppercase text-[#94A3B8] mb-1">Pattern</p>
              <p className="text-sm font-semibold text-[#0F172A]">Consecutive increase</p>
              <p className="text-xs text-[#64748B]">4 data points</p>
            </div>
          </div>

          <p className="text-xs text-[#94A3B8] mt-4 italic">
            Trend flag generated from structured lab observations.
          </p>
        </div>

        <div className="bg-white rounded-3xl p-6 border border-[#E2E8F0]">
          <h3 className="font-semibold text-[#0F172A] mb-2">Insight Flags</h3>
          <p className="text-sm text-[#64748B] mb-6">Observation-based signals</p>

          <div className="space-y-3">
            {insightFlags.map((flag, i) => (
              <div key={i} className={`p-4 rounded-2xl border ${
                flag.severity === 'needs-review' ? 'bg-red-50 border-red-200' :
                flag.severity === 'watch' ? 'bg-amber-50 border-amber-200' :
                'bg-blue-50 border-blue-200'
              }`}>
                <div className="flex items-start gap-2 mb-2">
                  <AlertCircle className={`w-4 h-4 flex-shrink-0 mt-0.5 ${
                    flag.severity === 'needs-review' ? 'text-red-600' :
                    flag.severity === 'watch' ? 'text-amber-600' :
                    'text-blue-600'
                  }`} />
                  <div className="flex-1">
                    <p className={`text-sm font-semibold ${
                      flag.severity === 'needs-review' ? 'text-red-700' :
                      flag.severity === 'watch' ? 'text-amber-700' :
                      'text-blue-700'
                    }`}>{flag.title}</p>
                    <p className={`text-xs mt-1 ${
                      flag.severity === 'needs-review' ? 'text-red-600' :
                      flag.severity === 'watch' ? 'text-amber-600' :
                      'text-blue-600'
                    }`}>{flag.desc}</p>
                  </div>
                </div>
                {flag.severity !== 'info' && (
                  <button onClick={() => setShowEvidence(true)} className={`text-xs font-medium ${
                    flag.severity === 'needs-review' ? 'text-red-700' :
                    'text-amber-700'
                  } hover:underline`}>
                    View evidence →
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2 bg-white rounded-3xl p-6 border border-[#E2E8F0]">
          <h3 className="font-semibold text-[#0F172A] mb-6">Clinical Timeline</h3>

          <div className="relative">
            <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-[#E2E8F0]"></div>
            <div className="space-y-6">
              {timeline.map((event, i) => (
                <div key={i} className="relative pl-16">
                  <div className={`absolute left-0 w-12 h-12 rounded-full flex items-center justify-center ${
                    event.type === 'diagnosis' ? 'bg-purple-100' :
                    event.type === 'report' ? 'bg-blue-100' :
                    event.type === 'treatment' ? 'bg-green-100' :
                    event.type === 'lab' ? 'bg-amber-100' :
                    event.type === 'imaging' ? 'bg-cyan-100' :
                    'bg-gray-100'
                  }`}>
                    {event.type === 'lab' && <Activity className={`w-5 h-5 ${i >= timeline.length - 3 ? 'text-red-600' : 'text-amber-600'}`} />}
                    {event.type === 'report' && <FileText className="w-5 h-5 text-blue-600" />}
                    {event.type === 'treatment' && <Plus className="w-5 h-5 text-green-600" />}
                    {event.type === 'imaging' && <TrendingUp className="w-5 h-5 text-cyan-600" />}
                    {event.type === 'diagnosis' && <AlertCircle className="w-5 h-5 text-purple-600" />}
                    {event.type === 'note' && <Clock className="w-5 h-5 text-gray-600" />}
                  </div>
                  <div className="ml-2">
                    <p className="text-xs text-[#94A3B8] mb-1">{event.date}</p>
                    <p className="font-medium text-[#0F172A]">{event.title}</p>
                    <p className="text-sm text-[#64748B]">{event.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="bg-white rounded-3xl p-6 border border-[#E2E8F0]">
          <h3 className="font-semibold text-[#0F172A] mb-6">Source Documents</h3>

          <div className="space-y-3 mb-6">
            {documents.map((doc, i) => (
              <div key={i} className="p-4 rounded-2xl border border-[#E2E8F0] hover:border-[#2563EB] hover:bg-[#F6FAFF] transition-all">
                <div className="flex items-start gap-3 mb-2">
                  <div className="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center flex-shrink-0">
                    <FileText className="w-5 h-5 text-blue-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-[#0F172A]">{doc.name}</p>
                    <p className="text-xs text-[#64748B] mt-1">{doc.date}</p>
                    <div className="mt-2">
                      <StatusBadge status={doc.status} size="sm" />
                    </div>
                  </div>
                </div>
                <button className="w-full mt-3 px-3 py-2 text-sm font-medium text-[#2563EB] border border-[#2563EB] rounded-xl hover:bg-[#EAF4FF] transition-colors">
                  View
                </button>
              </div>
            ))}
          </div>

          <button className="w-full px-4 py-3 bg-[#2563EB] text-white rounded-xl font-medium hover:bg-[#1d4ed8] transition-colors flex items-center justify-center gap-2">
            <Upload className="w-4 h-4" />
            Upload Report
          </button>
        </div>
      </div>

      <div className="bg-white rounded-3xl p-6 border border-[#E2E8F0]">
        <h3 className="font-semibold text-[#0F172A] mb-6">Extracted Structured Data</h3>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-[#E2E8F0]">
                <th className="text-left py-3 px-4 text-xs uppercase text-[#94A3B8] font-medium">Date</th>
                <th className="text-left py-3 px-4 text-xs uppercase text-[#94A3B8] font-medium">Source</th>
                <th className="text-left py-3 px-4 text-xs uppercase text-[#94A3B8] font-medium">Data Type</th>
                <th className="text-left py-3 px-4 text-xs uppercase text-[#94A3B8] font-medium">Name</th>
                <th className="text-left py-3 px-4 text-xs uppercase text-[#94A3B8] font-medium">Value</th>
                <th className="text-left py-3 px-4 text-xs uppercase text-[#94A3B8] font-medium">Unit</th>
                <th className="text-left py-3 px-4 text-xs uppercase text-[#94A3B8] font-medium">Confidence</th>
                <th className="text-left py-3 px-4 text-xs uppercase text-[#94A3B8] font-medium">Verified</th>
              </tr>
            </thead>
            <tbody>
              {extractedData.map((row, i) => (
                <tr key={i} className="border-b border-[#E2E8F0] last:border-0 hover:bg-[#F6FAFF]">
                  <td className="py-3 px-4 text-sm text-[#0F172A]">{row.date}</td>
                  <td className="py-3 px-4 text-sm text-[#64748B]">{row.source}</td>
                  <td className="py-3 px-4 text-sm text-[#64748B]">{row.type}</td>
                  <td className="py-3 px-4 text-sm font-medium text-[#0F172A]">{row.name}</td>
                  <td className="py-3 px-4 text-sm font-semibold text-[#0F172A]">{row.value}</td>
                  <td className="py-3 px-4 text-sm text-[#64748B]">{row.unit}</td>
                  <td className="py-3 px-4">
                    <span className={`text-sm font-medium ${parseInt(row.confidence) >= 90 ? 'text-green-600' : 'text-amber-600'}`}>
                      {row.confidence}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    {row.verified ? (
                      <span className="text-green-600 text-sm">✓ Verified</span>
                    ) : (
                      <span className="text-amber-600 text-sm">Pending</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {showEvidence && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-end z-50" onClick={() => setShowEvidence(false)}>
          <div className="bg-white w-[480px] h-full shadow-2xl rounded-l-3xl p-8 overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-start justify-between mb-6">
              <div className="flex-1">
                <h3 className="text-xl font-semibold text-[#0F172A] mb-2">CA 19-9 increased across last 3 measurements</h3>
                <StatusBadge status="needs-review" size="sm" />
              </div>
              <button onClick={() => setShowEvidence(false)} className="text-[#64748B] hover:text-[#0F172A] ml-4">
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="space-y-6">
              <div className="p-5 rounded-2xl bg-blue-50 border border-blue-100">
                <h4 className="font-semibold text-[#0F172A] mb-2">Why this was flagged</h4>
                <p className="text-sm text-[#64748B]">
                  This flag was generated because CA 19-9 increased on three consecutive recorded observations.
                </p>
              </div>

              <div>
                <h4 className="font-semibold text-[#0F172A] mb-4">Evidence used</h4>
                <div className="space-y-2">
                  {ca199Data.map((point) => (
                    <div key={point.id} className="p-4 rounded-xl border border-[#E2E8F0] bg-white">
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-[#64748B]">{point.date} 2026</span>
                        <span className="text-lg font-semibold text-[#0F172A]">{point.value} U/mL</span>
                      </div>
                      <p className="text-xs text-[#94A3B8] mt-1">Lab Report</p>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="font-semibold text-[#0F172A] mb-3">Source snippets</h4>
                <div className="space-y-3">
                  <div className="p-4 rounded-xl bg-amber-50 border border-amber-100">
                    <p className="text-sm text-[#0F172A] italic">
                      "CA 19-9 measured at 780 U/mL, elevated from prior measurement..."
                    </p>
                    <p className="text-xs text-[#94A3B8] mt-2">From Lab Report • Mar 29, 2026</p>
                  </div>
                  <div className="p-4 rounded-xl bg-amber-50 border border-amber-100">
                    <p className="text-sm text-[#0F172A] italic">
                      "CA 19-9 measured at 910 U/mL, continued increase noted..."
                    </p>
                    <p className="text-xs text-[#94A3B8] mt-2">From Lab Report • Apr 22, 2026</p>
                  </div>
                </div>
              </div>

              <div className="p-5 rounded-2xl bg-[#F6FAFF] border border-[#E2E8F0]">
                <h4 className="font-semibold text-[#0F172A] mb-2">Rule logic</h4>
                <p className="text-sm text-[#64748B]">
                  Flag if same marker increases across 3 consecutive measurements.
                </p>
              </div>

              <div className="pt-6 border-t border-[#E2E8F0] space-y-3">
                <button className="w-full px-4 py-3 bg-[#2563EB] text-white rounded-xl font-medium hover:bg-[#1d4ed8] transition-colors">
                  Mark reviewed
                </button>
                <button className="w-full px-4 py-3 border border-[#E2E8F0] text-[#0F172A] rounded-xl font-medium hover:bg-[#F6FAFF] transition-colors">
                  Open source report
                </button>
              </div>

              <p className="text-xs text-center text-[#94A3B8] pt-4 border-t border-[#E2E8F0]">
                This insight is informational and does not determine diagnosis or treatment.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
