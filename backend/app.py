from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from typing import List, Dict, Any
import os
import logging
from dotenv import load_dotenv

# Import services
from services.ner_ke import ResumeAnalyzer
from services.facs_analysis import FACSAnalyzer
from services.voice_engine import VoiceAnalyzer
from services.interview_coach import InterviewCoach

# Import models
from models.resume import ResumeAnalysisRequest, ResumeAnalysisResponse
from models.facs import FACSAnalysisRequest, FACSAnalysisResponse
from models.voice import VoiceAnalysisRequest, VoiceAnalysisResponse
from models.interview import InterviewSession, InterviewFeedback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Resume-Based Interview System",
    description="AI-powered interview preparation platform with resume analysis, FACS vision analysis, and voice quality engine",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
resume_analyzer = ResumeAnalyzer()
facs_analyzer = FACSAnalyzer()
voice_analyzer = VoiceAnalyzer()
interview_coach = InterviewCoach()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Resume-Based Interview System...")
    await resume_analyzer.initialize()
    await facs_analyzer.initialize()
    await voice_analyzer.initialize()
    logger.info("All services initialized successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down services...")
    await resume_analyzer.cleanup()
    await facs_analyzer.cleanup()
    await voice_analyzer.cleanup()
    logger.info("Services shutdown complete")

# Resume Analysis Endpoints
@app.post("/api/resume/analyze", response_model=ResumeAnalysisResponse)
async def analyze_resume(
    file: UploadFile = File(...),
    request: ResumeAnalysisRequest = Depends()
):
    """Analyze uploaded resume using NER-KE Algorithm v2.0"""
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.pdf', '.docx', '.txt')):
            raise HTTPException(status_code=400, detail="Unsupported file format. Please upload PDF, DOCX, or TXT files.")
        
        # Read file content
        content = await file.read()
        
        # Analyze resume
        result = await resume_analyzer.analyze_resume(content, file.filename, request)
        
        logger.info(f"Resume analysis completed for {file.filename}")
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing resume: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/resume/questions")
async def get_interview_questions(resume_id: str):
    """Generate interview questions based on resume analysis"""
    try:
        questions = await resume_analyzer.generate_interview_questions(resume_id)
        return {"questions": questions}
    except Exception as e:
        logger.error(f"Error generating questions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# FACS Analysis Endpoints
@app.websocket("/ws/facs/analyze")
async def facs_analysis_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time FACS analysis"""
    await websocket.accept()
    try:
        while True:
            # Receive video frame data
            frame_data = await websocket.receive_bytes()
            
            # Analyze frame
            result = await facs_analyzer.analyze_frame(frame_data)
            
            # Send analysis result
            await websocket.send_json(result)
            
    except Exception as e:
        logger.error(f"FACS WebSocket error: {str(e)}")
        await websocket.close()

@app.post("/api/facs/analyze", response_model=FACSAnalysisResponse)
async def analyze_facs_video(request: FACSAnalysisRequest):
    """Analyze pre-recorded video for FACS analysis"""
    try:
        result = await facs_analyzer.analyze_video(request)
        return result
    except Exception as e:
        logger.error(f"Error in FACS analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Voice Analysis Endpoints
@app.post("/api/voice/analyze", response_model=VoiceAnalysisResponse)
async def analyze_voice(request: VoiceAnalysisRequest):
    """Analyze speech patterns and voice quality"""
    try:
        result = await voice_analyzer.analyze_speech(request)
        return result
    except Exception as e:
        logger.error(f"Error in voice analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/voice/feedback")
async def get_voice_feedback(session_id: str):
    """Get detailed voice quality feedback"""
    try:
        feedback = await voice_analyzer.get_detailed_feedback(session_id)
        return feedback
    except Exception as e:
        logger.error(f"Error getting voice feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Interview Session Endpoints
@app.post("/api/interview/start")
async def start_interview_session(resume_id: str):
    """Start a new interview session"""
    try:
        session = await interview_coach.start_session(resume_id)
        return {"session_id": session.session_id, "status": "started"}
    except Exception as e:
        logger.error(f"Error starting interview session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/interview/feedback")
async def get_interview_feedback(session_id: str):
    """Get comprehensive interview feedback"""
    try:
        feedback = await interview_coach.get_session_feedback(session_id)
        return feedback
    except Exception as e:
        logger.error(f"Error getting interview feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Root endpoint with API documentation"""
    return HTMLResponse("""
    <html>
        <head>
            <title>Resume-Based Interview System</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 800px; margin: 0 auto; }
                h1 { color: #333; }
                .endpoint { background: #f5f5f5; padding: 20px; margin: 10px 0; border-radius: 5px; }
                .method { font-weight: bold; color: #007bff; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Resume-Based Interview System API</h1>
                <p>AI-powered interview preparation platform with advanced analysis capabilities.</p>
                
                <div class="endpoint">
                    <span class="method">POST</span> /api/resume/analyze - Analyze resume using NER-KE Algorithm v2.0
                </div>
                <div class="endpoint">
                    <span class="method">GET</span> /api/resume/questions - Generate interview questions
                </div>
                <div class="endpoint">
                    <span class="method">WebSocket</span> /ws/facs/analyze - Real-time FACS analysis
                </div>
                <div class="endpoint">
                    <span class="method">POST</span> /api/facs/analyze - Analyze video for facial expressions
                </div>
                <div class="endpoint">
                    <span class="method">POST</span> /api/voice/analyze - Analyze speech patterns
                </div>
                <div class="endpoint">
                    <span class="method">GET</span> /api/voice/feedback - Get voice quality feedback
                </div>
                <div class="endpoint">
                    <span class="method">POST</span> /api/interview/start - Start interview session
                </div>
                <div class="endpoint">
                    <span class="method">GET</span> /api/interview/feedback - Get comprehensive feedback
                </div>
                
                <p><a href="/docs">API Documentation</a> | <a href="/redoc">ReDoc</a></p>
            </div>
        </body>
    </html>
    """)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )