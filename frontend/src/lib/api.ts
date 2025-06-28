import { getAccessToken } from './utils';

// Base API URL - Use relative URLs in production to leverage Next.js rewrites
let API_BASE_URL: string;

if (typeof window !== 'undefined') {
  // Client-side: use relative URLs to leverage Next.js rewrites in production
  API_BASE_URL = process.env.NODE_ENV === 'development' 
    ? 'http://localhost:8000'  // Direct backend call in development
    : '';  // Relative URLs in production (Next.js will proxy)
} else {
  // Server-side: always use the backend URL directly
  API_BASE_URL = process.env.API_URL || 'http://localhost:8000';
}

// Debug logging (only in development)
if (process.env.NODE_ENV === 'development') {
  console.log('API Configuration:', {
    NODE_ENV: process.env.NODE_ENV,
    isClient: typeof window !== 'undefined',
    API_BASE_URL,
    API_URL_ENV: process.env.API_URL
  });
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
    // Debug logging (only in development)
    if (process.env.NODE_ENV === 'development') {
      console.log(`Making API call:`, {
        method,
        url,
        API_BASE_URL,
        endpoint,
        hasData: !!data,
        isFormData
      });
    }
    
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
      const blob = await response.blob();
      
      // For PDF responses, also extract filename from Content-Disposition header
      if (contentType.includes('application/pdf')) {
        const contentDisposition = response.headers.get('content-disposition');
        
        let filename = null;
        
        if (contentDisposition) {
          // Try RFC 5987 format first (filename*=utf-8''name.pdf)
          const rfc5987Match = contentDisposition.match(/filename\*=utf-8''([^;]+)/i);
          if (rfc5987Match) {
            // Decode the URL-encoded filename
            filename = decodeURIComponent(rfc5987Match[1]);
          } else {
            // Fallback to standard format (filename="name.pdf" or filename=name.pdf)
            const standardMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
            if (standardMatch) {
              filename = standardMatch[1].replace(/['"]/g, '');
            }
          }
        }
        
        // Return an object with both blob and filename for PDFs
        return { blob, filename };
      }
      
      // For .tex files, also extract filename from Content-Disposition header
      if (contentType.includes('application/x-tex')) {
        const contentDisposition = response.headers.get('content-disposition');
        
        let filename = null;
        
        if (contentDisposition) {
          // Try RFC 5987 format first (filename*=utf-8''name.tex)
          const rfc5987Match = contentDisposition.match(/filename\*=utf-8''([^;]+)/i);
          if (rfc5987Match) {
            // Decode the URL-encoded filename
            filename = decodeURIComponent(rfc5987Match[1]);
          } else {
            // Fallback to standard format (filename="name.tex" or filename=name.tex)
            const standardMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
            if (standardMatch) {
              filename = standardMatch[1].replace(/['"]/g, '');
            }
          }
        }
        
        // Return an object with both blob and filename for .tex files
        return { blob, filename };
      }
      
      // For non-PDF binary files, return just the blob
      return blob;
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

// User preferences endpoints
export const preferences = {
  getUserPreferences: () => apiCall('users/me/preferences'),
  
  addUserPreference: (preference: string) => 
    apiCall('users/me/preferences', 'POST', { preference }),
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
    }, false),
    
  // Anonymous resume generation (no authentication required)
  generateAnonymousResume: (resumeText: string, jobDescription: string) =>
    apiCall('applications/resume/anonymous', 'POST', { 
      resume_text: resumeText, 
      job_description: jobDescription 
    }, false),

  getAnonymousResume: (sessionId: string) =>
    apiCall(`applications/resume/anonymous/${sessionId}`, 'GET', undefined, false),
};

export default {
  auth,
  resume,
  applications,
  preferences
}; 