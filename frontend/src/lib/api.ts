import { getAccessToken } from './utils';

// Get the backend URL from environment or use fallback
const getBackendUrl = () => {
  // For server-side rendering, always use the backend URL directly
  if (typeof window === 'undefined') {
    return process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  }
  
  // For client-side, use environment variable if available
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  
  // Fallback for client-side when no env var is set
  if (process.env.NODE_ENV === 'development') {
    return 'http://localhost:8000';
  }
  
  // In production, try to infer backend URL from current domain
  const currentOrigin = window.location.origin;
  // Try common backend URL patterns
  const possibleUrls = [
    currentOrigin.replace(/:\d+$/, ':8000'), // Same domain, port 8000
    currentOrigin.replace('www.', 'api.'), // api subdomain
    `${currentOrigin}/api`, // /api path
  ];
  
  return possibleUrls[0]; // Use the first one as default
};

// Default timeout for API calls (in milliseconds)
const DEFAULT_TIMEOUT = 60000; // 1 minute for most operations
const RESUME_GENERATION_TIMEOUT = 120000; // 2 minutes for AI resume generation

// Get appropriate timeout based on endpoint
const getTimeoutForEndpoint = (endpoint: string): number => {
  // Resume generation operations need longer timeout due to AI processing
  if (endpoint.includes('resume/pdf') || 
      endpoint.includes('resume/anonymous') || 
      endpoint.includes('cover-letter') ||
      endpoint.includes('resume/edit') ||
      endpoint.includes('cover-letter/edit')) {
    return RESUME_GENERATION_TIMEOUT;
  }
  return DEFAULT_TIMEOUT;
};

// Generic API call function with fallback mechanism
async function apiCall(
  endpoint: string,
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' = 'GET',
  data?: any,
  isFormData = false
) {
  const token = await getAccessToken();
  
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
  
  // Prepare the request body
  if (data) {
    if (method === 'GET') {
      // For GET requests, append data as query parameters
      const params = new URLSearchParams();
      Object.entries(data).forEach(([key, value]) => {
        params.append(key, String(value));
      });
      endpoint = `${endpoint}?${params.toString()}`;
    } else if (isFormData) {
      options.body = data;
    } else {
      options.body = JSON.stringify(data);
    }
  }
  
  // Use AbortController for timeout handling with dynamic timeout
  const controller = new AbortController();
  const timeoutMs = getTimeoutForEndpoint(endpoint);
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
  options.signal = controller.signal;
  
  // Strategy: Try relative URL first (for Next.js rewrites), then try direct backend URL
  const urlsToTry = [];
  
  if (typeof window !== 'undefined' && process.env.NODE_ENV === 'production') {
    // In production client-side, try relative URL first (for rewrites)
    urlsToTry.push(`/${endpoint}`);
  }
  
  // Always add the direct backend URL as fallback
  const backendUrl = getBackendUrl();
  urlsToTry.push(`${backendUrl}/${endpoint}`);
  
  let lastError: Error | null = null;
  
  for (let i = 0; i < urlsToTry.length; i++) {
    const url = urlsToTry[i];
    
    try {
      if (process.env.NODE_ENV === 'development') {
        console.log(`Attempting API call ${i + 1}/${urlsToTry.length}:`, {
          method,
          url,
          endpoint,
          hasData: !!data,
          isFormData
        });
      }
      
      const response = await fetch(url, options);
      
      // Clear the timeout since the request completed
      clearTimeout(timeoutId);
      
      // Handle non-2xx responses
      if (!response.ok) {
        const errorText = await response.text();
        let errorMessage = `Request failed with status ${response.status}`;
        
        try {
          const errorData = JSON.parse(errorText);
          errorMessage = errorData.detail || errorMessage;
        } catch (e) {
          if (errorText) errorMessage = errorText;
        }
        
        // If this is a 404 and we have more URLs to try, continue to next URL
        if (response.status === 404 && i < urlsToTry.length - 1) {
          console.warn(`URL ${url} returned 404, trying next URL...`);
          continue;
        }
        
        throw new Error(errorMessage);
      }
      
      // Success! Process the response
      if (response.status === 204) {
        return null;
      }
      
      const contentType = response.headers.get('content-type');
      
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
            const rfc5987Match = contentDisposition.match(/filename\*=utf-8''([^;]+)/i);
            if (rfc5987Match) {
              filename = decodeURIComponent(rfc5987Match[1]);
            } else {
              const standardMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
              if (standardMatch) {
                filename = standardMatch[1].replace(/['"]/g, '');
              }
            }
          }
          
          return { blob, filename };
        }
        
        // For .tex files, also extract filename from Content-Disposition header
        if (contentType.includes('application/x-tex')) {
          const contentDisposition = response.headers.get('content-disposition');
          
          let filename = null;
          
          if (contentDisposition) {
            const rfc5987Match = contentDisposition.match(/filename\*=utf-8''([^;]+)/i);
            if (rfc5987Match) {
              filename = decodeURIComponent(rfc5987Match[1]);
            } else {
              const standardMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
              if (standardMatch) {
                filename = standardMatch[1].replace(/['"]/g, '');
              }
            }
          }
          
          return { blob, filename };
        }
        
        return blob;
      }
      
      return await response.text();
      
    } catch (error: any) {
      lastError = error;
      
      // Handle timeout errors
      if (error.name === 'AbortError') {
        clearTimeout(timeoutId);
        const timeoutSeconds = Math.floor(timeoutMs / 1000);
        throw new Error(`The request took too long to complete (over ${timeoutSeconds} seconds). This typically happens when generating complex resumes. Please try again or use a shorter job description.`);
      }
      
      // If this is the last URL to try, throw the error
      if (i === urlsToTry.length - 1) {
        clearTimeout(timeoutId);
        console.error('All API call attempts failed:', error);
        throw error;
      }
      
      // Otherwise, log the error and try the next URL
      console.warn(`API call to ${url} failed, trying next URL:`, error.message);
    }
  }
  
  // This should never be reached, but just in case
  clearTimeout(timeoutId);
  throw lastError || new Error('All API call attempts failed');
}

// Auth endpoints. Login/signup are handled by Supabase Auth on the client
// (see components/auth/auth-modal.tsx); the backend only exposes the profile.
export const auth = {
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

// Simple application session management
const applicationSessionManager = {
  // Extract company name for display purposes (simple version)
  extractCompanyName: (jobDescription: string): string => {
    const text = jobDescription.toLowerCase();
    
    // Look for simple patterns like "Company Name | Salary" or "Company Name - Job Title"  
    const patterns = [
      /^([^|\n]+?)\s*\|/,  // "Company | Rest"
      /^([^-\n]+?)\s*-/,   // "Company - Rest"
    ];
    
    for (const pattern of patterns) {
      const match = text.match(pattern);
      if (match && match[1]) {
        return match[1].trim().replace(/\b(inc|corp|llc|ltd|company|solutions|technologies|systems)\b/gi, '').trim();
      }
    }
    
    // Fallback: take first line up to 50 chars
    const firstLine = jobDescription.split('\n')[0];
    return firstLine.length > 50 ? firstLine.substring(0, 50).replace(/\W+$/, '') : firstLine;
  }
};

// Application endpoints
export const applications = {
  generateResume: (jobDescription: string, isNewApplication?: boolean) => {
    const params: any = { job_description: jobDescription };
    if (isNewApplication !== undefined) {
      params.is_new_application = isNewApplication;
    }
    
    return apiCall('applications/resume/pdf', 'GET', params, false);
  },
  
  getResumeTeX: () => 
    apiCall('applications/resume/tex', 'GET', undefined, false),
  
  getResumeTeXContent: () => 
    apiCall('applications/resume/tex/content', 'GET'),
  
  getLatestResumeJson: () =>
    apiCall('applications/resume/json', 'GET'),
  
  generateCoverLetter: (jobDescription: string, isNewApplication?: boolean) => {
    const params: any = { job_description: jobDescription };
    if (isNewApplication !== undefined) {
      params.is_new_application = isNewApplication;
    }
    
    return apiCall('applications/cover-letter/plain', 'GET', params, false);
  },
  
  getCoverLetterPDF: () => 
    apiCall('applications/cover-letter/pdf', 'GET'),
  
  getCoverLetterText: () => 
    apiCall('applications/cover-letter/text', 'GET'),
  
  answerQuestion: (jobDescription: string, question: string, isNewApplication?: boolean) => {
    const params: any = { 
      job_description: jobDescription, 
      question 
    };
    if (isNewApplication !== undefined) {
      params.is_new_application = isNewApplication;
    }
    
    return apiCall('applications/questions/answer', 'GET', params, false);
  },
    
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
  generateAnonymousResume: (resumeText: string | null, jobDescription: string, resumeFile?: File) => {
    const formData = new FormData();
    formData.append('job_description', jobDescription);
    
    if (resumeFile) {
      formData.append('resume_file', resumeFile);
    } else if (resumeText) {
      formData.append('resume_text', resumeText);
    }
    
    return apiCall('applications/resume/anonymous', 'POST', formData, true);
  },

  getAnonymousResume: (sessionId: string) =>
    apiCall(`applications/resume/anonymous/${sessionId}`, 'GET', undefined, false),
};

// Billing endpoints
export const billing = {
  createCustomerPortalSession: (returnUrl?: string) => 
    apiCall('billing/manage-subscription', 'POST', returnUrl ? { return_url: returnUrl } : {}),
};

export { applicationSessionManager };

export default {
  auth,
  resume,
  applications,
  preferences,
  billing
}; 