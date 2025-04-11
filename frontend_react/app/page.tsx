'use client';

import { useState, useEffect } from 'react';
import Image from "next/image";
import Navbar from './components/Navbar';
import { useAuth } from './context/AuthContext';
import { fetchWithAuth } from './utils/api';

export default function Home() {
  const { isLoggedIn, token } = useAuth();
  const [currentStep, setCurrentStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [step1Response, setStep1Response] = useState<string | null>(null);
  const [step2Response, setStep2Response] = useState<string | null>(null);
  const [extractedText, setExtractedText] = useState<string | null>(null);
  const [pdfPath, setPdfPath] = useState<string | null>(null);
  const [appFolderPath, setAppFolderPath] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  
  // States for collapsible sections
  const [isStep1Expanded, setIsStep1Expanded] = useState(false);
  const [isExtractedTextExpanded, setIsExtractedTextExpanded] = useState(false);
  const [isStep2Expanded, setIsStep2Expanded] = useState(false);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsLoading(true);
    setCurrentStep(1);
    setStep1Response(null);
    setStep2Response(null);
    setExtractedText(null);
    setPdfPath(null);
    setAppFolderPath(null);
    setFileName(null);

    try {
      // Step 1: Upload the file with authentication
      const formData = new FormData();
      formData.append('file', file);

      // Add auth token to the request
      const headers: HeadersInit = {};
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const uploadResponse = await fetch('http://localhost:8000/upload/resume-text', {
        method: 'POST',
        headers,
        body: formData,
      });

      if (!uploadResponse.ok) {
        throw new Error('Upload failed');
      }

      const result = await uploadResponse.json();
      console.log('Step 1 Response:', result);
      setStep1Response(JSON.stringify(result, null, 2));
      
      if (result.extracted_text) {
        setExtractedText(result.extracted_text);
        setCurrentStep(2);
        
        // Step 2: Generate PDF resume - Direct GET call to FastAPI endpoint with auth
        const url = new URL('http://localhost:8000/applications/resume/pdf');
        url.searchParams.append('job_description', result.extracted_text);
        
        const authHeaders: HeadersInit = {
          'accept': 'application/json'
        };
        
        if (token) {
          authHeaders['Authorization'] = `Bearer ${token}`;
        }
        
        const step2Response = await fetch(url.toString(), {
          method: 'GET',
          headers: authHeaders
        });

        if (!step2Response.ok) {
          throw new Error('Step 2 failed');
        }

        const step2Result = await step2Response.json();
        console.log('Step 2 Response:', step2Result);
        setStep2Response(JSON.stringify(step2Result, null, 2));
        
        // Extract PDF path if available
        if (step2Result.access && step2Result.access.local_path) {
          const fullPath = step2Result.access.local_path;
          setPdfPath(fullPath);
          
          // Extract the Applications folder path and filename
          const pathParts = fullPath.split('\\');
          const appIndex = pathParts.findIndex((part: string) => part === 'Applications');
          
          if (appIndex !== -1) {
            const relativePath = pathParts.slice(appIndex).join('/');
            setAppFolderPath(relativePath);
            setFileName(pathParts[pathParts.length - 1]);
          }
        }
      }
    } catch (error) {
      console.error('Error:', error);
      setStep2Response('An error occurred while processing your resume');
    } finally {
      setIsLoading(false);
    }
  };

  const getDownloadUrl = () => {
    if (!appFolderPath || !fileName) return '';
    
    // Construct the download URL based on the server's file serving configuration
    return `http://localhost:8000/download/${appFolderPath}`;
  };

  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      
      <div className="flex-1 p-8">
        <div className="max-w-2xl mx-auto">
          <h1 className="text-3xl font-bold mb-8">Resume Upload</h1>
          
          {!isLoggedIn ? (
            <div className="bg-yellow-100 p-4 rounded-md mb-8">
              <p className="text-yellow-800">Please log in to upload and process your resume.</p>
            </div>
          ) : (
            <>
              <div className="mb-8">
                <label className="block mb-4">
                  <span className="text-gray-700">Upload your resume (PDF)</span>
                  <input
                    type="file"
                    accept=".pdf"
                    onChange={handleFileUpload}
                    className="mt-2 block w-full text-sm text-gray-500
                      file:mr-4 file:py-2 file:px-4
                      file:rounded-full file:border-0
                      file:text-sm file:font-semibold
                      file:bg-blue-50 file:text-blue-700
                      hover:file:bg-blue-100"
                    disabled={isLoading || !isLoggedIn}
                  />
                </label>
              </div>

              <div className="space-y-4">
                <div className={`flex items-center ${currentStep >= 1 ? 'text-blue-600' : 'text-gray-400'}`}>
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center ${currentStep >= 1 ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}>
                    1
                  </div>
                  <span className="ml-2">Uploading and Extracting Text</span>
                  {currentStep === 1 && isLoading && (
                    <span className="ml-2 text-sm">(In Progress...)</span>
                  )}
                </div>

                <div className={`flex items-center ${currentStep >= 2 ? 'text-blue-600' : 'text-gray-400'}`}>
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center ${currentStep >= 2 ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}>
                    2
                  </div>
                  <span className="ml-2">Generating PDF Resume</span>
                  {currentStep === 2 && isLoading && (
                    <span className="ml-2 text-sm">(In Progress...)</span>
                  )}
                </div>
              </div>

              {step1Response && (
                <div className="mt-8 p-4 bg-gray-100 rounded-lg">
                  <div 
                    className="flex justify-between items-center cursor-pointer"
                    onClick={() => setIsStep1Expanded(!isStep1Expanded)}
                  >
                    <h2 className="text-xl font-semibold">Step 1 Response:</h2>
                    <button className="text-blue-600">
                      {isStep1Expanded ? '▲ Collapse' : '▼ Expand'}
                    </button>
                  </div>
                  {isStep1Expanded && (
                    <pre className="whitespace-pre-wrap max-h-60 overflow-y-auto mt-2">{step1Response}</pre>
                  )}
                </div>
              )}

              {extractedText && (
                <div className="mt-8 p-4 bg-gray-100 rounded-lg">
                  <div 
                    className="flex justify-between items-center cursor-pointer"
                    onClick={() => setIsExtractedTextExpanded(!isExtractedTextExpanded)}
                  >
                    <h2 className="text-xl font-semibold">Extracted Text:</h2>
                    <button className="text-blue-600">
                      {isExtractedTextExpanded ? '▲ Collapse' : '▼ Expand'}
                    </button>
                  </div>
                  {isExtractedTextExpanded && (
                    <pre className="whitespace-pre-wrap max-h-60 overflow-y-auto mt-2">{extractedText}</pre>
                  )}
                </div>
              )}

              {step2Response && (
                <div className="mt-8 p-4 bg-gray-100 rounded-lg">
                  <div 
                    className="flex justify-between items-center cursor-pointer"
                    onClick={() => setIsStep2Expanded(!isStep2Expanded)}
                  >
                    <h2 className="text-xl font-semibold">Step 2 Response:</h2>
                    <button className="text-blue-600">
                      {isStep2Expanded ? '▲ Collapse' : '▼ Expand'}
                    </button>
                  </div>
                  {isStep2Expanded && (
                    <pre className="whitespace-pre-wrap max-h-60 overflow-y-auto mt-2">{step2Response}</pre>
                  )}
                </div>
              )}

              {pdfPath && (
                <div className="mt-8 flex justify-center">
                  <a 
                    href={`http://localhost:8000/files/applications/${appFolderPath}`}
                    download={fileName}
                    className="bg-green-600 text-white py-3 px-6 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 flex items-center"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                    Download PDF Resume
                  </a>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
