import axios from 'axios';

// Default configuration
const baseURL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
const apiURL = `${baseURL}/api/v1`;
const documentsURL = `${apiURL}/documents`;

console.log('Using API URL:', apiURL);

// Create axios instance
const api = axios.create({
  baseURL,
  timeout: 30000, // 30 second timeout
  headers: {
    'Accept': 'application/json',
  }
});

// Add request interceptor for debugging
api.interceptors.request.use(
  config => {
    // For multipart/form-data, let the browser set the content type with boundary
    if (config.data instanceof FormData) {
      config.headers['Content-Type'] = 'multipart/form-data';
    } else {
      // For regular JSON requests
      config.headers['Content-Type'] = 'application/json';
    }
    
    // Log outgoing requests in development
    if (process.env.NODE_ENV !== 'production') {
      console.log('API Request:', {
        method: config.method?.toUpperCase(),
        url: config.url,
        headers: config.headers,
        data: config.data instanceof FormData ? '[FormData]' : config.data
      });
    }
    
    return config;
  },
  error => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for logging
api.interceptors.response.use(
  response => {
    // Log successful responses in development
    if (process.env.NODE_ENV !== 'production') {
      console.log('API Response:', {
        status: response.status,
        statusText: response.statusText,
        data: response.data
      });
    }
    return response;
  },
  error => {
    // Log errors in all environments
    if (axios.isAxiosError(error)) {
      const errorInfo = {
        message: error.message,
        code: error.code || 'UNKNOWN',
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        url: error.config?.url
      };
      console.error('API Response Error:', errorInfo);
    } else {
      console.error('Non-Axios Error:', error);
    }
    return Promise.reject(error);
  }
);

// API client service
export const apiService = {
  /**
   * Upload a file to the backend
   */
  async uploadFile(file: File) {
    try {
      console.log(`Uploading file to ${documentsURL}/upload`);
      
      const formData = new FormData();
      formData.append('file', file);

      const response = await api.post(`${documentsURL}/upload`, formData);
      console.log('Upload response:', response.data);
      
      return {
        success: true,
        ...response.data,
      };
    } catch (error: any) {
      console.error('Error uploading file:', error);
      
      // Provide more detailed error information
      let errorMessage = 'Failed to upload file';
      
      if (axios.isAxiosError(error)) {
        if (error.response) {
          // The request was made and the server responded with a status code
          // that falls out of the range of 2xx
          errorMessage = `Server error: ${error.response.status} - ${error.response.data?.detail || error.response.statusText}`;
          console.error('Error response data:', error.response.data);
        } else if (error.request) {
          // The request was made but no response was received
          errorMessage = 'Network Error: No response received from the server. Please check if the backend is running.';
        } else {
          // Something happened in setting up the request
          errorMessage = `Request setup error: ${error.message}`;
        }
      } else if (error instanceof Error) {
        errorMessage = error.message;
      }
      
      return {
        success: false,
        error: errorMessage,
      };
    }
  },

  /**
   * List all documents
   */
  async listFiles() {
    try {
      const response = await api.get(`${documentsURL}/list`);
      return {
        success: true,
        files: response.data,
      };
    } catch (error: any) {
      console.error('Error listing files:', error);
      
      let errorMessage = 'Failed to list files';
      
      if (axios.isAxiosError(error)) {
        if (error.response) {
          errorMessage = `Server error: ${error.response.status} - ${error.response.data?.detail || error.response.statusText}`;
        } else if (error.request) {
          errorMessage = 'Network Error: No response received from the server';
        } else {
          errorMessage = `Request setup error: ${error.message}`;
        }
      } else if (error instanceof Error) {
        errorMessage = error.message;
      }
      
      return {
        success: false,
        error: errorMessage,
      };
    }
  },

  /**
   * Delete a document
   */
  async deleteFile(fileId: string) {
    try {
      const response = await api.delete(`${documentsURL}/${fileId}`);
      return {
        success: true,
        message: response.data.message || 'File deleted successfully',
      };
    } catch (error: any) {
      console.error('Error deleting file:', error);
      
      let errorMessage = 'Failed to delete file';
      
      if (axios.isAxiosError(error)) {
        if (error.response) {
          errorMessage = `Server error: ${error.response.status} - ${error.response.data?.detail || error.response.statusText}`;
        } else if (error.request) {
          errorMessage = 'Network Error: No response received from the server';
        } else {
          errorMessage = `Request setup error: ${error.message}`;
        }
      } else if (error instanceof Error) {
        errorMessage = error.message;
      }
      
      return {
        success: false,
        error: errorMessage,
      };
    }
  },

  /**
   * Check if the backend is available
   */
  async checkBackendStatus() {
    try {
      console.log(`Checking backend status at: ${apiURL}/documents/list`);
      
      // Use a direct fetch with no timeout for more reliable connection
      const response = await axios.get(`${apiURL}/documents/list`, { 
        timeout: 10000, // Increase timeout to 10 seconds
        // Don't throw on 4xx errors, we still want to know the backend is running
        validateStatus: (status) => status < 500
      });
      
      console.log('Backend status check response:', {
        status: response.status,
        statusText: response.statusText
      });
      
      // Any status under 500 means the backend is running
      return {
        success: true,
        status: response.status,
        message: response.status === 200 
          ? 'Backend is available' 
          : `Backend is running (status: ${response.status})`
      };
    } catch (error) {
      console.error('Backend availability check failed:', error);
      
      let errorMessage = 'Backend availability check failed';
      let errorDetails = '';
      
      if (axios.isAxiosError(error)) {
        if (error.response) {
          // The request was made and the server responded with a status >= 500
          errorMessage = `Backend error: ${error.response.status} - ${error.response.statusText}`;
          errorDetails = JSON.stringify(error.response.data || {});
        } else if (error.request) {
          // The request was made but no response was received
          if (error.code === 'ECONNREFUSED') {
            errorMessage = 'Cannot connect to the backend server. Please ensure it is running.';
          } else if (error.code === 'ETIMEDOUT' || error.code === 'ECONNABORTED') {
            errorMessage = 'Connection to backend timed out. The server might be overloaded or unreachable.';
          } else {
            errorMessage = `Network error: ${error.code || 'No response from server'}`;
          }
        } else {
          // Something happened in setting up the request
          errorMessage = `Request setup error: ${error.message}`;
        }
        
        console.error('Detailed error:', {
          message: errorMessage,
          code: error.code,
          details: errorDetails
        });
      }
      
      return {
        success: false,
        error: errorMessage
      };
    }
  },

  /**
   * Get detailed information about the backend configuration and connection
   */
  async getBackendInfo() {
    interface ConnectionTest {
      status: 'pending' | 'completed' | 'failed';
      error: string | null;
      details: any;
    }
    
    interface BackendInfo {
      baseURL: string;
      apiURL: string;
      documentsURL: string;
      nodeEnv: string;
      backendUrl: string;
      browser: boolean;
      connectionTest: ConnectionTest;
    }
    
    const info: BackendInfo = {
      baseURL,
      apiURL,
      documentsURL,
      nodeEnv: process.env.NODE_ENV || 'unknown',
      backendUrl: process.env.NEXT_PUBLIC_BACKEND_URL || 'not set (using default)',
      browser: typeof window !== 'undefined' ? true : false,
      connectionTest: {
        status: 'pending',
        error: null,
        details: null
      }
    };
    
    try {
      // Try a simple ping request to the base URL
      const pingResponse = await axios.get(`${baseURL}/api/v1/documents/list`, { 
        timeout: 5000,
        validateStatus: () => true // Accept any status code
      });
      
      info.connectionTest = {
        status: 'completed',
        error: null,
        details: {
          statusCode: pingResponse.status,
          statusText: pingResponse.statusText,
          headers: pingResponse.headers,
          data: pingResponse.data
        }
      };
      
      return {
        success: true,
        info
      };
    } catch (error) {
      let errorDetails: any;
      
      if (axios.isAxiosError(error)) {
        errorDetails = {
          message: error.message,
          code: error.code,
          config: {
            url: error.config?.url,
            method: error.config?.method,
            timeout: error.config?.timeout
          },
          response: error.response ? {
            status: error.response.status,
            statusText: error.response.statusText,
            data: error.response.data
          } : null
        };
      } else if (error instanceof Error) {
        errorDetails = {
          name: error.name,
          message: error.message,
          stack: error.stack
        };
      } else {
        errorDetails = String(error);
      }
      
      info.connectionTest = {
        status: 'failed',
        error: error instanceof Error ? error.message : String(error),
        details: errorDetails
      };
      
      return {
        success: false,
        info
      };
    }
  }
}; 