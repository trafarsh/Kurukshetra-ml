import React from 'react';
import { PageHeader } from '../components/common/PageHeader';
import { MetricCard } from '../components/common/MetricCard';
import { StatusBadge } from '../components/common/StatusBadge';
import { Timer, ArrowRight, TrendingUp } from 'lucide-react';

export const LapAnalysisPage: React.FC = () => {
  const [selectedLap, setSelectedLap] = React.useState<number>(3);

  const laps = [
    { num: 1, time: 45.42, s1: 14.8, s2: 17.2, s3: 13.42, maxV: 82.4, valid: true },
    { num: 2, time: 44.15, s1: 14.1, s2: 16.9, s3: 13.15, maxV: 84.8, valid: true },
    { num: 3, time: 43.82, s1: 13.9, s2: 16.8, s3: 13.12, maxV: 86.2, valid: true, best: true },
    { num: 4, time: 44.30, s1: 14.2, s2: 17.0, s3: 13.10, maxV: 85.0, valid: true },
    { num: 5, time: 48.90, s1: 15.4, s2: 19.2, s3: 14.30, maxV: 79.1, valid: false },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Lap Performance Analysis"
        subtitle="Lap split times, sector benchmarks, speed apex comparison, and theoretical optimal stint pace."
        badge={<StatusBadge status="ACTIVE" label="5 Laps Loaded" />}
      />

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <MetricCard label="Fastest Lap" value="43.82" unit="s" subValue="Lap 3 · Arshad" variant="highlight" />
        <MetricCard label="Theoretical Best (S1+S2+S3)" value="43.80" unit="s" subValue="Delta: -0.02s potential" variant="highlight" />
        <MetricCard label="Average Valid Lap" value="44.42" unit="s" subValue="Std dev: ±0.52s" />
        <MetricCard label="Top Speed in Stint" value="86.2" unit="km/h" subValue="Main Straight Exit" />
      </div>

      {/* Laps Table */}
      <div className="bg-[#1E293B]/60 rounded-xl border border-slate-800 overflow-hidden">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider font-mono">
            Stint Lap Table
          </h3>
          <span className="text-xs font-mono text-slate-500">Click a lap to inspect telemetry trace</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-900/60 text-slate-400 uppercase text-[11px] border-b border-slate-800">
              <tr>
                <th className="p-3">Lap</th>
                <th className="p-3">Lap Time</th>
                <th className="p-3">Sector 1</th>
                <th className="p-3">Sector 2</th>
                <th className="p-3">Sector 3</th>
                <th className="p-3">Peak Speed</th>
                <th className="p-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-200">
              {laps.map((l) => (
                <tr
                  key={l.num}
                  onClick={() => setSelectedLap(l.num)}
                  className={`cursor-pointer hover:bg-slate-800/40 transition-colors ${
                    selectedLap === l.num ? 'bg-slate-800/70 border-l-2 border-emerald-500' : ''
                  }`}
                >
                  <td className="p-3 font-bold text-slate-300">
                    Lap {l.num} {l.best && <span className="ml-1 text-[10px] text-emerald-400 font-semibold">[BEST]</span>}
                  </td>
                  <td className="p-3 font-semibold text-emerald-400">{l.time.toFixed(2)}s</td>
                  <td className="p-3">{l.s1.toFixed(2)}s</td>
                  <td className="p-3">{l.s2.toFixed(2)}s</td>
                  <td className="p-3">{l.s3.toFixed(2)}s</td>
                  <td className="p-3">{l.maxV.toFixed(1)} km/h</td>
                  <td className="p-3">
                    <StatusBadge status={l.valid ? 'SAFE' : 'CAUTION'} label={l.valid ? 'VALID' : 'TRAFFIC'} />
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
