/**
 * API Service Layer — Axios client for backend communication.
 * Base URL defaults to localhost:5000 for development.
 */
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
});

// --- Violations ---
export const getViolations = (page = 1, perPage = 20) =>
  api.get(`/api/violations?page=${page}&per_page=${perPage}`);

export const getViolationById = (id) =>
  api.get(`/api/violations/${id}`);

export const filterViolations = (filters) => {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== '') params.append(k, v);
  });
  return api.get(`/api/violations/filter?${params.toString()}`);
};

export const createViolation = (data) =>
  api.post('/api/violation', data);

// --- Stats ---
export const getStats = () =>
  api.get('/api/stats');

// --- AI ---
export const aiQuery = (query) =>
  api.post('/api/ai/query', { query });

export const aiExplain = (violationId) =>
  api.post(`/api/ai/explain/${violationId}`);

export const aiPredict = () =>
  api.get('/api/ai/predict');

// --- CV ---
export const uploadVideo = (formData) =>
  api.post('/api/cv/process-video', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });

export const startWebcam = () =>
  api.post('/api/cv/start-webcam');

export const stopWebcam = () =>
  api.post('/api/cv/stop-webcam');

export const getCVStatus = () =>
  api.get('/api/cv/status');

// --- Health ---
export const healthCheck = () =>
  api.get('/api/health');

export default api;
