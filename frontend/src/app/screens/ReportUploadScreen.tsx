import { Upload, FileText, Check } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router';

import { fetchPatients, submitReportIntake } from '../api/client';

export function ReportUploadScreen() {
  const [searchParams] = useSearchParams();
  const prePatient = searchParams.get('patient');

  const [patients, setPatients] = useState<Array<{ id: number; name: string; mrn: string }>>([]);
  const [patientId, setPatientId] = useState<string>(prePatient || '');
  const [reportType, setReportType] = useState('lab');
  const [reportDate, setReportDate] = useState('');
  const [title, setTitle] = useState('');
  const [rawText, setRawText] = useState('');

  const [loadingPatients, setLoadingPatients] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastResult, setLastResult] = useState<{
    report_id: number;
    parse_status: string;
    extraction_count: number;
    review_extraction_url_hint?: string;
  } | null>(null);

  useEffect(() => {
    if (prePatient) setPatientId(prePatient);
  }, [prePatient]);

  useEffect(() => {
    let cancelled = false;
    fetchPatients()
      .then((res) => {
        if (!cancelled)
          setPatients(res.patients.map((p) => ({ id: p.id, name: p.name, mrn: p.mrn })));
      })
      .catch(() => {})
      .finally(() => {
        if (!cancelled) setLoadingPatients(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!patientId && patients.length > 0) {
      setPatientId(String(patients[0].id));
    }
  }, [patients, patientId]);

  const handleUpload = async () => {
    setError(null);
    setLastResult(null);
    if (!patientId) {
      setError('Choose a patient');
      return;
    }
    if (!rawText.trim()) {
      setError('Paste report text to run extraction');
      return;
    }
    setProcessing(true);
    try {
      const res = await submitReportIntake({
        patient: Number(patientId),
        report_type: reportType,
        report_date: reportDate || undefined,
        title: title.trim() || undefined,
        raw_text: rawText.trim(),
      });
      setLastResult(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Intake failed');
    } finally {
      setProcessing(false);
    }
  };

  const uploaded = Boolean(lastResult);

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-2xl p-5 border border-[#E2E8F0] mb-6">
        <div className="flex items-center gap-8">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center text-sm font-semibold">
              1
            </div>
            <span className="text-sm font-medium text-[#0F172A]">Upload</span>
          </div>
          <div className="flex items-center gap-3">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold ${processing || uploaded ? 'bg-blue-600 text-white' : 'bg-[#E2E8F0] text-[#64748B]'}`}>
              2
            </div>
            <span className={`text-sm ${processing || uploaded ? 'text-[#0F172A] font-medium' : 'text-[#64748B]'}`}>Extract</span>
          </div>
          <div className="flex items-center gap-3">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold ${uploaded ? 'bg-blue-600 text-white' : 'bg-[#E2E8F0] text-[#64748B]'}`}>
              3
            </div>
            <span className={`text-sm ${uploaded ? 'text-[#0F172A] font-medium' : 'text-[#64748B]'}`}>Confirm</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl p-6 border border-[#E2E8F0]">
          <h3 className="font-semibold text-[#0F172A] mb-2 text-sm">Paste report text</h3>
          <p className="text-xs text-[#64748B] mb-4">
            The demo parses pasted text server-side (file upload UI is cosmetic here).
          </p>

          <div className="border-2 border-dashed border-[#E2E8F0] rounded-3xl p-12 text-center mb-6 opacity-60 pointer-events-none">
            <div className="w-16 h-16 rounded-full bg-blue-50 flex items-center justify-center mx-auto mb-4">
              <Upload className="w-8 h-8 text-blue-600" />
            </div>
            <p className="font-medium text-[#0F172A] mb-2">Drag &amp; drop (not wired)</p>
          </div>

          <div className="space-y-4">
            <div>
              <label htmlFor="report-type" className="block text-sm font-medium text-[#0F172A] mb-2">
                Report type
              </label>
              <select
                id="report-type"
                value={reportType}
                onChange={(e) => setReportType(e.target.value)}
                className="w-full px-4 py-2.5 rounded-lg border border-[#E2E8F0] bg-white text-sm focus:outline-none focus:ring-2 focus:ring-[#2563EB] focus:border-transparent"
              >
                <option value="lab">Lab report</option>
                <option value="pathology">Pathology report</option>
                <option value="imaging">Imaging report</option>
                <option value="oncology_note">Oncology note</option>
                <option value="other">Other</option>
              </select>
            </div>

            <div>
              <label htmlFor="patient-id" className="block text-sm font-medium text-[#0F172A] mb-2">
                Patient
              </label>
              <select
                id="patient-id"
                value={patientId}
                onChange={(e) => setPatientId(e.target.value)}
                disabled={loadingPatients || patients.length === 0}
                className="w-full px-4 py-2.5 rounded-lg border border-[#E2E8F0] bg-white text-sm focus:outline-none focus:ring-2 focus:ring-[#2563EB] focus:border-transparent"
              >
                {loadingPatients ? (
                  <option value="">Loading…</option>
                ) : (
                  patients.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name} — MRN {p.mrn}
                    </option>
                  ))
                )}
              </select>
            </div>

            <div>
              <label htmlFor="report-date" className="block text-sm font-medium text-[#0F172A] mb-2">
                Report date (optional)
              </label>
              <input
                id="report-date"
                type="date"
                value={reportDate}
                onChange={(e) => setReportDate(e.target.value)}
                className="w-full px-4 py-2.5 rounded-lg border border-[#E2E8F0] bg-white text-sm focus:outline-none focus:ring-2 focus:ring-[#2563EB] focus:border-transparent"
              />
            </div>

            <div>
              <label htmlFor="title" className="block text-sm font-medium text-[#0F172A] mb-2">
                Title override (optional)
              </label>
              <input
                id="title"
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Defaults from report type + patient name"
                className="w-full px-4 py-2.5 rounded-lg border border-[#E2E8F0] bg-white text-sm focus:outline-none focus:ring-2 focus:ring-[#2563EB] focus:border-transparent"
              />
            </div>

            <div>
              <label htmlFor="raw" className="block text-sm font-medium text-[#0F172A] mb-2">
                Paste report text
              </label>
              <textarea
                id="raw"
                value={rawText}
                onChange={(e) => setRawText(e.target.value)}
                className="w-full px-4 py-2.5 rounded-lg border border-[#E2E8F0] bg-white text-sm focus:outline-none focus:ring-2 focus:ring-[#2563EB] focus:border-transparent resize-none"
                rows={10}
                placeholder="Paste clinical report text here..."
              />
            </div>

            {error && (
              <p className="text-sm text-red-600 bg-red-50 border border-red-100 rounded-lg px-3 py-2">{error}</p>
            )}

            <button
              type="button"
              onClick={handleUpload}
              disabled={processing}
              className="w-full px-4 py-2.5 bg-[#2563EB] text-white rounded-xl text-sm font-medium hover:bg-[#1d4ed8] transition-colors disabled:opacity-50"
            >
              Start extraction
            </button>
          </div>
        </div>

        <div className="bg-white rounded-2xl p-6 border border-[#E2E8F0]">
          <h3 className="font-semibold text-[#0F172A] mb-2 text-sm">Extraction result</h3>

          {!uploaded && !processing && (
            <div className="flex flex-col items-center justify-center py-20">
              <div className="w-24 h-24 rounded-full bg-[#F6FAFF] flex items-center justify-center mb-4">
                <FileText className="w-12 h-12 text-[#94A3B8]" />
              </div>
              <p className="text-sm text-[#64748B] text-center px-6">
                Paste text and submit to parse and persist extractions for the selected patient.
              </p>
            </div>
          )}

          {processing && (
            <div className="space-y-4">
              <div className="flex items-center gap-3 p-4 rounded-xl bg-blue-50">
                <div className="w-6 h-6 border-[3px] border-blue-600 border-t-transparent rounded-full animate-spin" />
                <span className="text-sm font-medium text-blue-700">Calling intake API…</span>
              </div>
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm text-[#64748B]">
                  <Check className="w-4 h-4 text-green-600" />
                  <span>Queued for server parsing</span>
                </div>
              </div>
            </div>
          )}

          {uploaded && !processing && lastResult && (
            <div className="space-y-6">
              <div className="flex items-center gap-3 p-4 rounded-xl bg-green-50 border border-green-200">
                <Check className="w-6 h-6 text-green-600" />
                <span className="text-sm font-medium text-green-700">Parse completed</span>
              </div>

              <div>
                <h4 className="font-medium text-[#0F172A] mb-3">Server response</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between p-3 rounded-xl bg-[#F6FAFF]">
                    <span className="text-[#64748B]">Report id</span>
                    <span className="font-medium text-[#0F172A]">{lastResult.report_id}</span>
                  </div>
                  <div className="flex justify-between p-3 rounded-xl bg-[#F6FAFF]">
                    <span className="text-[#64748B]">Parse status</span>
                    <span className="font-medium text-[#0F172A]">{lastResult.parse_status}</span>
                  </div>
                  <div className="flex justify-between p-3 rounded-xl bg-[#F6FAFF]">
                    <span className="text-[#64748B]">Extractions created</span>
                    <span className="font-medium text-[#0F172A]">{lastResult.extraction_count}</span>
                  </div>
                </div>
              </div>

              {lastResult.review_extraction_url_hint && (
                <p className="text-xs text-[#64748B]">
                  Django hint: <span className="font-mono">{lastResult.review_extraction_url_hint}</span>
                </p>
              )}

              <div className="p-4 rounded-xl bg-blue-50 border border-blue-100">
                <p className="text-xs text-blue-700">
                  Confirmation of individual extractions is still done from the clinician review workflow / Django
                  views in this prototype.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
