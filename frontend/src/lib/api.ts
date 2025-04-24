import { getAccessToken } from './utils';

// Base API URL - adjust as needed for your environment
const API_BASE_URL = 'http://localhost:8000';

// Generic API call function
async function apiCall(
  endpoint: string,
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' = 'GET',
  data?: any,
  isFormData = false
) {
  let url = `${API_BASE_URL}/${endpoint}`;
  const token = getAccessToken();
  
  const headers: Record<string, string> = {};
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  if (!isFormData && method !== 'GET') {
    headers['Content-Type'] = 'application/json';
  }
  
  const options: RequestInit = {
    method,
    headers,
  };
  
  if (data) {
    if (method === 'GET') {
      // For GET requests, append data as query parameters
      const params = new URLSearchParams();
      Object.entries(data).forEach(([key, value]) => {
        params.append(key, String(value));
      });
      url = `${url}?${params.toString()}`;
    } else if (isFormData) {
      // For FormData, don't manually set Content-Type - browser will set it with boundary
      options.body = data;
    } else {
      // For JSON data
      options.body = JSON.stringify(data);
    }
  }
  
  try {
    console.log(`Calling ${method} ${url}`, options);
    const response = await fetch(url, options);
    
    // Handle non-2xx responses
    if (!response.ok) {
      const errorText = await response.text();
      let errorMessage = `Request failed with status ${response.status}`;
      
      try {
        // Try to parse as JSON
        const errorData = JSON.parse(errorText);
        errorMessage = errorData.detail || errorMessage;
      } catch (e) {
        // If not JSON, use the text
        if (errorText) errorMessage = errorText;
      }
      
      throw new Error(errorMessage);
    }
    
    // For 204 No Content
    if (response.status === 204) {
      return null;
    }
    
    // Try to parse as JSON
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return await response.json();
    }
    
    // Handle binary responses (like PDFs)
    if (contentType && contentType.includes('application/pdf')) {
      return await response.blob();
    }
    
    // Default to text
    return await response.text();
  } catch (error) {
    console.error('API call failed:', error);
    throw error;
  }
}

// Auth endpoints
export const auth = {
  login: (username: string, password: string) => {
    // Create URLSearchParams for form data submission
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    
    return apiCall('login', 'POST', formData, true);
  },
  
  signup: (username: string, password: string, email: string, initialResume: string) => 
    apiCall('users/signup', 'POST', { 
      username, 
      password, 
      email, 
      initial_resume: initialResume || 'Empty' 
    }),
    
  getProfile: () => apiCall('users/me'),
};

// Resume endpoints
export const resume = {
  getResume: () => apiCall('users/me/resume'),
  
  updateResume: (resumeContent: string) => 
    apiCall('users/me/resume', 'PUT', { resume_content: resumeContent }),
  
  getTailoringOptions: () => apiCall('users/me/tailoring-options'),
  
  updateTailoringOptions: (aiModel: string, resumeTemplate: string) => 
    apiCall('users/me/tailoring-options', 'PUT', { ai_model: aiModel, resume_template: resumeTemplate }),
};

// Application endpoints
export const applications = {
  generateResume: (jobDescription: string) => 
    apiCall('applications/resume/pdf', 'GET', { job_description: jobDescription }),
  
  generateCoverLetter: (jobDescription: string) => 
    apiCall('applications/cover-letter/plain', 'GET', { job_description: jobDescription }),
  
  answerQuestion: (jobDescription: string, question: string) => 
    apiCall('applications/questions/answer', 'GET', { 
      job_description: jobDescription, 
      question 
    }),
    
  improveResume: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiCall('applications/resume/improve', 'POST', formData, true);
  }
};

export default {
  auth,
  resume,
  applications
}; 