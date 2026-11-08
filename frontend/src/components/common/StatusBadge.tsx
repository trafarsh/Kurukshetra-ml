import React from 'react';
import { clsx } from 'clsx';

interface StatusBadgeProps {
  status: 'SAFE' | 'CAUTION' | 'DANGER' | 'connected' | 'reconnecting' | 'disconnected' | 'ACTIVE' | 'COMPLETED' | 'ABORTED';
  label?: string;
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, label, className }) => {
  const displayLabel = label || status;

  const colorStyles: Record<string, string> = {
    SAFE: 'bg-emerald-950 text-emerald-400 border-emerald-800',
    connected: 'bg-emerald-950 text-emerald-400 border-emerald-800',
    ACTIVE: 'bg-emerald-950 text-emerald-400 border-emerald-800',
    CAUTION: 'bg-amber-950 text-amber-400 border-amber-800',
    reconnecting: 'bg-amber-950 text-amber-400 border-amber-800',
    DANGER: 'bg-red-950 text-red-400 border-red-800 animate-pulse',
    disconnected: 'bg-slate-800 text-slate-400 border-slate-700',
    COMPLETED: 'bg-blue-950 text-blue-400 border-blue-800',
    ABORTED: 'bg-red-950 text-red-400 border-red-800',
  };

  const dotColors: Record<string, string> = {
    SAFE: 'bg-emerald-500',
    connected: 'bg-emerald-500',
    ACTIVE: 'bg-emerald-500',
    CAUTION: 'bg-amber-500',
    reconnecting: 'bg-amber-500',
    DANGER: 'bg-red-500',
    disconnected: 'bg-slate-500',
    COMPLETED: 'bg-blue-500',
    ABORTED: 'bg-red-500',
  };

  const badgeStyle = colorStyles[status] || 'bg-slate-800 text-slate-400 border-slate-700';
  const dotColor = dotColors[status] || 'bg-slate-500';

  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border tracking-wide uppercase',
        badgeStyle,
        className
      )}
    >
      <span className={clsx('w-1.5 h-1.5 rounded-full', dotColor)} />
      {displayLabel}
    </span>
  );
};

