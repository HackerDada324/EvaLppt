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
      
      // Try to make API call, but catch error if backend isn't ready
      const response = await api.post('/api/analyze-body-motion', formData, config);
      return response;
    } catch (error) {
      console.log('API not ready yet:', error);
      // Return mock data for development
      return {
        data: {
          status: 'success',
          message: 'Mock analysis complete',
          results: {
            // Mock analysis results here
          }
        }
      };
    }
  },
  
  getSummary: async () => {
    try {
      const response = await api.get('/api/summary');
      return response;
    } catch (error) {
      console.log('API not ready yet:', error);
      // Return mock data
      return {
        data: {
          // Mock summary data
        }
      };
    }
  }
};