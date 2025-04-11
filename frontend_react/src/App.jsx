import { useState } from 'react'
import axios from 'axios'
import './App.css'

function App() {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState('')
  const [extractedText, setExtractedText] = useState('')

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setFile(selectedFile)
      setUploadStatus('')
      setExtractedText('')
    } else {
      setFile(null)
      setUploadStatus('Please select a valid PDF file')
    }
  }

  const handleUpload = async () => {
    if (!file) {
      setUploadStatus('Please select a file first')
      return
    }

    setLoading(true)
    setUploadStatus('')
    setExtractedText('')

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await axios.post('http://127.0.0.1:8000/upload/resume-text', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      setUploadStatus('Upload successful!')
      setFile(null)
      if (response.data.status === 'success') {
        setExtractedText(response.data.extracted_text)
      }
    } catch (error) {
      setUploadStatus('Upload failed. Please try again.')
      console.error('Upload error:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <div className="upload-container">
        <h1>PDF Upload</h1>
        <div className="upload-box">
          <input
            type="file"
            accept=".pdf"
            onChange={handleFileChange}
            className="file-input"
            id="file-upload"
            disabled={loading}
          />
          <label htmlFor="file-upload" className={`upload-label ${loading ? 'disabled' : ''}`}>
            {file ? file.name : 'Choose PDF file'}
          </label>
          {file && (
            <button
              onClick={handleUpload}
              disabled={loading}
              className="upload-button"
            >
              {loading ? (
                <div className="loading-spinner">
                  <div className="spinner"></div>
                  <span>Uploading...</span>
                </div>
              ) : (
                'Upload PDF'
              )}
            </button>
          )}
          {uploadStatus && (
            <p className={`status ${uploadStatus.includes('success') ? 'success' : 'error'}`}>
              {uploadStatus}
            </p>
          )}
          {extractedText && (
            <div className="text-box-container">
              <h3>Extracted Text:</h3>
              <textarea
                className="extracted-text"
                value={extractedText}
                readOnly
                placeholder="Extracted text will appear here..."
              />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default App
