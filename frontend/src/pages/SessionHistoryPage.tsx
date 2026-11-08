import React from 'react';
import { PageHeader } from '../components/common/PageHeader';
import { StatusBadge } from '../components/common/StatusBadge';
import { History, Upload, FileCode, CheckCircle } from 'lucide-react';

export const SessionHistoryPage: React.FC = () => {
  const [sessions, setSessions] = React.useState([
    {
      id: 'sess_20261108_01',
      name: 'Practice Stint 1 — Baseline Setup',
      date: '2026-11-08 14:30',
      track: 'SKCET Proving Ground',
      driver: 'Arshad (#7)',
      laps: 5,
      bestLap: '43.82s',
      status: 'COMPLETED' as const,
    },
    {
      id: 'sess_20261107_02',
      name: 'Tire Scrub & Brake Bedding Stint',
      date: '2026-11-07 16:15',
      track: 'SKCET Proving Ground',
      driver: 'Arshad (#7)',
      laps: 8,
      bestLap: '45.10s',
      status: 'COMPLETED' as const,
    },
  ]);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Session Archive & SD-Card Ingestion"
        subtitle="Historical track outings, raw MicroSD file parser, data cleaning status, and dataset quality reports."
        badge={<StatusBadge status="ACTIVE" label={`${sessions.length} Archived Outings`} />}
        actions={
          <label className="cursor-pointer px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-100 font-mono text-xs font-semibold rounded-lg border border-slate-700 flex items-center gap-2 transition">
            <Upload className="w-3.5 h-3.5 text-emerald-400" />
            <span>IMPORT SD-CARD CSV / BIN</span>
            <input type="file" className="hidden" />
          </label>
        }
      />

      <div className="bg-[#1E293B]/60 rounded-xl border border-slate-800 overflow-hidden">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider font-mono">
            Archived Telemetry Sessions
          </h3>
          <span className="text-xs font-mono text-slate-500">Dual-path storage (SD FAT32 + PostgreSQL/SQLite)</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-900/60 text-slate-400 uppercase text-[11px] border-b border-slate-800">
              <tr>
                <th className="p-3">Session Name & ID</th>
                <th className="p-3">Date</th>
                <th className="p-3">Track</th>
                <th className="p-3">Driver</th>
                <th className="p-3">Laps</th>
                <th className="p-3">Best Lap</th>
                <th className="p-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-200">
              {sessions.map((s) => (
                <tr key={s.id} className="hover:bg-slate-800/40 transition">
                  <td className="p-3">
                    <div className="font-bold text-slate-100">{s.name}</div>
                    <div className="text-[10px] text-slate-500 font-mono">{s.id}</div>
                  </td>
                  <td className="p-3 text-slate-400">{s.date}</td>
                  <td className="p-3">{s.track}</td>
                  <td className="p-3 text-slate-300">{s.driver}</td>
                  <td className="p-3 font-semibold text-emerald-400">{s.laps}</td>
                  <td className="p-3 font-mono font-bold text-emerald-400">{s.bestLap}</td>
                  <td className="p-3">
                    <StatusBadge status={s.status} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
