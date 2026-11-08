import React from 'react';
import { PageHeader } from '../components/common/PageHeader';
import { MetricCard } from '../components/common/MetricCard';
import { StatusBadge } from '../components/common/StatusBadge';
import { Box, Play, RefreshCw, CheckCircle2 } from 'lucide-react';

export const DigitalTwinPage: React.FC = () => {
  const [isSimulating, setIsSimulating] = React.useState(false);
  const [simLapTime, setSimLapTime] = React.useState('44.12');

  const runSimulation = () => {
    setIsSimulating(true);
    setTimeout(() => {
      setIsSimulating(false);
      setSimLapTime('43.94');
    }, 800);
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Physics Digital Twin & Calibration"
        subtitle="Forward point-mass vehicle dynamics solver, empirical grip calibration loop, and speed envelope generation."
        badge={<StatusBadge status="ACTIVE" label="Model Calibrated (RMSE 3.8%)" />}
        actions={
          <button
            onClick={runSimulation}
            disabled={isSimulating}
            className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-slate-900 font-mono text-xs font-bold rounded-lg flex items-center gap-2 transition disabled:opacity-50"
          >
            {isSimulating ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
            {isSimulating ? 'SOLVING EQUATIONS...' : 'RUN FORWARD SIMULATION'}
          </button>
        }
      />

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard label="Simulated Lap Time" value={simLapTime} unit="s" subValue="Point-mass solver" variant="highlight" />
        <MetricCard label="Measured Reference Lap" value="43.82" unit="s" subValue="Session 1 · Lap 3" />
        <MetricCard label="Calibration Error (RMSE)" value="3.8" unit="%" subValue="Target: < 5.0% (PASSED)" variant="highlight" />
        <MetricCard label="Calibrated Grip (μ)" value="1.24" unit="" subValue="Initial: 1.15 μ" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Kart Model Parameters */}
        <div className="bg-[#1E293B]/60 p-5 rounded-xl border border-slate-800 space-y-4">
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider font-mono">
            Governing Physics Parameters
          </h3>
          <div className="space-y-2.5 text-xs font-mono">
            <div className="flex justify-between p-2.5 bg-slate-900/60 rounded border border-slate-800">
              <span className="text-slate-400">Total Mass (m):</span>
              <span className="text-slate-200">183 kg (Kart 115kg + Driver 68kg)</span>
            </div>
            <div className="flex justify-between p-2.5 bg-slate-900/60 rounded border border-slate-800">
              <span className="text-slate-400">Effective Grip (μ):</span>
              <span className="text-emerald-400">1.24 (Calibrated)</span>
            </div>
            <div className="flex justify-between p-2.5 bg-slate-900/60 rounded border border-slate-800">
              <span className="text-slate-400">Drag Product (Cd·A):</span>
              <span className="text-slate-200">0.273 m² (Cd 0.65 × A 0.42)</span>
            </div>
            <div className="flex justify-between p-2.5 bg-slate-900/60 rounded border border-slate-800">
              <span className="text-slate-400">Rolling Resistance (Crr):</span>
              <span className="text-slate-200">0.018</span>
            </div>
            <div className="flex justify-between p-2.5 bg-slate-900/60 rounded border border-slate-800">
              <span className="text-slate-400">Peak Engine Power:</span>
              <span className="text-slate-200">7.5 kW (~10.1 HP)</span>
            </div>
          </div>
        </div>

        {/* Calibration Status & Convergence */}
        <div className="bg-[#1E293B]/60 p-5 rounded-xl border border-slate-800 lg:col-span-2 flex flex-col justify-between">
          <div>
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider font-mono mb-3">
              Iterative Calibration Loop Convergence
            </h3>
            <div className="p-4 bg-slate-900/80 rounded-lg border border-slate-800 space-y-3 font-mono text-xs">
              <div className="flex items-center gap-2 text-emerald-400">
                <CheckCircle2 className="w-4 h-4" />
                <span className="font-semibold">CONVERGED IN 4 ITERATIONS</span>
              </div>
              <p className="text-slate-400 font-sans text-xs leading-relaxed">
                The calibration algorithm compared corner apex speeds across Turns 1, 4, 7, and 9 against measured wheel telemetry. The effective tire grip parameter was tuned from μ = 1.15 to μ = 1.24, dropping apex RMSE from 6.8 km/h down to 1.6 km/h (3.8% relative error).
              </p>
            </div>
          </div>

          <div className="text-[11px] font-mono text-slate-500 border-t border-slate-800 pt-3 mt-4">
            Point-mass vehicle dynamics solver verified with low-speed asymptotic stabilization.
          </div>
        </div>
      </div>
    </div>
  );
};
