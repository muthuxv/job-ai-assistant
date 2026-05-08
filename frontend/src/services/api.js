import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ===== CV =====
export const uploadCV = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await axios.post(`${API_BASE_URL}/cvs/upload`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const getActiveCV = async () => {
  const response = await api.get('/cvs/active');
  return response.data;
};

export const getAllCVs = async () => {
  const response = await api.get('/cvs/');
  return response.data;
};

// ===== JOBS =====
export const analyzeJob = async (description, url) => {
  const response = await api.post('/jobs/analyze', { description, url });
  return response.data;
};

export const getAllJobs = async () => {
  const response = await api.get('/jobs/');
  return response.data;
};

export const getJob = async (jobId) => {
  const response = await api.get(`/jobs/${jobId}`);
  return response.data;
};

export const recalculateAllScores = async () => {
  const response = await api.post('/jobs/recalculate-all-scores');
  return response.data;
};

// ===== APPLICATIONS =====
export const getAllApplications = async () => {
  const response = await api.get('/applications/');
  return response.data;
};

export const getApplication = async (applicationId) => {
  const response = await api.get(`/applications/${applicationId}`);
  return response.data;
};

export const updateApplication = async (applicationId, data) => {
  const response = await api.patch(`/applications/${applicationId}`, data);
  return response.data;
};

export const deleteApplication = async (applicationId) => {
  const response = await api.delete(`/applications/${applicationId}`);
  return response.data;
};

export const getStats = async () => {
  const response = await api.get('/applications/stats/overview');
  return response.data;
};

export const getDashboardAnalytics = async () => {
  const response = await api.get('/applications/analytics/dashboard');
  return response.data;
};

// ===== COVER LETTERS =====
export const generateCoverLetter = async (applicationId, tone) => {
  const response = await api.post('/cover-letters/generate', {
    application_id: applicationId,
    tone,
  });
  return response.data;
};

export const generateAllTones = async (applicationId) => {
  const response = await api.post(
    `/cover-letters/generate-all-tones?application_id=${applicationId}`
  );
  return response.data;
};

export const getCoverLettersForApplication = async (applicationId) => {
  const response = await api.get(`/cover-letters/application/${applicationId}`);
  return response.data;
};

// ===== INTERVIEW PREP =====
export const getInterviewPrep = async (applicationId) => {
  const response = await api.get(`/interview-prep/${applicationId}`);
  return response.data;
};

export default api;
