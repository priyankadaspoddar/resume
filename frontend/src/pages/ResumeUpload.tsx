import React, { useState } from 'react'
import { Box, Typography, Card, CardContent, Button, LinearProgress, Alert } from '@mui/material'
import { CloudUpload as UploadIcon } from '@mui/icons-material'

const ResumeUpload: React.FC = () => {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      const selectedFile = event.target.files[0]
      const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain']
      
      if (!validTypes.includes(selectedFile.type)) {
        setError('Please upload a PDF, DOCX, or TXT file.')
        return
      }
      
      setFile(selectedFile)
      setError(null)
    }
  }

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file to upload.')
      return
    }

    setUploading(true)
    setProgress(0)
    setError(null)

    try {
      // Simulate upload progress
      const interval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 90) {
            clearInterval(interval)
            return 90
          }
          return prev + 10
        })
      }, 200)

      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 3000))
      
      setProgress(100)
      setSuccess(true)
      
      setTimeout(() => {
        setSuccess(false)
        // Redirect to dashboard or show analysis results
      }, 2000)

    } catch (err) {
      setError('Upload failed. Please try again.')
    } finally {
      setUploading(false)
    }
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Resume Analysis
      </Typography>
      
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Upload Your Resume
          </Typography>
          
          <Box sx={{ mb: 3 }}>
            <input
              accept=".pdf,.docx,.txt"
              style={{ display: 'none' }}
              id="resume-upload"
              type="file"
              onChange={handleFileChange}
            />
            <label htmlFor="resume-upload">
              <Button
                variant="contained"
                component="span"
                startIcon={<UploadIcon />}
                disabled={uploading}
              >
                Choose File
              </Button>
            </label>
            
            {file && (
              <Typography sx={{ mt: 2, color: 'text.secondary' }}>
                Selected: {file.name}
              </Typography>
            )}
          </Box>

          {uploading && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Uploading and analyzing your resume...
              </Typography>
              <LinearProgress variant="determinate" value={progress} />
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                {progress}%
              </Typography>
            </Box>
          )}

          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          {success && (
            <Alert severity="success" sx={{ mb: 3 }}>
              Resume uploaded successfully! Analysis will begin shortly.
            </Alert>
          )}

          <Button
            variant="contained"
            onClick={handleUpload}
            disabled={!file || uploading}
            sx={{ mt: 2 }}
          >
            Upload and Analyze
          </Button>
        </CardContent>
      </Card>

      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Supported Formats
          </Typography>
          <Typography color="text.secondary">
            • PDF files (.pdf)
            <br />
            • Microsoft Word documents (.docx)
            <br />
            • Plain text files (.txt)
          </Typography>
          
          <Typography variant="h6" sx={{ mt: 3 }} gutterBottom>
            What We Analyze
          </Typography>
          <Typography color="text.secondary">
            • Personal information and contact details
            <br />
            • Education and work experience
            <br />
            • Skills and certifications
            <br />
            • Generate personalized interview questions
            <br />
            • Provide improvement recommendations
          </Typography>
        </CardContent>
      </Card>
    </Box>
  )
}

export default ResumeUpload