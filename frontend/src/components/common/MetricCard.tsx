import React from 'react';
import { clsx } from 'clsx';

interface MetricCardProps {
  label: string;
  value: string | number;
  unit?: string;
  subValue?: string;
  variant?: 'normal' | 'caution' | 'danger' | 'highlight';
  icon?: React.ReactNode;
  className?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  unit,
  subValue,
  variant = 'normal',
  icon,
  className,
}) => {
  const borderVariants = {
    normal: 'border-slate-800 hover:border-slate-700',
    caution: 'border-amber-600/50 bg-amber-950/10',
    danger: 'border-red-600/60 bg-red-950/20 shadow-red-950/30 shadow-md',
    highlight: 'border-emerald-600/50 bg-emerald-950/10',
  };

  const textVariants = {
    normal: 'text-slate-100',
    caution: 'text-amber-400',
    danger: 'text-red-400',
    highlight: 'text-emerald-400',
  };

  return (
    <div
      className={clsx(
        'bg-[#1E293B]/80 rounded-xl p-4 border transition-all duration-200 flex flex-col justify-between',
        borderVariants[variant],
        className
      )}
    >
      <div className="flex items-center justify-between gap-2 mb-2">
        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{label}</span>
        {icon && <div className="text-slate-400 opacity-80">{icon}</div>}
      </div>

      <div className="flex items-baseline gap-1.5 my-1">
        <span className={clsx('text-2xl font-bold tracking-tight font-mono', textVariants[variant])}>
          {value}
        </span>
        {unit && <span className="text-xs font-medium text-slate-400">{unit}</span>}
      </div>

      {subValue && (
        <div className="text-xs text-slate-500 font-mono mt-1 pt-1 border-t border-slate-800/80">
          {subValue}
        </div>
      )}
    </div>
  );
};

