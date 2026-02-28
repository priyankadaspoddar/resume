# Resume-Based Interview System - Development Guide

## Overview

This guide provides comprehensive information for developers working on the Resume-Based Interview System, including setup instructions, API documentation, and development best practices.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Technology Stack](#technology-stack)
3. [Setup Instructions](#setup-instructions)
4. [API Documentation](#api-documentation)
5. [Development Guidelines](#development-guidelines)
6. [Testing](#testing)
7. [Deployment](#deployment)
8. [Troubleshooting](#troubleshooting)

## System Architecture

### Backend Architecture

The backend follows a microservices-inspired architecture with the following components:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │   Interview      │    │   Gemini API    │
│   (Main Server) │◄──►│   Coach Service  │◄──►│   Integration   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │
         ├─────────────────────────────────────────────────────────┐
         │                                                         │
    ┌─────────────────┐                                       ┌─────────────────┐
    │   NER-KE        │                                       │   FACS Vision   │
    │   Algorithm     │                                       │   Analysis      │
    │   Service       │                                       │   Service       │
    └─────────────────┘                                       └─────────────────┘
         │                                                         │
         │                                                         │
    ┌─────────────────┐                                       ┌─────────────────┐
    │   Voice Quality │                                       │   MediaPipe     │
    │   Engine        │                                       │   Integration   │
    │   Service       │                                       │                 │
    └─────────────────┘                                       └─────────────────┘
```

### Frontend Architecture

The frontend uses a component-based architecture with React and Material-UI:

```
┌─────────────────────────────────────────────────────────────────┐
│                        Main App                                 │
├─────────────────────────────────────────────────────────────────┤
│  Sidebar  │  Topbar  │  Dashboard  │  Resume Upload  │  Analytics│
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                    ┌─────────────────────┐
                    │   Interview Session │
                    │   (Real-time FACS   │
                    │    & Voice Analysis)│
                    └─────────────────────┘
```

## Technology Stack

### Backend

- **Framework**: FastAPI (Python 3.9+)
- **AI/ML**: Google Gemini 2.5 Pro, spaCy, OpenCV, MediaPipe
- **Audio Processing**: librosa, speech_recognition, pydub
- **Computer Vision**: OpenCV, MediaPipe
- **Database**: PostgreSQL (planned)
- **Real-time Communication**: WebSockets
- **Testing**: pytest, unittest.mock
- **Documentation**: FastAPI automatic docs

### Frontend

- **Framework**: React 18 with TypeScript
- **UI Library**: Material-UI (MUI) v5
- **Routing**: React Router v6
- **Charts**: Chart.js with React integration
- **HTTP Client**: Axios
- **Build Tool**: Vite
- **Styling**: CSS-in-JS with MUI theming

### Development Tools

- **Code Quality**: ESLint, Prettier
- **Type Checking**: TypeScript
- **Package Management**: npm/pnpm
- **Environment**: Docker (optional)

## Setup Instructions

### Prerequisites

1. **Python 3.9+** with pip
2. **Node.js 16+** with npm
3. **PostgreSQL** (optional for production)
4. **Google Gemini API Key**

### Backend Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd resume-interview-system/backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the backend directory:
   ```bash
   GEMINI_API_KEY=your_gemini_api_key_here
   DATABASE_URL=postgresql://user:password@localhost:5432/interview_db
   ```

5. **Run the server**:
   ```bash
   python app.py
   ```

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd resume-interview-system/frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start development server**:
   ```bash
   npm run dev
   ```

4. **Access the application**:
   Open your browser and go to `http://localhost:3000`

### Docker Setup (Optional)

1. **Build and run backend**:
   ```bash
   cd resume-interview-system/backend
   docker build -t interview-system-backend .
   docker run -p 8000:8000 interview-system-backend
   ```

2. **Build and run frontend**:
   ```bash
   cd resume-interview-system/frontend
   docker build -t interview-system-frontend .
   docker run -p 3000:3000 interview-system-frontend
   ```

## API Documentation

### Resume Analysis API

#### POST /api/resume/analyze

Analyze uploaded resume using NER-KE Algorithm v2.0.

**Request**:
- **File**: Resume file (PDF, DOCX, or TXT)
- **Form Data**:
  - `extract_keywords`: boolean (optional)
  - `extract_entities`: boolean (optional)
  - `generate_questions`: boolean (optional)
  - `analysis_depth`: string (optional, "basic", "medium", "advanced")

**Response**:
```json
{
  "resume_id": "resume_1234567890",
  "metadata": {
    "filename": "john_doe_resume.pdf",
    "file_size": 102400,
    "file_type": "pdf",
    "upload_date": "2023-01-01T00:00:00",
    "extracted_text_length": 1500
  },
  "personal_info": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "location": "New York, NY"
  },
  "education": [...],
  "work_experience": [...],
  "skills": [...],
  "projects": [...],
  "certifications": [...],
  "extracted_keywords": ["Python", "JavaScript", "React"],
  "entities": {
    "PERSON": ["John Doe"],
    "ORG": ["Tech Corp"],
    "GPE": ["New York"]
  },
  "quality_score": 85.5,
  "recommendations": ["Add more technical skills"],
  "analysis_timestamp": "2023-01-01T00:00:00",
  "processing_time_ms": 1500
}
```

#### GET /api/resume/questions

Generate interview questions based on resume analysis.

**Query Parameters**:
- `resume_id`: string (required)

**Response**:
```json
{
  "questions": [
    {
      "question": "Tell me about yourself and your professional background.",
      "category": "behavioral",
      "difficulty": "easy",
      "related_skills": ["communication"],
      "explanation": "Assess overall presentation and communication skills"
    }
  ],
  "total_questions": 10,
  "categories": ["behavioral", "technical", "situational"],
  "generation_timestamp": "2023-01-01T00:00:00"
}
```

### FACS Analysis API

#### WebSocket /ws/facs/analyze

Real-time FACS analysis for video frames.

**Message Format**:
- **Input**: Binary frame data
- **Output**: JSON with analysis results

**Response**:
```json
{
  "frame_number": 123,
  "timestamp": "2023-01-01T00:00:00",
  "current_emotion": "neutral",
  "emotion_confidence": 0.85,
  "action_units": [
    {
      "au_id": "AU12",
      "intensity": 0.6,
      "confidence": 0.9,
      "description": "Lip corner puller",
      "muscle_group": "Zygomaticus major"
    }
  ],
  "posture_score": 0.75,
  "eye_contact_score": 0.8,
  "engagement_score": 0.82,
  "recommendations": ["Maintain better eye contact"]
}
```

#### POST /api/facs/analyze

Analyze pre-recorded video for comprehensive FACS analysis.

**Request**:
```json
{
  "video_file": "path/to/video.mp4",
  "analysis_duration": 300,
  "target_focus": ["emotions", "posture", "gestures", "eye_contact"],
  "real_time_mode": false,
  "confidence_threshold": 0.5
}
```

**Response**:
```json
{
  "analysis_id": "facs_1234567890",
  "video_metadata": {
    "duration": 300,
    "resolution": "1920x1080",
    "frame_rate": 30
  },
  "summary": {
    "engagement_score": 0.75,
    "emotion_consistency": 0.8,
    "posture_score": 0.7,
    "eye_contact_score": 0.85,
    "gesture_effectiveness": 0.6
  },
  "detailed_analysis": {
    "video_id": "facs_1234567890",
    "total_frames": 9000,
    "duration_seconds": 300,
    "frame_analysis": [...],
    "emotion_timeline": {...},
    "posture_timeline": [...],
    "gesture_timeline": [...],
    "eye_contact_timeline": [...],
    "micro_expression_timeline": [...],
    "overall_performance_score": 0.78,
    "recommendations": ["Improve posture", "Use more natural gestures"]
  },
  "recommendations": [...],
  "analysis_timestamp": "2023-01-01T00:00:00",
  "processing_time_ms": 5000
}
```

### Voice Analysis API

#### POST /api/voice/analyze

Analyze speech patterns and voice quality.

**Request**:
```json
{
  "audio_file": "path/to/audio.wav",
  "transcript": "Hello, this is my answer to the question.",
  "analysis_type": "comprehensive",
  "target_metrics": ["clarity", "confidence", "pace", "tone"],
  "language_code": "en-US"
}
```

**Response**:
```json
{
  "analysis_id": "voice_1234567890",
  "audio_metadata": {
    "duration_seconds": 60,
    "sample_rate": 44100,
    "channels": 1,
    "bit_depth": 16
  },
  "transcript": {
    "text": "Hello, this is my answer to the question.",
    "start_time": 0.0,
    "end_time": 60.0,
    "confidence": 0.95,
    "speaker_id": "user"
  },
  "speech_analysis": {
    "speech_features": {
      "pitch_mean": 180.5,
      "pitch_std": 25.3,
      "speech_rate": 140,
      "pause_duration_mean": 1.2,
      "clarity_score": 0.85,
      "pronunciation_score": 0.9
    },
    "filler_word_analysis": {
      "filler_words": {"um": 3, "like": 2},
      "filler_word_rate": 8.5,
      "disfluency_count": 5,
      "common_fillers": ["um", "like"]
    },
    "tone_analysis": {
      "tone_confidence": {"confident": 0.8, "enthusiastic": 0.6},
      "dominant_tone": "confident",
      "confidence_score": 0.85,
      "enthusiasm_score": 0.6
    },
    "voice_quality": {
      "volume_mean": 0.7,
      "voice_stability": 0.8,
      "overall_voice_quality": 0.75
    },
    "engagement_score": 0.8,
    "clarity_score": 0.85,
    "confidence_score": 0.85
  },
  "overall_score": 0.83,
  "recommendations": ["Reduce filler words", "Improve speech rate"],
  "analysis_timestamp": "2023-01-01T00:00:00",
  "processing_time_ms": 2000
}
```

### Interview Session API

#### POST /api/interview/start

Start a new interview session.

**Request**:
```json
{
  "resume_id": "resume_1234567890",
  "interview_type": "practice"
}
```

**Response**:
```json
{
  "session_id": "session_1234567890",
  "status": "started"
}
```

#### GET /api/interview/feedback

Get comprehensive interview feedback.

**Query Parameters**:
- `session_id`: string (required)

**Response**:
```json
{
  "overall_score": 0.78,
  "resume_feedback": {
    "resume_id": "resume_1234567890",
    "question_relevance": 0.85,
    "skill_alignment": 0.75,
    "strengths": ["Strong communication skills"],
    "improvements": ["Add more technical details"]
  },
  "facs_feedback": {
    "engagement_score": 0.75,
    "posture_score": 0.7,
    "eye_contact_score": 0.85,
    "recommendations": ["Use more natural gestures"]
  },
  "voice_feedback": {
    "clarity_score": 0.85,
    "confidence_score": 0.8,
    "recommendations": ["Reduce filler words"]
  },
  "question_feedback": [...],
  "overall_strengths": ["Good communication", "Technical knowledge"],
  "critical_improvements": ["Body language", "Speech clarity"],
  "personalized_recommendations": [...],
  "progress_tracking": {...},
  "next_steps": [...]
}
```

## Development Guidelines

### Code Style

#### Backend (Python)

- **Formatting**: Use Black for code formatting
- **Linting**: Use flake8 for linting
- **Type Hints**: Always use type hints for function signatures
- **Docstrings**: Use Google-style docstrings

```python
def analyze_resume(
    self, 
    content: bytes, 
    filename: str, 
    request: ResumeAnalysisRequest
) -> ResumeAnalysisResponse:
    """Analyze uploaded resume using NER-KE Algorithm v2.0.
    
    Args:
        content: Resume file content as bytes
        filename: Original filename
        request: Analysis request configuration
        
    Returns:
        ResumeAnalysisResponse with analysis results
        
    Raises:
        ValueError: If file format is unsupported
        Exception: If analysis fails
    """
    # Implementation
```

#### Frontend (TypeScript/React)

- **Formatting**: Use Prettier for code formatting
- **Linting**: Use ESLint with React hooks plugin
- **Naming**: Use camelCase for variables, PascalCase for components
- **Imports**: Group imports by type (libraries, components, utils)

```typescript
// Good
import React, { useState, useEffect } from 'react';
import { Button, Typography, Box } from '@mui/material';

// Component imports
import DashboardCard from './components/DashboardCard';
import ResumeUploadForm from './components/ResumeUploadForm';

// Utility imports
import { formatFileSize } from './utils/fileUtils';
import { analyzeResume } from './services/api';
```

### Error Handling

#### Backend

- Use FastAPI's HTTPException for HTTP errors
- Implement proper logging with structured logging
- Handle AI model failures gracefully
- Validate all inputs

```python
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

async def analyze_resume(self, content: bytes, filename: str) -> ResumeAnalysisResponse:
    try:
        # Validate input
        if not filename.lower().endswith(('.pdf', '.docx', '.txt')):
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        # Process resume
        result = await self._process_resume(content, filename)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing resume: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

#### Frontend

- Use error boundaries for React components
- Implement proper loading states
- Handle API errors gracefully
- Provide user-friendly error messages

```typescript
const [error, setError] = useState<string | null>(null);
const [loading, setLoading] = useState(false);

const handleUpload = async (file: File) => {
  setLoading(true);
  setError(null);
  
  try {
    const result = await uploadResume(file);
    // Handle success
  } catch (err) {
    setError('Failed to upload resume. Please try again.');
    console.error('Upload error:', err);
  } finally {
    setLoading(false);
  }
};
```

### Testing

#### Unit Tests

- Test individual functions and components
- Use mocking for external dependencies
- Aim for 80%+ code coverage

```python
# Backend unit test
def test_extract_personal_info():
    text = "John Doe\nEmail: john@example.com\nPhone: +1234567890"
    result = resume_analyzer._extract_personal_info(text)
    
    assert result.name == "John Doe"
    assert result.email == "john@example.com"
    assert result.phone == "+1234567890"
```

```typescript
// Frontend unit test
describe('ResumeUploadForm', () => {
  it('should render upload button', () => {
    render(<ResumeUploadForm />);
    expect(screen.getByText('Choose File')).toBeInTheDocument();
  });
  
  it('should validate file format', () => {
    const { getByTestId } = render(<ResumeUploadForm />);
    const fileInput = getByTestId('file-input');
    
    // Simulate invalid file
    fireEvent.change(fileInput, { target: { files: [invalidFile] } });
    
    expect(screen.getByText('Invalid file format')).toBeInTheDocument();
  });
});
```

#### Integration Tests

- Test API endpoints with real requests
- Test component interactions
- Test end-to-end workflows

```python
# API integration test
def test_resume_analysis_endpoint(client):
    with open('test_resume.pdf', 'rb') as f:
        response = client.post(
            '/api/resume/analyze',
            files={'file': ('test_resume.pdf', f, 'application/pdf')}
        )
    
    assert response.status_code == 200
    assert 'resume_id' in response.json()
    assert 'quality_score' in response.json()
```

### Performance Optimization

#### Backend

- Use async/await for I/O operations
- Implement caching for expensive operations
- Optimize AI model calls
- Use connection pooling for databases

```python
import asyncio
from functools import lru_cache

class ResumeAnalyzer:
    @lru_cache(maxsize=128)
    async def analyze_resume(self, content: bytes, filename: str) -> ResumeAnalysisResponse:
        # Cached analysis
        pass
    
    async def _process_multiple_resumes(self, resumes: List[Tuple[bytes, str]]):
        # Process in parallel
        tasks = [self.analyze_resume(content, filename) for content, filename in resumes]
        results = await asyncio.gather(*tasks)
        return results
```

#### Frontend

- Implement memoization for expensive calculations
- Use virtualization for long lists
- Optimize image and video loading
- Implement proper state management

```typescript
import { useMemo, useCallback } from 'react';
import { FixedSizeList as List } from 'react-window';

const ResumeList = ({ resumes }: { resumes: Resume[] }) => {
  const sortedResumes = useMemo(() => {
    return resumes.sort((a, b) => b.score - a.score);
  }, [resumes]);
  
  const handleResumeClick = useCallback((resumeId: string) => {
    // Handle click
  }, []);
  
  return (
    <List
      height={600}
      itemCount={sortedResumes.length}
      itemSize={50}
      itemData={sortedResumes}
    >
      {ResumeItem}
    </List>
  );
};
```

## Testing

### Running Tests

#### Backend Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=services --cov=app --cov-report=html

# Run specific test file
pytest tests/test_integration.py

# Run with verbose output
pytest -v
```

#### Frontend Tests

```bash
# Run all tests
npm test

# Run tests with coverage
npm test -- --coverage

# Run specific test file
npm test ResumeUpload.test.tsx
```

### Test Structure

#### Backend Test Structure

```
backend/
├── tests/
│   ├── __init__.py
│   ├── test_integration.py      # Integration tests
│   ├── test_ner_ke.py          # NER-KE algorithm tests
│   ├── test_facs_analysis.py   # FACS analysis tests
│   ├── test_voice_engine.py    # Voice engine tests
│   ├── test_interview_coach.py # Interview coach tests
│   └── fixtures/               # Test data and fixtures
│       ├── sample_resumes/     # Test resume files
│       ├── test_videos/        # Test video files
│       └── test_audio/         # Test audio files
```

#### Frontend Test Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── __tests__/
│   │   │   ├── Dashboard.test.tsx
│   │   │   ├── ResumeUpload.test.tsx
│   │   │   └── InterviewSession.test.tsx
│   │   └── ...
│   ├── pages/
│   │   ├── __tests__/
│   │   │   ├── Dashboard.test.tsx
│   │   │   └── ResumeUpload.test.tsx
│   │   └── ...
│   └── services/
│       ├── __tests__/
│       │   └── api.test.ts
│       └── ...
```

### Mocking External Services

#### Backend Mocking

```python
from unittest.mock import Mock, patch, AsyncMock

@patch('services.ner_ke.ResumeAnalyzer')
def test_resume_analysis(mock_resume_analyzer):
    # Configure mock
    mock_instance = Mock()
    mock_instance.analyze_resume = AsyncMock(return_value=mock_response)
    mock_resume_analyzer.return_value = mock_instance
    
    # Test
    result = await analyze_resume_endpoint(file, request)
    
    # Assert
    assert result.resume_id == "test_id"
```

#### Frontend Mocking

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { jest } from '@jest/globals';

// Mock API service
jest.mock('../services/api', () => ({
  analyzeResume: jest.fn(),
}));

describe('ResumeUpload', () => {
  it('should call API on upload', async () => {
    const mockAnalyzeResume = jest.fn();
    require('../services/api').analyzeResume.mockImplementation(mockAnalyzeResume);
    
    render(<ResumeUpload />);
    
    // Trigger upload
    const file = new File(['test'], 'test.pdf', { type: 'application/pdf' });
    const input = screen.getByTestId('file-input');
    fireEvent.change(input, { target: { files: [file] } });
    
    expect(mockAnalyzeResume).toHaveBeenCalledWith(file);
  });
});
```

## Deployment

### Production Deployment

#### Backend Deployment

1. **Environment Setup**:
   ```bash
   # Set production environment variables
   export GEMINI_API_KEY=your_production_key
   export DATABASE_URL=your_production_database_url
   export ENVIRONMENT=production
   ```

2. **Database Setup**:
   ```bash
   # Run migrations
   alembic upgrade head
   
   # Seed initial data
   python scripts/seed_data.py
   ```

3. **Application Deployment**:
   ```bash
   # Using Gunicorn
   gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker
   
   # Using Docker
   docker build -t interview-system .
   docker run -p 8000:8000 interview-system
   ```

#### Frontend Deployment

1. **Build Production Version**:
   ```bash
   npm run build
   ```

2. **Serve Static Files**:
   ```bash
   # Using Nginx
   nginx -s reload
   
   # Using Node.js
   npx serve -s dist
   ```

3. **Environment Configuration**:
   ```bash
   # Set API endpoint
   REACT_APP_API_URL=https://api.yourdomain.com
   
   # Build with environment variables
   npm run build
   ```

### Docker Deployment

#### Multi-Stage Dockerfile

```dockerfile
# Backend Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

# Frontend Dockerfile
FROM node:16-alpine

WORKDIR /app
COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

EXPOSE 3000
CMD ["npm", "run", "preview"]
```

#### Docker Compose

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - DATABASE_URL=${DATABASE_URL}
    depends_on:
      - database

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000

  database:
    image: postgres:13
    environment:
      POSTGRES_DB: interview_system
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### CI/CD Pipeline

#### GitHub Actions Example

```yaml
name: Deploy Interview System

on:
  push:
    branches: [ main ]

jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      
      - name: Run tests
        run: |
          cd backend
          pytest
      
      - name: Build Docker image
        run: docker build -t interview-system-backend .
      
      - name: Deploy to production
        run: |
          # Deployment commands

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: '16'
      
      - name: Install dependencies
        run: |
          cd frontend
          npm install
      
      - name: Run tests
        run: npm test -- --coverage
      
      - name: Build application
        run: npm run build
      
      - name: Deploy to production
        run: |
          # Deployment commands
```

## Troubleshooting

### Common Issues

#### Backend Issues

1. **Gemini API Connection Errors**:
   ```bash
   # Check API key
   echo $GEMINI_API_KEY
   
   # Test connection
   python -c "import google.generativeai as genai; genai.configure(api_key=os.getenv('GEMINI_API_KEY')); print('Connected')"
   ```

2. **Database Connection Errors**:
   ```bash
   # Check database URL
   echo $DATABASE_URL
   
   # Test connection
   python -c "import sqlalchemy; engine = sqlalchemy.create_engine(os.getenv('DATABASE_URL')); engine.connect()"
   ```

3. **Memory Issues with AI Models**:
   ```python
   # Reduce batch size
   # Use model quantization
   # Implement caching
   ```

#### Frontend Issues

1. **Build Failures**:
   ```bash
   # Clear cache
   npm cache clean --force
   
   # Reinstall dependencies
   rm -rf node_modules package-lock.json
   npm install
   
   # Check TypeScript errors
   npx tsc --noEmit
   ```

2. **API Connection Issues**:
   ```bash
   # Check CORS settings
   # Verify API endpoint
   # Check network tab in browser dev tools
   ```

3. **Performance Issues**:
   ```typescript
   // Implement memoization
   // Use virtualization for long lists
   // Optimize image loading
   ```

### Debugging Tools

#### Backend Debugging

```python
import logging
import traceback

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Add debug prints
logger.debug(f"Processing resume: {filename}")

# Handle exceptions with detailed traceback
try:
    result = await process_resume(content)
except Exception as e:
    logger.error(f"Error: {str(e)}")
    logger.error(traceback.format_exc())
    raise
```

#### Frontend Debugging

```typescript
// Enable React DevTools
// Use browser dev tools
// Add console logs
console.log('Resume upload started:', file);

// Use React Query DevTools for API debugging
import { ReactQueryDevtools } from 'react-query/devtools';
```

### Performance Monitoring

#### Backend Monitoring

```python
import time
import logging

def monitor_performance(func):
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            duration = time.time() - start_time
            logger.info(f"{func.__name__} took {duration:.2f} seconds")
    return wrapper

@monitor_performance
async def analyze_resume(self, content: bytes, filename: str):
    # Implementation
```

#### Frontend Monitoring

```typescript
// Performance monitoring
const startTime = performance.now();
// Component render
const endTime = performance.now();
console.log(`Component rendered in ${endTime - startTime}ms`);

// Error boundaries
class ErrorBoundary extends React.Component {
  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }
}
```

### Support and Resources

#### Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/docs)
- [Material-UI Documentation](https://mui.com/)
- [Google Gemini API](https://ai.google.dev/gemini-api)

#### Community Support
- GitHub Issues for bug reports
- Stack Overflow for general questions
- Discord/Slack for community chat

#### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

For more information, see [CONTRIBUTING.md](CONTRIBUTING.md).