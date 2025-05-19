import { getAccessToken } from './utils';

// Base API URL - adjust as needed for your environment
let API_BASE_URL = typeof window !== 'undefined' 
  ? window.location.origin.replace(/:\d+$/, ':8000')  // In production, use same origin but port 8000
  : 'http://localhost:8000';  // Fallback for SSR

// For development fallback
if (process.env.NODE_ENV === 'development') {
  API_BASE_URL = 'http://localhost:8000';
}

// Default timeout for API calls (in milliseconds)
const DEFAULT_TIMEOUT = 60000; // 1 minute for all operations

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
    
    // Use AbortController for timeout handling
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), DEFAULT_TIMEOUT);
    
    // Add signal to options
    options.signal = controller.signal;
    
    const response = await fetch(url, options);
    
    // Clear the timeout since the request completed
    clearTimeout(timeoutId);
    
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
    console.log(`Response content type: ${contentType}`);
    
    if (contentType && contentType.includes('application/json')) {
      return await response.json();
    }
    
    // Handle binary responses (like PDFs or .tex files)
    if (contentType && (
      contentType.includes('application/pdf') || 
      contentType.includes('application/x-tex') ||
      contentType.includes('application/octet-stream')
    )) {
      return await response.blob();
    }
    
    // Default to text
    return await response.text();
  } catch (error: any) {
    console.error('API call failed:', error);
    
    // Handle timeout errors with more meaningful messages
    if (error.name === 'AbortError') {
      throw new Error('The request took too long to complete. This typically happens when generating complex resumes. Please try again or use a shorter job description.');
    }
    
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
  
  signup: (username: string, password: string, email: string, initialResume: string, resumeFile?: string) => 
    apiCall('users/signup', 'POST', { 
      username, 
      password, 
      email, 
      initial_resume: initialResume || null,
      resume_file: resumeFile || null
    }),
    
  getProfile: () => apiCall('users/me'),
};

// Resume endpoints
export const resume = {
  getResume: () => apiCall('users/me/resume'),
  
  updateResume: (resumeContent: string) => 
    apiCall('users/me/resume', 'PUT', { resume_content: resumeContent }),
  
  getResumePdf: () => apiCall('users/me/resume/pdf'),
  
  uploadResumePdf: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiCall('users/me/resume/upload', 'POST', formData, true);
  }
};

// Application endpoints
export const applications = {
  generateResume: (jobDescription: string) => 
    apiCall('applications/resume/pdf', 'GET', { job_description: jobDescription }, false),
  
  getResumeTeX: () => 
    apiCall('applications/resume/tex', 'GET', undefined, false),
  
  getResumeTeXContent: () => 
    apiCall('applications/resume/tex/content', 'GET'),
  
  getLatestResumeJson: () =>
    apiCall('applications/resume/json', 'GET'),
  
  generateCoverLetter: (jobDescription: string) => 
    apiCall('applications/cover-letter/plain', 'GET', { job_description: jobDescription }, false),
  
  getCoverLetterPDF: () => 
    apiCall('applications/cover-letter/pdf', 'GET'),
  
  getCoverLetterText: () => 
    apiCall('applications/cover-letter/text', 'GET'),
  
  answerQuestion: (jobDescription: string, question: string) => 
    apiCall('applications/questions/answer', 'GET', { 
      job_description: jobDescription, 
      question 
    }, false),
    
  editAnswerWithInstructions: (editInstruction: string, originalAnswer: string, question: string, jobDescription: string) => 
    apiCall('applications/questions/answer/edit', 'GET', { 
      edit_instruction: editInstruction,
      original_answer: originalAnswer,
      question,
      job_description: jobDescription
    }, false),
    
  improveResume: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiCall('applications/resume/improve', 'POST', formData, true);
  },
  
  editResumeWithInstructions: (editInstruction: string, jobDescription: string) => 
    apiCall('applications/resume/edit', 'GET', { 
      edit_instruction: editInstruction,
      job_description: jobDescription 
    }, false),
    
  editCoverLetterWithInstructions: (editInstruction: string, jobDescription: string) => 
    apiCall('applications/cover-letter/edit', 'GET', { 
      edit_instruction: editInstruction, 
      job_description: jobDescription 
    }, false)
};

export default {
  auth,
  resume,
  applications
}; 