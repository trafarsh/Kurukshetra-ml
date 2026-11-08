import React from 'react';
import { PageHeader } from '../components/common/PageHeader';
import { MetricCard } from '../components/common/MetricCard';
import { StatusBadge } from '../components/common/StatusBadge';
import { UserCheck, Activity, Award } from 'lucide-react';

export const DriverAnalysisPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Driver Style & Consistency"
        subtitle="Quantitative driving inputs: steering smoothness, throttle application profiles, and braking consistency."
        badge={<StatusBadge status="ACTIVE" label="Driver: Arshad Mohamed (#7)" />}
      />

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard label="Driving Consistency Index" value="92.4" unit="/ 100" subValue="Variance: ±0.34s" variant="highlight" />
        <MetricCard label="Throttle Aggression" value="Medium" subValue="Progressive pickup" />
        <MetricCard label="Steering Smoothness" value="88.0" unit="/ 100" subValue="Max yaw jerk: 1.4 rad/s³" />
        <MetricCard label="Braking Stability" value="High" subValue="Decel peak: -1.25g" variant="highlight" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-[#1E293B]/60 p-5 rounded-xl border border-slate-800 space-y-3">
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider font-mono">
            Driver Input Characteristics
          </h3>
          <div className="space-y-3 text-xs font-mono text-slate-300">
            <div className="p-3 bg-slate-900/60 rounded-lg border border-slate-800">
              <div className="font-semibold text-emerald-400">CORNER APEX BEHAVIOUR</div>
              <p className="text-slate-400 mt-1 font-sans text-xs">
                Smooth trail-steering with progressive throttle pickup. No sudden wheel jerk observed in Turn 1 or Turn 4.
              </p>
            </div>
            <div className="p-3 bg-slate-900/60 rounded-lg border border-slate-800">
              <div className="font-semibold text-amber-400">TURN 7 THROTTLE HESITATION</div>
              <p className="text-slate-400 mt-1 font-sans text-xs">
                Telemetry indicates early throttle lift 15m before braking marker. 0.22s can be gained by deeper trail entry.
              </p>
            </div>
          </div>
        </div>

        <div className="bg-[#1E293B]/60 p-5 rounded-xl border border-slate-800 space-y-3">
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider font-mono">
            Stint Stint-by-Stint Progression
          </h3>
          <div className="space-y-2 text-xs font-mono">
            <div className="flex justify-between p-2.5 bg-slate-900/60 rounded border border-slate-800">
              <span>Stint 1 (Baseline Setup)</span>
              <span className="text-emerald-400">Avg 44.42s · Best 43.82s</span>
            </div>
            <div className="flex justify-between p-2.5 bg-slate-900/40 rounded border border-slate-800/80 text-slate-400">
              <span>Practice Stint 0 (Out-Lap)</span>
              <span>Avg 47.10s · Tire Scrubbing</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
