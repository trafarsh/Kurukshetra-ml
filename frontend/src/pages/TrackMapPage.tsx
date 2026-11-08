import React from 'react';
import { PageHeader } from '../components/common/PageHeader';
import { StatusBadge } from '../components/common/StatusBadge';
import { MapPin, Compass, Navigation } from 'lucide-react';

export const TrackMapPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Circuit & Track Reconstruct"
        subtitle="GPS trace alignment, dead-reckoning positioning, and corner sector discretisation."
        badge={<StatusBadge status="ACTIVE" label="SKCET Proving Ground" />}
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Track Canvas Projection */}
        <div className="lg:col-span-2 bg-[#1E293B]/60 p-5 rounded-xl border border-slate-800 flex flex-col justify-between min-h-[420px]">
          <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-2">
            <span>CIRCUIT TRAJECTORY: 850m (9 TURNS)</span>
            <span className="text-emerald-400">ESTIMATED ACCURACY: ±1.8m</span>
          </div>

          {/* SVG Track Representation */}
          <div className="flex-1 flex items-center justify-center p-6 relative">
            <svg viewBox="0 0 500 300" className="w-full max-w-lg h-auto stroke-emerald-500 fill-none stroke-[6]">
              {/* Circuit Outline */}
              <path
                d="M 60,150 C 60,70 140,50 220,50 C 300,50 420,70 440,120 C 460,170 380,240 300,240 C 220,240 180,180 140,180 C 100,180 60,220 60,150 Z"
                className="stroke-slate-700 stroke-[8]"
              />
              <path
                d="M 60,150 C 60,70 140,50 220,50 C 300,50 420,70 440,120 C 460,170 380,240 300,240 C 220,240 180,180 140,180 C 100,180 60,220 60,150 Z"
                className="stroke-emerald-400 stroke-[3]"
              />
              {/* Start Finish Line */}
              <line x1="60" y1="130" x2="60" y2="170" stroke="#F59E0B" strokeWidth="4" />
              {/* Active Kart Marker */}
              <circle cx="220" cy="50" r="7" className="fill-red-500 stroke-white stroke-2 animate-pulse" />
            </svg>
            <div className="absolute top-2 left-2 bg-slate-900/80 px-2 py-1 rounded text-[10px] font-mono text-slate-400 border border-slate-800">
              Start/Finish: Turn 9 Exit
            </div>
            <div className="absolute bottom-2 right-2 bg-slate-900/80 px-2 py-1 rounded text-[10px] font-mono text-emerald-400 border border-slate-800">
              Kart: Sector 1 (Approaching Turn 1 Apex)
            </div>
          </div>

          <div className="text-[11px] font-mono text-slate-500 border-t border-slate-800 pt-3 flex justify-between">
            <span>Dead Reckoning (Appendix D kinematic model) active</span>
            <span>Surface: Dry Asphalt · μ ~ 1.18</span>
          </div>
        </div>

        {/* Sector Information */}
        <div className="bg-[#1E293B]/60 p-5 rounded-xl border border-slate-800 space-y-4">
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider font-mono">
            Sector Geometry Breakdown
          </h3>
          <div className="space-y-3">
            <div className="p-3 bg-slate-900/70 rounded-lg border border-slate-800">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-slate-300 font-bold">SECTOR 1</span>
                <span className="text-emerald-400">0m – 280m</span>
              </div>
              <div className="text-[11px] text-slate-500 mt-1">Main Straight · Turn 1 Hairpin (R = 18.5m)</div>
            </div>
            <div className="p-3 bg-slate-900/70 rounded-lg border border-slate-800">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-slate-300 font-bold">SECTOR 2</span>
                <span className="text-emerald-400">280m – 590m</span>
              </div>
              <div className="text-[11px] text-slate-500 mt-1">Esses Chicanes · Turn 4 Sweeper (R = 32.0m)</div>
            </div>
            <div className="p-3 bg-slate-900/70 rounded-lg border border-slate-800">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-slate-300 font-bold">SECTOR 3</span>
                <span className="text-emerald-400">590m – 850m</span>
              </div>
              <div className="text-[11px] text-slate-500 mt-1">Back Straight · Final Turn 9 (R = 24.0m)</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

