import React from 'react';
import { PageHeader } from '../components/common/PageHeader';
import { MetricCard } from '../components/common/MetricCard';
import { StatusBadge } from '../components/common/StatusBadge';
import { useTelemetryStore } from '../stores/telemetryStore';
import { Gauge, Zap, Thermometer, ShieldAlert, Navigation, Compass } from 'lucide-react';

export const OverviewPage: React.FC = () => {
  const { currentData, activeSessionId } = useTelemetryStore();

  const speed = currentData ? currentData.speed_kmh.toFixed(1) : '0.0';
  const rpm = currentData ? currentData.engine_rpm : 0;
  const temp = currentData ? currentData.engine_temp_c.toFixed(1) : '28.4';
  const throttle = currentData ? `${currentData.throttle_percent.toFixed(0)}%` : '0%';
  const steering = currentData ? `${currentData.steering_angle_deg.toFixed(1)}°` : '0.0°';
  const latG = currentData ? `${currentData.accel_y_g.toFixed(2)} g` : '0.00 g';
  const ttc = currentData && currentData.ttc_seconds ? `${currentData.ttc_seconds.toFixed(2)} s` : '∞';
  const warning = currentData ? currentData.warning_level : 'SAFE';

  return (
    <div className="space-y-6">
      <PageHeader
        title="Overview Dashboard"
        subtitle="Real-time kart operating parameters, driver metrics, and active session telemetry."
        badge={<StatusBadge status="ACTIVE" label={activeSessionId || 'STANDBY'} />}
      />

      {/* Primary Telemetry Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard
          label="Speed"
          value={speed}
          unit="km/h"
          subValue="Limit: 110 km/h"
          icon={<Gauge className="w-4 h-4" />}
          variant="highlight"
        />
        <MetricCard
          label="Engine RPM"
          value={rpm}
          unit="RPM"
          subValue="Redline: 9,500"
          icon={<Zap className="w-4 h-4" />}
          variant={rpm > 9000 ? 'danger' : 'normal'}
        />
        <MetricCard
          label="Engine Temp"
          value={temp}
          unit="°C"
          subValue="Max: 110 °C"
          icon={<Thermometer className="w-4 h-4" />}
          variant={parseFloat(temp) > 100 ? 'danger' : 'normal'}
        />
        <MetricCard
          label="Time-To-Contact"
          value={ttc}
          unit=""
          subValue="Threshold: 1.00s"
          icon={<ShieldAlert className="w-4 h-4" />}
          variant={warning === 'DANGER' ? 'danger' : warning === 'CAUTION' ? 'caution' : 'normal'}
        />
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard
          label="Throttle"
          value={throttle}
          unit=""
          subValue="Position sensor"
        />
        <MetricCard
          label="Steering Angle"
          value={steering}
          unit=""
          subValue="Rack travel ±35°"
          icon={<Compass className="w-4 h-4" />}
        />
        <MetricCard
          label="Lateral G-Force"
          value={latG}
          unit=""
          subValue="Grip Limit ~1.30g"
          icon={<Navigation className="w-4 h-4" />}
        />
        <MetricCard
          label="Best Lap Time"
          value="43.82"
          unit="s"
          subValue="Delta: -0.44s"
          variant="highlight"
        />
      </div>

      {/* Two Column Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Active Warning Panel */}
        <div className="bg-[#1E293B]/60 rounded-xl p-5 border border-slate-800 flex flex-col justify-between">
          <div>
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-4 flex items-center justify-between">
              Active Warnings & Alarms
              <span className="text-emerald-400 font-mono text-[11px]">ALL SYSTEMS GREEN</span>
            </h3>
            <div className="space-y-2.5">
              <div className="p-3 bg-slate-900/60 rounded-lg border border-slate-800/80 flex items-center justify-between">
                <div>
                  <div className="text-xs font-medium text-slate-200">Forward Ultrasonic TTC</div>
                  <div className="text-[11px] text-slate-500 font-mono">Distance: 450cm · Closing: 0.0 m/s</div>
                </div>
                <StatusBadge status="SAFE" />
              </div>
              <div className="p-3 bg-slate-900/60 rounded-lg border border-slate-800/80 flex items-center justify-between">
                <div>
                  <div className="text-xs font-medium text-slate-200">Engine Cylinder Head Temp</div>
                  <div className="text-[11px] text-slate-500 font-mono">Current: {temp}°C (Safe &lt; 105°C)</div>
                </div>
                <StatusBadge status="SAFE" />
              </div>
            </div>
          </div>
          <div className="text-[11px] text-slate-500 font-mono mt-4 pt-3 border-t border-slate-800">
            Advisory collision awareness active · 10 Hz refresh
          </div>
        </div>

        {/* Vehicle & Session Details */}
        <div className="bg-[#1E293B]/60 rounded-xl p-5 border border-slate-800 lg:col-span-2">
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-4">
            Active Outing Configuration
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-4">
            <div className="p-3 bg-slate-900/60 rounded-lg border border-slate-800">
              <div className="text-[10px] text-slate-500 uppercase font-mono">Chassis</div>
              <div className="text-sm font-semibold text-slate-200 font-mono mt-0.5">Kurukshetra IC-04</div>
            </div>
            <div className="p-3 bg-slate-900/60 rounded-lg border border-slate-800">
              <div className="text-[10px] text-slate-500 uppercase font-mono">Driver</div>
              <div className="text-sm font-semibold text-slate-200 font-mono mt-0.5">Arshad (#7)</div>
            </div>
            <div className="p-3 bg-slate-900/60 rounded-lg border border-slate-800">
              <div className="text-[10px] text-slate-500 uppercase font-mono">Circuit</div>
              <div className="text-sm font-semibold text-slate-200 font-mono mt-0.5">SKCET Proving Ground</div>
            </div>
            <div className="p-3 bg-slate-900/60 rounded-lg border border-slate-800">
              <div className="text-[10px] text-slate-500 uppercase font-mono">Track Condition</div>
              <div className="text-sm font-semibold text-emerald-400 font-mono mt-0.5">DRY · 31.5°C</div>
            </div>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Telemetry logging active via onboard ESP32. High-frequency MicroSD dump (100 Hz) recording to local FAT32 volume; live advisory telemetry streaming over wireless packet link at 20 Hz.
          </p>
        </div>
      </div>
    </div>
  );
};

