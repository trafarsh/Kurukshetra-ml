import React from 'react';
import { PageHeader } from '../components/common/PageHeader';
import { MetricCard } from '../components/common/MetricCard';
import { StatusBadge } from '../components/common/StatusBadge';
import { Brain, Layers, Cpu, Play } from 'lucide-react';

export const MLCentrePage: React.FC = () => {
  const models = [
    {
      name: 'Engine Anomaly Detector',
      algo: 'Isolation Forest (scikit-learn)',
      version: 'v1.0.0',
      status: 'ACTIVE',
      accuracy: 'FPR: 2.1%',
      purpose: 'Identifies unexpected temperature / RPM / vibration drift before mechanical seizure.',
    },
    {
      name: 'Lap-Time Predictor',
      algo: 'RandomForest & GradientBoosting Regressor',
      version: 'v1.0.0',
      status: 'ACTIVE',
      accuracy: 'MAE: 0.38s (R² = 0.89)',
      purpose: 'Forecasts lap time from sector speeds without temporal data leakage.',
    },
    {
      name: 'Driver Behaviour Classifier',
      algo: 'Rule-Calibrated Decision Tree',
      version: 'v1.0.0',
      status: 'ACTIVE',
      accuracy: 'F1: 0.91',
      purpose: 'Categorizes throttle onset rate, steering smoothness, and corner entry speed.',
    },
    {
      name: 'Dynamic Grip Estimator',
      algo: 'Physics-Constrained Lateral Regression',
      version: 'v1.0.0',
      status: 'ACTIVE',
      accuracy: 'RMSE: 0.04 μ',
      purpose: 'Estimates effective tire grip limit μ from lateral acceleration and radius.',
    },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Machine Learning Centre"
        subtitle="Model registry, training manifests, feature importance, and inference pipelines."
        badge={<StatusBadge status="ACTIVE" label="4 Production Models" />}
      />

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard label="Registered Models" value="4" subValue="All models active" variant="highlight" />
        <MetricCard label="Training Sessions" value="12" subValue="Group-split validation" />
        <MetricCard label="Inference Latency" value="4.2" unit="ms" subValue="Sub-15ms budget" variant="highlight" />
        <MetricCard label="Data Leakage Check" value="PASSED" subValue="Session-grouped CV" />
      </div>

      {/* Model Registry Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {models.map((m) => (
          <div key={m.name} className="bg-[#1E293B]/60 p-5 rounded-xl border border-slate-800 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-mono text-emerald-400 font-bold">{m.version}</span>
                <StatusBadge status="SAFE" label={m.status} />
              </div>
              <h3 className="text-base font-bold text-slate-100 font-mono">{m.name}</h3>
              <p className="text-xs text-slate-400 mt-1 font-sans">{m.purpose}</p>

              <div className="mt-4 p-3 bg-slate-900/60 rounded-lg border border-slate-800 space-y-1 font-mono text-xs">
                <div className="flex justify-between">
                  <span className="text-slate-400">Algorithm:</span>
                  <span className="text-slate-200">{m.algo}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Performance:</span>
                  <span className="text-emerald-400">{m.accuracy}</span>
                </div>
              </div>
            </div>

            <div className="mt-4 pt-3 border-t border-slate-800 flex justify-end">
              <button className="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-xs font-mono text-slate-200 rounded border border-slate-700 transition">
                Inspect Manifest
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

