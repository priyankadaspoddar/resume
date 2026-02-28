# Resume-Based Interview System

A comprehensive AI-powered interview preparation platform that analyzes resumes, detects facial expressions, and evaluates speech patterns.

## Features

### 1. Named Entity Recognition & Keyword Extraction (NER-KE Algorithm v2.0)
- Extracts key information from resumes using advanced NLP techniques
- Identifies skills, experience, education, and professional details
- Generates interview questions based on extracted content

### 2. FACS Vision Analysis (Facial Action Coding System)
- Real-time facial expression analysis using Gemini 2.5 Pro
- Detects micro-expressions, posture, gestures, and eye contact
- Provides feedback on non-verbal communication

### 3. Voice Quality Engine
- Speech pattern and delivery analysis
- Analyzes clarity, pacing, tone confidence, and filler word detection
- Overall engagement scoring using NLP techniques

## Technology Stack

- **Backend**: Python with FastAPI
- **Frontend**: React with TypeScript
- **AI Models**: Gemini 2.5 Pro, spaCy, OpenCV
- **Database**: PostgreSQL
- **Real-time Communication**: WebSockets

## Installation

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL
- Gemini API credentials

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## Usage

1. Upload your resume
2. Start a mock interview session
3. Receive comprehensive feedback on:
   - Resume content analysis
   - Facial expressions and body language
   - Speech patterns and delivery

## Project Structure

```
resume-interview-system/
├── backend/
│   ├── app.py                    # Main FastAPI application
│   ├── models/                   # Pydantic models
│   ├── services/                 # Business logic
│   │   ├── ner_ke.py            # NER-KE Algorithm v2.0
│   │   ├── facs_analysis.py     # FACS Vision Analysis
│   │   └── voice_engine.py      # Voice Quality Engine
│   ├── utils/                    # Utility functions
│   └── tests/                    # Unit tests
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── pages/               # Page components
│   │   ├── services/            # API services
│   │   └── hooks/               # Custom hooks
│   └── public/
└── docs/                        # Documentation
```

## API Endpoints

### Resume Analysis
- `POST /api/resume/analyze` - Analyze uploaded resume
- `GET /api/resume/questions` - Get generated interview questions

### FACS Analysis
- `POST /api/facs/analyze` - Analyze facial expressions from video
- `GET /api/facs/feedback` - Get FACS-based feedback

### Voice Analysis
- `POST /api/voice/analyze` - Analyze speech patterns
- `GET /api/voice/feedback` - Get voice quality feedback

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for your changes
5. Submit a pull request

## License

MIT License