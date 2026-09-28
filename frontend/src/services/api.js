import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to attach JWT token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle token expiration/unauthorized
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // If unauthorized, clear invalid token
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    }
    return Promise.reject(error);
  }
);

// API Service Methods
export const authService = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  getMe: () => api.get('/auth/me'),
};

export const profileService = {
  getProfile: () => api.get('/profile'),
  updateProfile: (data) => api.put('/profile', data),
};

export const subjectsService = {
  listSubjects: () => api.get('/subjects'),
  createSubject: (data) => api.post('/subjects', data),
  getSubject: (id) => api.get(`/subjects/${id}`),
  updateSubject: (id, data) => api.put(`/subjects/${id}`, data),
  deleteSubject: (id) => api.delete(`/subjects/${id}`),
};

export const topicsService = {
  listTopics: (subjectId) => api.get(`/subjects/${subjectId}/topics`),
  createTopic: (subjectId, data) => api.post(`/subjects/${subjectId}/topics`, data),
  getTopic: (id) => api.get(`/topics/${id}`),
  updateTopic: (id, data) => api.put(`/topics/${id}`, data),
  deleteTopic: (id) => api.delete(`/topics/${id}`),
};

export const studyPlanService = {
  generatePlan: (data) => api.post('/study-plans/generate', data),
  listPlans: () => api.get('/study-plans'),
  getPlan: (id) => api.get(`/study-plans/${id}`),
};

export const aiService = {
  summarize: (data) => api.post('/ai/summarize', data),
  ask: (data) => api.post('/ai/ask', data),
  analyzePerformance: (subjectId) => api.post('/ai/performance/analyze', { subject_id: subjectId }),
};

export const quizService = {
  generateQuiz: (data) => api.post('/quizzes/generate', data),
  listQuizzes: (subjectId) => api.get('/quizzes', { params: subjectId ? { subject_id: subjectId } : {} }),
  getQuiz: (id) => api.get(`/quizzes/${id}`),
  submitQuiz: (id, answers) => api.post(`/quizzes/${id}/submit`, { answers }),
  getAttempts: (id) => api.get(`/quizzes/${id}/attempts`),
};

export const progressService = {
  updateProgress: (data) => api.post('/progress', data),
  listProgress: () => api.get('/progress'),
  getProgressBySubject: (subjectId) => api.get(`/progress/subjects/${subjectId}`),
  getProgressByTopic: (topicId) => api.get(`/progress/topics/${topicId}`),
};

export const dashboardService = {
  getDashboard: () => api.get('/dashboard'),
};

export default api;
