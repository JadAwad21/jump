import axios from 'axios';

const API_BASE_URL = '/api/v1';

// Create axios client
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add Bearer token automatically
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export default apiClient;

// ============================================================================
// USER / AUTH APIs
// ============================================================================
export const userAPI = {
  me: () => apiClient.get('/users/users/me/'),
  mfaStatus: () => apiClient.get('/authentication/mfa/status/'),
  mfaVerify: (code) =>
    apiClient.post('/authentication/mfa/verify/', { code }),
};

// ============================================================================
// TAG APIs  (needed by TagManagement.jsx)
// ============================================================================
export const tagAPI = {
  list: (params = {}) => apiClient.get('/blockchain/tags/', { params }),
  create: (data) => apiClient.post('/blockchain/tags/', data),
  update: (id, data) => apiClient.put(`/blockchain/tags/${id}/`, data),
  delete: (id) => apiClient.delete(`/blockchain/tags/${id}/`),
};

// ============================================================================
// INVESTIGATION APIs
// ============================================================================
export const investigationAPI = {
  list: (params = {}) =>
    apiClient.get('/blockchain/investigations/', { params }),

  get: (id) => apiClient.get(`/blockchain/investigations/${id}/`),

  create: (data) => apiClient.post('/blockchain/investigations/', data),

  update: (id, data) =>
    apiClient.put(`/blockchain/investigations/${id}/`, data),

  archive: (id, reason) =>
    apiClient.post(`/blockchain/investigations/${id}/archive/`, { reason }),

  reopen: (id, reason) =>
    apiClient.post(`/blockchain/investigations/${id}/reopen/`, { reason }),
};

// ============================================================================
// EVIDENCE APIs
// ============================================================================
export const evidenceAPI = {
  list: (params = {}) => apiClient.get('/blockchain/evidence/', { params }),

  get: (id) => apiClient.get(`/blockchain/evidence/${id}/`),

  upload: (formData) =>
    apiClient.post('/blockchain/evidence/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),

  download: (id) =>
    apiClient.get(`/blockchain/evidence/${id}/download/`, {
      responseType: 'blob',
    }),

  verify: (id) => apiClient.get(`/blockchain/evidence/${id}/verify/`),
};

// ============================================================================
// INVESTIGATION TAG APIs
// ============================================================================
export const investigationTagAPI = {
  list: (params = {}) =>
    apiClient.get('/blockchain/investigation-tags/', { params }),

  assign: (investigationId, tagId) =>
    apiClient.post('/blockchain/investigation-tags/', {
      investigation: investigationId,
      tag: tagId,
    }),

  remove: (id) =>
    apiClient.delete(`/blockchain/investigation-tags/${id}/`),
};

// ============================================================================
// NOTES APIs
// ============================================================================
export const noteAPI = {
  list: (params = {}) => apiClient.get('/blockchain/notes/', { params }),

  create: (investigationId, content) =>
    apiClient.post('/blockchain/notes/', {
      investigation: investigationId,
      content,
    }),
};

// ============================================================================
// ACTIVITY APIs
// ============================================================================
export const activityAPI = {
  list: (params = {}) => apiClient.get('/blockchain/activities/', { params }),
  markViewed: (id) =>
    apiClient.post(`/blockchain/activities/${id}/mark_viewed/`),
};

// ============================================================================
// TRANSACTION APIs
// ============================================================================
export const transactionAPI = {
  list: (params = {}) =>
    apiClient.get('/blockchain/transactions/', { params }),

  get: (id) => apiClient.get(`/blockchain/transactions/${id}/`),
};

// ============================================================================
// GUID APIs
// ============================================================================
export const guidAPI = {
  resolve: (guid, reason) =>
    apiClient.post('/blockchain/guid/resolve/', { guid, reason }),
};

