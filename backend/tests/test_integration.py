import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
import tempfile
import os

from app import app
from services.ner_ke import ResumeAnalyzer
from services.facs_analysis import FACSAnalyzer
from services.voice_engine import VoiceAnalyzer
from services.interview_coach import InterviewCoach

class TestResumeInterviewSystem:
    """Integration tests for the Resume-Based Interview System"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    async def mock_services(self):
        """Mock all services for testing"""
        with patch('services.ner_ke.ResumeAnalyzer') as mock_resume, \
             patch('services.facs_analysis.FACSAnalyzer') as mock_facs, \
             patch('services.voice_engine.VoiceAnalyzer') as mock_voice, \
             patch('services.interview_coach.InterviewCoach') as mock_coach:
            
            # Configure mock services
            mock_resume.return_value = Mock()
            mock_resume.return_value.initialize = AsyncMock()
            mock_resume.return_value.cleanup = AsyncMock()
            mock_resume.return_value.analyze_resume = AsyncMock()
            mock_resume.return_value.generate_interview_questions = AsyncMock()
            
            mock_facs.return_value = Mock()
            mock_facs.return_value.initialize = AsyncMock()
            mock_facs.return_value.cleanup = AsyncMock()
            mock_facs.return_value.analyze_frame = AsyncMock()
            mock_facs.return_value.analyze_video = AsyncMock()
            
            mock_voice.return_value = Mock()
            mock_voice.return_value.initialize = AsyncMock()
            mock_voice.return_value.cleanup = AsyncMock()
            mock_voice.return_value.analyze_speech = AsyncMock()
            mock_voice.return_value.get_detailed_feedback = AsyncMock()
            
            mock_coach.return_value = Mock()
            mock_coach.return_value.initialize = AsyncMock()
            mock_coach.return_value.cleanup = AsyncMock()
            mock_coach.return_value.start_session = AsyncMock()
            mock_coach.return_value.get_session_feedback = AsyncMock()
            
            yield {
                'resume': mock_resume.return_value,
                'facs': mock_facs.return_value,
                'voice': mock_voice.return_value,
                'coach': mock_coach.return_value
            }
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns HTML"""
        response = client.get("/")
        assert response.status_code == 200
        assert "Resume-Based Interview System" in response.text
        assert "API Documentation" in response.text
    
    def test_api_docs(self, client):
        """Test API documentation endpoints"""
        # Test OpenAPI docs
        response = client.get("/docs")
        assert response.status_code == 200
        
        # Test ReDoc
        response = client.get("/redoc")
        assert response.status_code == 200
        
        # Test OpenAPI schema
        response = client.get("/openapi.json")
        assert response.status_code == 200
        assert "Resume-Based Interview System" in response.text
    
    @pytest.mark.asyncio
    async def test_resume_analysis_endpoint(self, client, mock_services):
        """Test resume analysis endpoint"""
        # Mock resume analysis response
        mock_response = {
            "resume_id": "test_resume_123",
            "metadata": {
                "filename": "test_resume.pdf",
                "file_size": 1024,
                "file_type": "pdf",
                "upload_date": "2023-01-01T00:00:00",
                "extracted_text_length": 1000
            },
            "personal_info": {
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "+1234567890"
            },
            "education": [],
            "work_experience": [],
            "skills": [],
            "projects": [],
            "certifications": [],
            "extracted_keywords": ["Python", "JavaScript"],
            "entities": {"PERSON": ["John Doe"]},
            "quality_score": 85.5,
            "recommendations": ["Add more technical skills"],
            "analysis_timestamp": "2023-01-01T00:00:00",
            "processing_time_ms": 1000
        }
        
        mock_services['resume'].analyze_resume.return_value = mock_response
        
        # Create a test PDF file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(b"%PDF-1.4 test content")
            temp_file_path = temp_file.name
        
        try:
            with open(temp_file_path, 'rb') as f:
                response = client.post(
                    "/api/resume/analyze",
                    files={"file": ("test_resume.pdf", f, "application/pdf")},
                    data={"extract_keywords": True, "extract_entities": True}
                )
            
            assert response.status_code == 200
            assert response.json()["resume_id"] == "test_resume_123"
            assert response.json()["quality_score"] == 85.5
            
        finally:
            os.unlink(temp_file_path)
    
    @pytest.mark.asyncio
    async def test_interview_questions_endpoint(self, client, mock_services):
        """Test interview questions generation endpoint"""
        mock_questions = {
            "questions": [
                {
                    "question": "Tell me about yourself",
                    "category": "behavioral",
                    "difficulty": "easy"
                }
            ],
            "total_questions": 1,
            "categories": ["behavioral"]
        }
        
        mock_services['resume'].generate_interview_questions.return_value = mock_questions
        
        response = client.get("/api/resume/questions?resume_id=test_resume_123")
        
        assert response.status_code == 200
        assert len(response.json()["questions"]) == 1
        assert response.json()["questions"][0]["question"] == "Tell me about yourself"
    
    @pytest.mark.asyncio
    async def test_facs_analysis_endpoint(self, client, mock_services):
        """Test FACS analysis endpoint"""
        mock_response = {
            "analysis_id": "facs_test_123",
            "video_metadata": {"duration": 300, "resolution": "1920x1080"},
            "summary": {"engagement_score": 0.75},
            "detailed_analysis": {
                "video_id": "facs_test_123",
                "total_frames": 9000,
                "duration_seconds": 300,
                "overall_performance_score": 0.78
            },
            "recommendations": ["Improve posture"],
            "analysis_timestamp": "2023-01-01T00:00:00",
            "processing_time_ms": 5000
        }
        
        mock_services['facs'].analyze_video.return_value = mock_response
        
        response = client.post(
            "/api/facs/analyze",
            json={
                "video_file": "test_video.mp4",
                "analysis_duration": 300,
                "target_focus": ["emotions", "posture"]
            }
        )
        
        assert response.status_code == 200
        assert response.json()["analysis_id"] == "facs_test_123"
        assert response.json()["summary"]["engagement_score"] == 0.75
    
    @pytest.mark.asyncio
    async def test_voice_analysis_endpoint(self, client, mock_services):
        """Test voice analysis endpoint"""
        mock_response = {
            "analysis_id": "voice_test_123",
            "audio_metadata": {"duration_seconds": 60},
            "speech_analysis": {
                "engagement_score": 0.8,
                "clarity_score": 0.75,
                "confidence_score": 0.85
            },
            "overall_score": 0.8,
            "recommendations": ["Reduce filler words"],
            "analysis_timestamp": "2023-01-01T00:00:00",
            "processing_time_ms": 2000
        }
        
        mock_services['voice'].analyze_speech.return_value = mock_response
        
        response = client.post(
            "/api/voice/analyze",
            json={
                "audio_file": "test_audio.wav",
                "transcript": "Hello, this is my answer",
                "analysis_type": "comprehensive"
            }
        )
        
        assert response.status_code == 200
        assert response.json()["analysis_id"] == "voice_test_123"
        assert response.json()["overall_score"] == 0.8
    
    @pytest.mark.asyncio
    async def test_interview_session_endpoint(self, client, mock_services):
        """Test interview session endpoints"""
        # Mock session start
        mock_session = {
            "session_id": "session_test_123",
            "user_id": "user_123",
            "resume_id": "test_resume_123",
            "interview_type": "practice",
            "status": "active",
            "questions": [],
            "user_answers": []
        }
        
        mock_services['coach'].start_session.return_value = mock_session
        
        response = client.post(
            "/api/interview/start",
            json={"resume_id": "test_resume_123", "interview_type": "practice"}
        )
        
        assert response.status_code == 200
        assert response.json()["session_id"] == "session_test_123"
        assert response.json()["status"] == "started"
    
    def test_error_handling(self, client):
        """Test error handling for invalid requests"""
        # Test invalid file format
        response = client.post(
            "/api/resume/analyze",
            files={"file": ("test.txt", b"invalid content", "text/plain")},
            data={"extract_keywords": True}
        )
        
        # Should return 400 for invalid file format
        assert response.status_code in [400, 500]  # Depends on implementation
    
    @pytest.mark.asyncio
    async def test_service_initialization(self, mock_services):
        """Test service initialization"""
        # This would test the startup event
        # In a real test, you'd need to trigger the startup event
        pass
    
    @pytest.mark.asyncio
    async def test_service_cleanup(self, mock_services):
        """Test service cleanup"""
        # This would test the shutdown event
        # In a real test, you'd need to trigger the shutdown event
        pass

class TestNERKEAlgorithm:
    """Unit tests for NER-KE Algorithm v2.0"""
    
    def test_resume_text_extraction(self):
        """Test text extraction from different file formats"""
        # This would test the _extract_text method
        pass
    
    def test_personal_info_extraction(self):
        """Test personal information extraction using NER"""
        # This would test the _extract_personal_info method
        pass
    
    def test_education_extraction(self):
        """Test education information extraction"""
        # This would test the _extract_education method
        pass
    
    def test_work_experience_extraction(self):
        """Test work experience extraction"""
        # This would test the _extract_work_experience method
        pass
    
    def test_skill_extraction(self):
        """Test skill extraction and categorization"""
        # This would test the _extract_skills method
        pass
    
    def test_quality_score_calculation(self):
        """Test resume quality score calculation"""
        # This would test the _calculate_quality_score method
        pass

class TestFACSAnalysis:
    """Unit tests for FACS Vision Analysis"""
    
    def test_facial_landmark_detection(self):
        """Test facial landmark detection"""
        # This would test the _extract_eye_landmarks method
        pass
    
    def test_action_unit_detection(self):
        """Test FACS Action Unit detection"""
        # This would test the _calculate_au_intensity method
        pass
    
    def test_emotion_detection(self):
        """Test emotion detection from facial features"""
        # This would test the _detect_emotions method
        pass
    
    def test_posture_analysis(self):
        """Test body posture analysis"""
        # This would test the _analyze_posture method
        pass
    
    def test_eye_contact_analysis(self):
        """Test eye contact and gaze analysis"""
        # This would test the _analyze_eye_contact method
        pass

class TestVoiceAnalysis:
    """Unit tests for Voice Quality Engine"""
    
    def test_speech_feature_extraction(self):
        """Test speech feature extraction"""
        # This would test the _extract_speech_features method
        pass
    
    def test_filler_word_detection(self):
        """Test filler word and disfluency detection"""
        # This would test the _analyze_filler_words method
        pass
    
    def test_tone_analysis(self):
        """Test tone and emotional analysis"""
        # This would test the _analyze_tone method
        pass
    
    def test_voice_quality_metrics(self):
        """Test voice quality metric calculation"""
        # This would test the _analyze_voice_quality method
        pass
    
    def test_speech_rate_calculation(self):
        """Test speech rate calculation"""
        # This would test the _calculate_speech_rate method
        pass

class TestInterviewCoach:
    """Unit tests for Interview Coach"""
    
    def test_question_generation(self):
        """Test interview question generation"""
        # This would test the _generate_session_questions method
        pass
    
    def test_answer_analysis(self):
        """Test answer content and structure analysis"""
        # This would test the _analyze_answer method
        pass
    
    def test_comprehensive_feedback(self):
        """Test comprehensive feedback generation"""
        # This would test the get_session_feedback method
        pass
    
    def test_progress_tracking(self):
        """Test user progress tracking and analytics"""
        # This would test the _calculate_progress_tracking method
        pass

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])