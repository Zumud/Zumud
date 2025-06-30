"use client"

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { applications } from '@/lib/api'

export default function DebugResumePage() {
  const [testResults, setTestResults] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(false)

  const runTests = async () => {
    setIsLoading(true)
    const results = []

    // Test 1: Check API configuration
    results.push({
      test: 'API Configuration',
      result: {
        NODE_ENV: process.env.NODE_ENV,
        NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
        currentOrigin: typeof window !== 'undefined' ? window.location.origin : 'SSR'
      }
    })

    // Test 2: Try to fetch a known session
    try {
      const sessionId = '492c02df-8ad3-4d96-97d7-059ac2ceeffc'
      const resumeData = await applications.getAnonymousResume(sessionId)
      results.push({
        test: 'API Call Test',
        result: {
          success: true,
          sessionId: resumeData.session_id,
          hasData: !!resumeData.pdf_base64,
          company: resumeData.company_name
        }
      })
    } catch (error: any) {
      results.push({
        test: 'API Call Test',
        result: {
          success: false,
          error: error.message
        }
      })
    }

    // Test 3: Check current URL structure
    results.push({
      test: 'URL Structure',
      result: {
        currentPath: typeof window !== 'undefined' ? window.location.pathname : 'SSR',
        currentHost: typeof window !== 'undefined' ? window.location.host : 'SSR',
        expectedResumeUrl: `/resume/492c02df-8ad3-4d96-97d7-059ac2ceeffc`,
        expectedApiUrl: `/applications/resume/anonymous/492c02df-8ad3-4d96-97d7-059ac2ceeffc`
      }
    })

    setTestResults(results)
    setIsLoading(false)
  }

  const testResumeRoute = () => {
    const sessionId = '492c02df-8ad3-4d96-97d7-059ac2ceeffc'
    window.open(`/resume/${sessionId}`, '_blank')
  }

  const testApiRoute = () => {
    const sessionId = '492c02df-8ad3-4d96-97d7-059ac2ceeffc'
    window.open(`/applications/resume/anonymous/${sessionId}`, '_blank')
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Resume Route Debug Tool</h1>
        
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Quick Tests</h2>
          <div className="space-y-4">
            <Button onClick={runTests} disabled={isLoading} className="mr-4">
              {isLoading ? 'Running Tests...' : 'Run API Tests'}
            </Button>
            <Button onClick={testResumeRoute} variant="outline" className="mr-4">
              Test Resume Route
            </Button>
            <Button onClick={testApiRoute} variant="outline">
              Test API Route
            </Button>
          </div>
        </div>

        {testResults.length > 0 && (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Test Results</h2>
            <div className="space-y-4">
              {testResults.map((result, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <h3 className="font-medium text-gray-900 mb-2">{result.test}</h3>
                  <pre className="bg-gray-100 p-3 rounded text-sm overflow-auto">
                    {JSON.stringify(result.result, null, 2)}
                  </pre>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mt-6">
          <h3 className="text-lg font-medium text-blue-900 mb-2">Expected Behavior</h3>
          <ul className="text-blue-800 space-y-1">
            <li>• <strong>Resume Route:</strong> Should load the resume page with PDF viewer</li>
            <li>• <strong>API Route:</strong> Should return JSON with PDF data</li>
            <li>• <strong>API Tests:</strong> Should show successful API calls</li>
          </ul>
        </div>
      </div>
    </div>
  )
} 