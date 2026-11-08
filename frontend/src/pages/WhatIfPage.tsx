import React from 'react';
import { PageHeader } from '../components/common/PageHeader';
import { MetricCard } from '../components/common/MetricCard';
import { StatusBadge } from '../components/common/StatusBadge';
import { FlaskConical, Sliders, ArrowRight } from 'lucide-react';

export const WhatIfPage: React.FC = () => {
  const [deltaMass, setDeltaMass] = React.useState<number>(0);
  const [deltaGrip, setDeltaGrip] = React.useState<number>(0);
  const [deltaPower, setDeltaPower] = React.useState<number>(0);

  // Instant point-mass sensitivity model
  // dTime/dMass ~ +0.035 s/kg, dTime/dGrip ~ -1.8 s per +0.10 mu, dTime/dPower ~ -0.45 s/kW
  const baseTime = 43.82;
  const deltaT = deltaMass * 0.035 - (deltaGrip / 0.1) * 1.8 - deltaPower * 0.45;
  const simulatedTime = (baseTime + deltaT).toFixed(2);

  return (
    <div className="space-y-6">
      <PageHeader
        title="What-If Scenario Evaluation"
        subtitle="Simulate chassis setup modifications, power increments, and surface variations without modifying baseline data."
        badge={<StatusBadge status="ACTIVE" label="What-If Sandbox" />}
      />

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard
          label="Projected Lap Time"
          value={simulatedTime}
          unit="s"
          subValue={`Baseline: ${baseTime.toFixed(2)}s`}
          variant={deltaT < 0 ? 'highlight' : deltaT > 0 ? 'danger' : 'normal'}
        />
        <MetricCard
          label="Lap Time Delta (Δt)"
          value={`${deltaT > 0 ? '+' : ''}${deltaT.toFixed(2)}`}
          unit="s"
          subValue={deltaT < 0 ? 'Pace gain predicted' : deltaT > 0 ? 'Pace loss predicted' : 'Baseline matching'}
          variant={deltaT < 0 ? 'highlight' : deltaT > 0 ? 'danger' : 'normal'}
        />
        <MetricCard label="Simulated Mass" value={183 + deltaMass} unit="kg" subValue={`Δm: ${deltaMass > 0 ? '+' : ''}${deltaMass} kg`} />
        <MetricCard label="Simulated Grip (μ)" value={(1.24 + deltaGrip).toFixed(2)} unit="" subValue={`Δμ: ${deltaGrip > 0 ? '+' : ''}${deltaGrip.toFixed(2)}`} />
      </div>

      {/* Sliders Configuration */}
      <div className="bg-[#1E293B]/60 p-6 rounded-xl border border-slate-800 space-y-6">
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider font-mono flex items-center gap-2">
          <Sliders className="w-4 h-4 text-emerald-400" />
          Interactive Setup Parameter Adjustments
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Mass Slider */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-slate-300">VEHICLE MASS VARIATION</span>
              <span className="text-emerald-400">{deltaMass > 0 ? `+${deltaMass}` : deltaMass} kg</span>
            </div>
            <input
              type="range"
              min="-15"
              max="20"
              step="1"
              value={deltaMass}
              onChange={(e) => setDeltaMass(parseInt(e.target.value))}
              className="w-full accent-emerald-500"
            />
            <div className="flex justify-between text-[10px] text-slate-500 font-mono">
              <span>-15 kg (Lightened)</span>
              <span>+20 kg (Ballast)</span>
            </div>
          </div>

          {/* Grip Slider */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-slate-300">TIRE COMPOUND / TRACK GRIP (μ)</span>
              <span className="text-emerald-400">{deltaGrip > 0 ? `+${deltaGrip.toFixed(2)}` : deltaGrip.toFixed(2)}</span>
            </div>
            <input
              type="range"
              min="-0.30"
              max="0.25"
              step="0.02"
              value={deltaGrip}
              onChange={(e) => setDeltaGrip(parseFloat(e.target.value))}
              className="w-full accent-emerald-500"
            />
            <div className="flex justify-between text-[10px] text-slate-500 font-mono">
              <span>-0.30 (Wet / Dust)</span>
              <span>+0.25 (Soft Slick)</span>
            </div>
          </div>

          {/* Engine Power Slider */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-slate-300">ENGINE POWER TUNE</span>
              <span className="text-emerald-400">{deltaPower > 0 ? `+${deltaPower.toFixed(1)}` : deltaPower.toFixed(1)} kW</span>
            </div>
            <input
              type="range"
              min="-1.5"
              max="2.0"
              step="0.2"
              value={deltaPower}
              onChange={(e) => setDeltaPower(parseFloat(e.target.value))}
              className="w-full accent-emerald-500"
            />
            <div className="flex justify-between text-[10px] text-slate-500 font-mono">
              <span>-1.5 kW (Restricted)</span>
              <span>+2.0 kW (High Comp)</span>
            </div>
          </div>
        </div>

        <div className="text-[11px] font-mono text-slate-500 pt-3 border-t border-slate-800">
          All what-if outcomes are strictly labeled as simulated virtual projections and require physical track validation before competitive deployment.
        </div>
      </div>
    </div>
  );
};
