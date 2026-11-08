import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import {
  LayoutDashboard,
  Radio,
  Map,
  Timer,
  User,
  Thermometer,
  Brain,
  Box,
  FlaskConical,
  History,
  FileText,
  Activity,
  Wifi,
  WifiOff,
} from 'lucide-react';
import { clsx } from 'clsx';
import { useTelemetryStore } from '../stores/telemetryStore';
import { StatusBadge } from '../components/common/StatusBadge';

export const DashboardLayout: React.FC = () => {
  const { connectionStatus, activeSessionId } = useTelemetryStore();
  const [currentTime, setCurrentTime] = React.useState<string>('');

  React.useEffect(() => {
    const updateClock = () => {
      const now = new Date();
      setCurrentTime(
        now.toLocaleTimeString('en-GB', { hour12: false }) + '.' + String(now.getMilliseconds()).padStart(3, '0').slice(0, 2)
      );
    };
    updateClock();
    const interval = setInterval(updateClock, 50);
    return () => clearInterval(interval);
  }, []);

  const navItems = [
    { name: 'Overview', path: '/', icon: LayoutDashboard },
    { name: 'Live Telemetry', path: '/live', icon: Radio },
    { name: 'Track Map', path: '/track', icon: Map },
    { name: 'Lap Analysis', path: '/laps', icon: Timer },
    { name: 'Driver Analysis', path: '/driver', icon: User },
    { name: 'Engine Health', path: '/engine', icon: Thermometer },
    { name: 'ML Centre', path: '/ml', icon: Brain },
    { name: 'Digital Twin', path: '/twin', icon: Box },
    { name: 'What-If Analysis', path: '/whatif', icon: FlaskConical },
    { name: 'Session History', path: '/sessions', icon: History },
    { name: 'Reports', path: '/reports', icon: FileText },
  ];

  return (
    <div className="flex h-screen bg-[#0B0F19] text-slate-100 overflow-hidden font-sans">
      {/* Sidebar */}
      <aside className="w-64 bg-[#111827] border-r border-slate-800 flex flex-col justify-between shrink-0">
        <div>
          {/* Brand Header */}
          <div className="p-4 border-b border-slate-800 flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 font-bold font-mono text-sm">
                KK
              </div>
              <div>
                <h2 className="text-sm font-bold tracking-wider uppercase text-slate-100 font-mono">
                  Kurukshetra
                </h2>
                <p className="text-[10px] text-slate-400 uppercase tracking-widest font-mono">
                  EKVC S4 · SKCET
                </p>
              </div>
            </div>
            <span className="text-[10px] bg-slate-800 text-slate-300 px-1.5 py-0.5 rounded border border-slate-700 font-mono">
              V1.0
            </span>
          </div>

          {/* Nav Items */}
          <nav className="p-3 space-y-1 overflow-y-auto max-h-[calc(100vh-140px)]">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) =>
                    clsx(
                      'flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium tracking-wide transition-colors duration-150',
                      isActive
                        ? 'bg-slate-800 text-emerald-400 border-l-2 border-emerald-500 font-semibold'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                    )
                  }
                >
                  <Icon className="w-4 h-4 shrink-0" />
                  <span>{item.name}</span>
                </NavLink>
              );
            })}
          </nav>
        </div>

        {/* Footer Subsystem Status */}
        <div className="p-3.5 border-t border-slate-800 bg-[#0E1524]">
          <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 mb-1.5">
            <span className="flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5 text-emerald-400" />
              TELEMETRY BUS
            </span>
            <span className="text-emerald-400">OK</span>
          </div>
          <div className="text-[10px] text-slate-500 font-mono truncate">
            Session: {activeSessionId || 'No active stint'}
          </div>
        </div>
      </aside>

      {/* Main Container */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Pit-Wall Bar */}
        <header className="h-12 bg-[#111827]/80 backdrop-blur border-b border-slate-800 px-6 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              {connectionStatus === 'connected' ? (
                <Wifi className="w-4 h-4 text-emerald-400" />
              ) : (
                <WifiOff className="w-4 h-4 text-slate-500" />
              )}
              <StatusBadge status={connectionStatus} />
            </div>
            <div className="h-4 w-px bg-slate-800" />
            <span className="text-xs font-mono text-slate-400 uppercase tracking-widest hidden sm:inline">
              PIT WALL TELEMETRY STATION
            </span>
          </div>

          <div className="flex items-center gap-4">
            <div className="font-mono text-xs font-semibold text-emerald-400 bg-slate-900/80 px-2.5 py-1 rounded border border-slate-800">
              UTC {currentTime}
            </div>
          </div>
        </header>

        {/* Dynamic Content View */}
        <main className="flex-1 overflow-y-auto p-6 bg-[#0B0F19]">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

