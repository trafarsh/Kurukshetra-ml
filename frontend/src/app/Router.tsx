import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { DashboardLayout } from '../layouts/DashboardLayout';

import { OverviewPage } from '../pages/OverviewPage';
import { LiveTelemetryPage } from '../pages/LiveTelemetryPage';
import { TrackMapPage } from '../pages/TrackMapPage';
import { LapAnalysisPage } from '../pages/LapAnalysisPage';
import { DriverAnalysisPage } from '../pages/DriverAnalysisPage';
import { EngineHealthPage } from '../pages/EngineHealthPage';
import { MLCentrePage } from '../pages/MLCentrePage';
import { DigitalTwinPage } from '../pages/DigitalTwinPage';
import { WhatIfPage } from '../pages/WhatIfPage';
import { SessionHistoryPage } from '../pages/SessionHistoryPage';
import { ReportsPage } from '../pages/ReportsPage';

export const AppRouter: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<DashboardLayout />}>
          <Route index element={<OverviewPage />} />
          <Route path="live" element={<LiveTelemetryPage />} />
          <Route path="track" element={<TrackMapPage />} />
          <Route path="laps" element={<LapAnalysisPage />} />
          <Route path="driver" element={<DriverAnalysisPage />} />
          <Route path="engine" element={<EngineHealthPage />} />
          <Route path="ml" element={<MLCentrePage />} />
          <Route path="twin" element={<DigitalTwinPage />} />
          <Route path="whatif" element={<WhatIfPage />} />
          <Route path="sessions" element={<SessionHistoryPage />} />
          <Route path="reports" element={<ReportsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

