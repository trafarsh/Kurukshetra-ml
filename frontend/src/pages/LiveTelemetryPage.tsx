import React from 'react';
import { PageHeader } from '../components/common/PageHeader';
import { MetricCard } from '../components/common/MetricCard';
import { StatusBadge } from '../components/common/StatusBadge';
import { useTelemetryStore } from '../stores/telemetryStore';
import { Gauge, Zap, Thermometer, ShieldAlert } from 'lucide-react';

export const LiveTelemetryPage: React.FC = () => {
  const { currentData, connectionStatus, setConnectionStatus, pushTelemetry } = useTelemetryStore();
  const [isSimulating, setIsSimulating] = React.useState(false);

  // Live simulation generator for development & demonstration
  React.useEffect(() => {
    let timer: ReturnType<typeof setInterval>;
    if (isSimulating) {
      setConnectionStatus('connected');
      let angle = 0;
      timer = setInterval(() => {
        angle += 0.1;
        const speed = 45 + 35 * Math.sin(angle);
        const rpm = Math.floor(4000 + 4200 * Math.abs(Math.sin(angle * 1.2)));
        const temp = 88.0 + 4.5 * Math.sin(angle * 0.3);
        const steering = 22 * Math.cos(angle * 0.8);
        const throttle = Math.max(0, 100 * Math.sin(angle));
        const accelX = 0.8 * Math.cos(angle);
        const accelY = (Math.pow(speed / 3.6, 2) / 25.0) / 9.81 * Math.sin(angle * 0.8);
        const dist = 350 + 200 * Math.cos(angle * 0.5);
        const closeSpeed = Math.max(0, 5.0 * Math.sin(angle * 0.5));
        const ttc = closeSpeed > 0.5 ? dist / (closeSpeed * 100) : null;
        const warning = ttc && ttc < 1.0 ? 'DANGER' : ttc && ttc < 2.5 ? 'CAUTION' : 'SAFE';

        pushTelemetry({
          timestamp_us: Date.now() * 1000,
          speed_kmh: speed,
          engine_rpm: rpm,
          engine_temp_c: temp,
          steering_angle_deg: steering,
          throttle_percent: throttle,
          accel_x_g: accelX,
          accel_y_g: accelY,
          obstacle_distance_cm: dist,
          closing_speed_mps: closeSpeed,
          ttc_seconds: ttc,
          warning_level: warning,
          sensor_status: 'ALL_OK',
        });
      }, 50); // 20 Hz
    } else {
      setConnectionStatus('disconnected');
    }
    return () => clearInterval(timer);
  }, [isSimulating, setConnectionStatus, pushTelemetry]);

  const speed = currentData ? currentData.speed_kmh.toFixed(1) : '0.0';
  const rpm = currentData ? currentData.engine_rpm : 0;
  const temp = currentData ? currentData.engine_temp_c.toFixed(1) : '0.0';
  const ttc = currentData && currentData.ttc_seconds ? `${currentData.ttc_seconds.toFixed(2)} s` : '∞';
  const warning = currentData ? currentData.warning_level : 'SAFE';

  return (
    <div className="space-y-6">
      <PageHeader
        title="Live Telemetry Feed"
        subtitle="Real-time multi-signal sensor bus (16-byte UDP packet receiver at 20 Hz)."
        badge={<StatusBadge status={connectionStatus} />}
        actions={
          <button
            onClick={() => setIsSimulating(!isSimulating)}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono font-semibold transition-all border ${
              isSimulating
                ? 'bg-red-950 text-red-400 border-red-800 hover:bg-red-900'
                : 'bg-emerald-950 text-emerald-400 border-emerald-800 hover:bg-emerald-900'
            }`}
          >
            {isSimulating ? 'HALT LIVE SIMULATION' : 'START 20Hz DEMO STREAM'}
          </button>
        }
      />

      {/* Primary Gauges */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard label="Vehicle Speed" value={speed} unit="km/h" icon={<Gauge className="w-4 h-4" />} variant="highlight" />
        <MetricCard label="Engine RPM" value={rpm} unit="RPM" icon={<Zap className="w-4 h-4" />} variant={rpm > 8500 ? 'danger' : 'normal'} />
        <MetricCard label="Cylinder Temp" value={temp} unit="°C" icon={<Thermometer className="w-4 h-4" />} variant={parseFloat(temp) > 95 ? 'caution' : 'normal'} />
        <MetricCard
          label="TTC Warning"
          value={ttc}
          subValue={currentData?.closing_speed_mps ? `Closing: ${currentData.closing_speed_mps.toFixed(1)} m/s` : 'Clear'}
          icon={<ShieldAlert className="w-4 h-4" />}
          variant={warning === 'DANGER' ? 'danger' : warning === 'CAUTION' ? 'caution' : 'normal'}
        />
      </div>

      {/* Driver Controls & Dynamics Bars */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-[#1E293B]/60 p-5 rounded-xl border border-slate-800 space-y-4">
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider font-mono">
            Driver Inputs & Throttle Position
          </h3>
          <div>
            <div className="flex justify-between text-xs font-mono text-slate-300 mb-1">
              <span>THROTTLE</span>
              <span>{currentData ? `${currentData.throttle_percent.toFixed(0)}%` : '0%'}</span>
            </div>
            <div className="w-full h-3 bg-slate-900 rounded-full overflow-hidden border border-slate-800">
              <div
                className="h-full bg-emerald-500 transition-all duration-75"
                style={{ width: `${currentData ? currentData.throttle_percent : 0}%` }}
              />
            </div>
          </div>

          <div>
            <div className="flex justify-between text-xs font-mono text-slate-300 mb-1">
              <span>STEERING ANGLE</span>
              <span>{currentData ? `${currentData.steering_angle_deg.toFixed(1)}°` : '0.0°'}</span>
            </div>
            <div className="w-full h-3 bg-slate-900 rounded-full overflow-hidden border border-slate-800 relative">
              <div
                className="h-full bg-blue-500 transition-all duration-75 absolute"
                style={{
                  left: '50%',
                  width: `${Math.abs(currentData ? currentData.steering_angle_deg : 0) * 1.4}%`,
                  transform: (currentData?.steering_angle_deg || 0) < 0 ? 'translateX(-100%)' : 'none',
                }}
              />
            </div>
          </div>
        </div>

        <div className="bg-[#1E293B]/60 p-5 rounded-xl border border-slate-800 space-y-4">
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider font-mono">
            G-Force Acceleration Vector (IMU)
          </h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="p-3 bg-slate-900/80 rounded-lg border border-slate-800">
              <div className="text-[10px] text-slate-500 font-mono">LONGITUDINAL (Ax)</div>
              <div className="text-xl font-bold font-mono text-slate-200 mt-1">
                {currentData ? `${currentData.accel_x_g.toFixed(2)} g` : '0.00 g'}
              </div>
            </div>
            <div className="p-3 bg-slate-900/80 rounded-lg border border-slate-800">
              <div className="text-[10px] text-slate-500 font-mono">LATERAL (Ay)</div>
              <div className="text-xl font-bold font-mono text-slate-200 mt-1">
                {currentData ? `${currentData.accel_y_g.toFixed(2)} g` : '0.00 g'}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
