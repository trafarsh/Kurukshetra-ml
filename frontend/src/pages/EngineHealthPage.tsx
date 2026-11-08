import React from 'react';
import { PageHeader } from '../components/common/PageHeader';
import { MetricCard } from '../components/common/MetricCard';
import { StatusBadge } from '../components/common/StatusBadge';
import { Thermometer, Zap, Activity, AlertTriangle } from 'lucide-react';

export const EngineHealthPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Powertrain & Engine Health"
        subtitle="125cc IC Engine thermal telemetry, rev limiter protection, vibration monitoring, and anomaly detection."
        badge={<StatusBadge status="SAFE" label="Powertrain OK" />}
      />

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard label="Cylinder Head Temp" value="91.5" unit="°C" subValue="Safe ceiling: 110.0°C" icon={<Thermometer className="w-4 h-4" />} />
        <MetricCard label="Peak Stint RPM" value="9,140" unit="RPM" subValue="Soft limiter: 9,500" icon={<Zap className="w-4 h-4" />} />
        <MetricCard label="Avg Operating Temp" value="88.2" unit="°C" subValue="Thermal stability: 98%" />
        <MetricCard label="ML Anomaly Score" value="-0.12" unit="" subValue="Isolation Forest (Normal)" variant="highlight" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-[#1E293B]/60 p-5 rounded-xl border border-slate-800 space-y-4">
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider font-mono">
            Thermal Runaway Safeguards
          </h3>
          <div className="space-y-3 font-mono text-xs text-slate-300">
            <div className="p-3 bg-slate-900/60 rounded-lg border border-slate-800 flex justify-between items-center">
              <div>
                <div className="font-semibold text-slate-200">THERMAL GRADIENT (dT/dt)</div>
                <div className="text-[11px] text-slate-500">+0.15 °C/s during full throttle</div>
              </div>
              <StatusBadge status="SAFE" />
            </div>
            <div className="p-3 bg-slate-900/60 rounded-lg border border-slate-800 flex justify-between items-center">
              <div>
                <div className="font-semibold text-slate-200">MAX CONTINUOUS HIGH RPM</div>
                <div className="text-[11px] text-slate-500">4.2s consecutive &gt; 8500 RPM</div>
              </div>
              <StatusBadge status="SAFE" />
            </div>
          </div>
        </div>

        <div className="bg-[#1E293B]/60 p-5 rounded-xl border border-slate-800 space-y-4">
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider font-mono">
            Sensor Diagnostic Bitfield
          </h3>
          <div className="grid grid-cols-2 gap-3 text-xs font-mono">
            <div className="p-2.5 bg-slate-900/60 rounded border border-slate-800 flex justify-between">
              <span className="text-slate-400">Hall Wheel Speed:</span>
              <span className="text-emerald-400">ONLINE</span>
            </div>
            <div className="p-2.5 bg-slate-900/60 rounded border border-slate-800 flex justify-between">
              <span className="text-slate-400">Inductive RPM:</span>
              <span className="text-emerald-400">ONLINE</span>
            </div>
            <div className="p-2.5 bg-slate-900/60 rounded border border-slate-800 flex justify-between">
              <span className="text-slate-400">DS18B20 Temp Probe:</span>
              <span className="text-emerald-400">ONLINE</span>
            </div>
            <div className="p-2.5 bg-slate-900/60 rounded border border-slate-800 flex justify-between">
              <span className="text-slate-400">MPU6050 IMU:</span>
              <span className="text-emerald-400">ONLINE</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

