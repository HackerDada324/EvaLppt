import api from './api';

export const analysisService = {
  uploadVideo: async (file) => {
    const formData = new FormData();
    formData.append('video', file);
    
    return api.post('/uploads/video', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: (progressEvent) => {
        // You can track upload progress here
        const percentCompleted = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        console.log(`Upload Progress: ${percentCompleted}%`);
      }
    });
  },
  
  getAnalysisResults: async (videoId) => {
    return api.get(`/analysis/${videoId}`);
  },
  
  // Add other analysis-related API calls
};