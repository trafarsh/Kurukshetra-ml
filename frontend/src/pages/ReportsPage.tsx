import React from 'react';
import { PageHeader } from '../components/common/PageHeader';
import { MetricCard } from '../components/common/MetricCard';
import { StatusBadge } from '../components/common/StatusBadge';
import { FileText, Download, CheckCircle, FileSpreadsheet } from 'lucide-react';

export const ReportsPage: React.FC = () => {
  const [reports, setReports] = React.useState([
    {
      id: 'rep_20261108_01',
      title: 'Practice Stint 1 — Comprehensive Debrief Dossier',
      date: '2026-11-08',
      type: 'POST_STINT_DEBRIEF',
      session: 'sess_20261108_01',
      pdfSize: '1.4 MB',
      csvSize: '8.2 MB',
    },
    {
      id: 'rep_20261108_02',
      title: 'Digital Twin Empirical Calibration Audit',
      date: '2026-11-08',
      type: 'CALIBRATION_AUDIT',
      session: 'sess_20261108_01',
      pdfSize: '890 KB',
      csvSize: '2.1 MB',
    },
  ]);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Engineering Reports & Telemetry Export"
        subtitle="Automated post-session PDF dossiers, competition debriefs, and raw telemetry CSV packages."
        badge={<StatusBadge status="ACTIVE" label="Report Engine Online" />}
        actions={
          <button className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-slate-900 font-mono text-xs font-bold rounded-lg flex items-center gap-2 transition">
            <FileText className="w-3.5 h-3.5" />
            <span>GENERATE NEW DEBRIEF DOSSIER</span>
          </button>
        }
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {reports.map((r) => (
          <div key={r.id} className="bg-[#1E293B]/60 p-5 rounded-xl border border-slate-800 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] font-mono text-emerald-400 uppercase font-semibold">{r.type}</span>
                <span className="text-xs text-slate-500 font-mono">{r.date}</span>
              </div>
              <h3 className="text-base font-bold text-slate-100 font-mono">{r.title}</h3>
              <p className="text-xs text-slate-400 mt-1 font-mono">Linked Session: {r.session}</p>
            </div>

            <div className="mt-5 pt-3 border-t border-slate-800 flex items-center justify-between">
              <span className="text-[11px] font-mono text-slate-500">Formats: PDF + CSV</span>
              <div className="flex items-center gap-2">
                <button className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-xs font-mono text-slate-200 rounded border border-slate-700 flex items-center gap-1.5 transition">
                  <Download className="w-3 h-3 text-red-400" />
                  <span>PDF ({r.pdfSize})</span>
                </button>
                <button className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-xs font-mono text-slate-200 rounded border border-slate-700 flex items-center gap-1.5 transition">
                  <FileSpreadsheet className="w-3 h-3 text-emerald-400" />
                  <span>CSV ({r.csvSize})</span>
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

