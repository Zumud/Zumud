import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const formData = await request.formData();
    const file = formData.get('resume') as File;
    const step = formData.get('step') as string;

    if (!file && !step) {
      return NextResponse.json(
        { error: 'No file uploaded' },
        { status: 400 }
      );
    }

    if (file && file.type !== 'application/pdf') {
      return NextResponse.json(
        { error: 'Only PDF files are allowed' },
        { status: 400 }
      );
    }

    if (step === '1') {
      // Step 1: Upload and extract text
      const buffer = await file.arrayBuffer();
      const externalFormData = new FormData();
      externalFormData.append('file', new Blob([buffer], { type: 'application/pdf' }), file.name);

      const response = await fetch('http://localhost:8000/upload/resume-text', {
        method: 'POST',
        body: externalFormData,
      });

      if (!response.ok) {
        throw new Error('Failed to upload to external API');
      }

      const result = await response.json();
      console.log('Step 1 Response:', result);
      return NextResponse.json(result);
    } else if (step === '2') {
      // Step 2: Generate PDF resume with extracted text
      const extractedText = formData.get('extracted_text') as string;
      
      // Use GET method with query parameters
      const url = new URL('http://localhost:8000/applications/resume/pdf');
      url.searchParams.append('job_description', extractedText);
      
      const response = await fetch(url.toString(), {
        method: 'GET',
        headers: {
          'accept': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to generate PDF resume');
      }

      const result = await response.json();
      console.log('Step 2 Response:', result);
      return NextResponse.json(result);
    }

    return NextResponse.json(
      { error: 'Invalid step' },
      { status: 400 }
    );
  } catch (error) {
    console.error('Error:', error);
    return NextResponse.json(
      { error: 'Failed to process request' },
      { status: 500 }
    );
  }
} 