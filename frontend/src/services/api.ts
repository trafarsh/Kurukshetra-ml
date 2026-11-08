import axios from 'axios';
import type { Vehicle, Driver, Track, Session } from '../types';

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('kk_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('kk_token');
    }
    return Promise.reject(error);
  }
);

export default api;

export const vehiclesApi = {
  list: () => api.get<Vehicle[]>('/vehicles'),
  create: (data: Partial<Vehicle>) => api.post<Vehicle>('/vehicles', data),
  get: (id: string) => api.get<Vehicle>(`/vehicles/${id}`),
};

export const driversApi = {
  list: () => api.get<Driver[]>('/drivers'),
  create: (data: Partial<Driver>) => api.post<Driver>('/drivers', data),
  get: (id: string) => api.get<Driver>(`/drivers/${id}`),
};

export const tracksApi = {
  list: () => api.get<Track[]>('/tracks'),
  create: (data: Partial<Track>) => api.post<Track>('/tracks', data),
  get: (id: string) => api.get<Track>(`/tracks/${id}`),
};

export const sessionsApi = {
  list: (params?: Record<string, string>) => api.get<Session[]>('/sessions', { params }),
  create: (data: Partial<Session>) => api.post<Session>('/sessions', data),
  get: (id: string) => api.get<Session>(`/sessions/${id}`),
  finalize: (id: string) => api.post<Session>(`/sessions/${id}/finalize`),
};

export const telemetryApi = {
  ingest: (data: any) => api.post('/telemetry/ingest', data),
  get: (sessionId: string, params?: Record<string, any>) =>
    api.get(`/telemetry/${sessionId}`, { params }),
  summary: (sessionId: string) => api.get(`/telemetry/${sessionId}/summary`),
};

export const healthApi = {
  check: () => api.get('/health'),
  ready: () => api.get('/health/ready'),
};

export const phase7Api = {
  recommend: (metrics: Record<string, number>) =>
    api.post('/recommendations', { metrics }),
  generateReport: (data: {
    report_id: string;
    report_type?: string;
    telemetry: Record<string, unknown>[];
    summary: Record<string, unknown>;
  }) => api.post('/reports', data),
  downloadReport: (reportId: string, format: 'pdf' | 'csv') =>
    api.get(`/reports/${encodeURIComponent(reportId)}/${format}`, { responseType: 'blob' }),
  prepareReplay: (records: Record<string, unknown>[], speed = 1) =>
    api.post('/replay/prepare', { records, speed }),
};
