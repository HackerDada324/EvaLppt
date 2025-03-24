import axios from 'axios';

// Base API URL - change this based on your environment
const API_BASE_URL = 'http://localhost:5000';

// Create a custom axios instance
const api = axios.create({
  baseURL: API_BASE_URL
});

// Analysis service methods
export const analysisService = {
  /**
   * Upload video for analysis
   * @param {File} file - The video file to upload
   * @param {Object} options - Optional parameters
   * @returns {Promise} - Promise with the analysis results
   */
  uploadVideo: async (file, options = {}) => {
    const formData = new FormData();
    formData.append('video', file);
    
    // Add any additional options
    if (options.targetFps) {
      formData.append('target_fps', options.targetFps);
    }
    
    // Create upload request with progress tracking
    const config = {
      onUploadProgress: (progressEvent) => {
        if (options.onProgress) {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          options.onProgress(percentCompleted);
        }
      }
    };
    
    // Make the API call
    const response = await api.post('/api/analyze-body-motion', formData, config);
    return response;
  },
  
  /**
   * Get analysis summary
   * @returns {Promise} - Promise with summary data
   */
  getSummary: async () => {
    const response = await api.get('/api/summary');
    return response;
  }
};