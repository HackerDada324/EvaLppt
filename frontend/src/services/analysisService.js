// In services/analysisService.js
import api from './api';

export const analysisService = {
  uploadVideo: async (file, options = {}) => {
    try {
      const formData = new FormData();
      formData.append('video', file);
      
      if (options.targetFps) {
        formData.append('target_fps', options.targetFps);
      }
      
      const config = {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          if (options.onProgress) {
            const percentCompleted = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
            options.onProgress(percentCompleted);
          }
        }
      };
      
      const response = await api.post('/api/analyze-body-motion', formData, config);
      return response;
    } catch (error) {
      console.error('API Error:', error);
      throw new Error(`Upload failed: ${error.response?.data?.error || error.message}`);
    }
  },
  
  getAnalysisStatus: async (analysisId) => {
    try {
      const response = await api.get(`/api/analysis/${analysisId}/status`);
      return response;
    } catch (error) {
      console.error('API Error:', error);
      throw new Error(`Failed to get analysis status: ${error.response?.data?.error || error.message}`);
    }
  },
  
  getAnalysisResults: async (analysisId) => {
    try {
      const response = await api.get(`/api/analysis/${analysisId}/results`);
      return response;
    } catch (error) {
      console.error('API Error:', error);
      throw new Error(`Failed to get analysis results: ${error.response?.data?.error || error.message}`);
    }
  },
  
  getSummary: async () => {
    try {
      const response = await api.get('/api/summary');
      return response;
    } catch (error) {
      console.error('API Error:', error);
      throw new Error(`Failed to get summary: ${error.response?.data?.error || error.message}`);
    }
  },

  testConnection: async () => {
    try {
      const response = await api.get('/api/test');
      console.log('API Connection Test:', response.data);
      return response;
    } catch (error) {
      console.error('API Connection Failed:', error);
      throw new Error(`Connection test failed: ${error.response?.data?.error || error.message}`);
    }
  }
};