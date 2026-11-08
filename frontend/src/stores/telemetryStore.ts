import { create } from 'zustand';
import type { TelemetryPoint, ConnectionStatus } from '../types';

const MAX_HISTORY = 300; // 15 seconds buffer at 20 Hz

interface TelemetryStore {
  connectionStatus: ConnectionStatus;
  activeSessionId: string | null;
  currentData: TelemetryPoint | null;
  history: TelemetryPoint[];
  lastUpdateTime: number | null;

  setConnectionStatus: (status: ConnectionStatus) => void;
  setActiveSessionId: (id: string | null) => void;
  pushTelemetry: (point: TelemetryPoint) => void;
  clearHistory: () => void;
}

export const useTelemetryStore = create<TelemetryStore>((set) => ({
  connectionStatus: 'disconnected',
  activeSessionId: null,
  currentData: null,
  history: [],
  lastUpdateTime: null,

  setConnectionStatus: (status) => set({ connectionStatus: status }),
  setActiveSessionId: (id) => set({ activeSessionId: id }),
  pushTelemetry: (point) =>
    set((state) => ({
      currentData: point,
      lastUpdateTime: Date.now(),
      history: [...state.history.slice(-(MAX_HISTORY - 1)), point],
    })),
  clearHistory: () => set({ history: [], currentData: null, lastUpdateTime: null }),
}));

