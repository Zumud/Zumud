// Utility for making authenticated API requests

export async function fetchWithAuth(url: string, options: RequestInit = {}) {
  // Get the auth token from localStorage
  const token = localStorage.getItem('authToken');
  
  // Prepare headers with authorization if token exists
  const headers = {
    ...options.headers,
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
  
  // Make the request with the authorization header
  return fetch(url, {
    ...options,
    headers,
  });
}

// Function to handle file uploads with authentication
export async function uploadFileWithAuth(url: string, file: File, additionalFormData: Record<string, string> = {}) {
  const token = localStorage.getItem('authToken');
  const formData = new FormData();
  
  // Add the file to form data
  formData.append('file', file);
  
  // Add any additional form data fields
  Object.entries(additionalFormData).forEach(([key, value]) => {
    formData.append(key, value);
  });
  
  return fetch(url, {
    method: 'POST',
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
    body: formData,
  });
} 