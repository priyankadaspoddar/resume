from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum

class InterviewType(str, Enum):
    """Types of interview sessions"""
    BEHAVIORAL = "behavioral"
    TECHNICAL = "technical"
    CASE_STUDY = "case_study"
    MOCK = "mock"
    PRACTICE = "practice"

class SessionStatus(str, Enum):
    """Status of interview session"""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class QuestionCategory(str, Enum):
    """Categories of interview questions"""
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    SITUATIONAL = "situational"
    PROBLEM_SOLVING = "problem_solving"
    CULTURE_FIT = "culture_fit"

class AnswerQuality(BaseModel):
    """Quality metrics for an answer"""
    content_score: float
    structure_score: float
    relevance_score: float
    confidence_score: float
    technical_accuracy: Optional[float] = None
    communication_score: float
    overall_score: float

class InterviewQuestion(BaseModel):
    """Interview question with context"""
    question_id: str
    question_text: str
    category: QuestionCategory
    difficulty: str
    expected_duration: int  # in seconds
    related_skills: List[str]
    hints: List[str] = []

class UserAnswer(BaseModel):
    """User's answer to a question"""
    question_id: str
    answer_text: str
    answer_audio: Optional[str] = None  # path to audio file
    answer_video: Optional[str] = None  # path to video file
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    transcript: Optional[str] = None

class QuestionFeedback(BaseModel):
    """Feedback for a specific question answer"""
    question_id: str
    answer_quality: AnswerQuality
    strengths: List[str]
    areas_for_improvement: List[str]
    specific_feedback: str
    suggested_improvements: List[str]
    score_breakdown: Dict[str, float]

class ResumeBasedFeedback(BaseModel):
    """Feedback based on resume analysis"""
    resume_id: str
    question_relevance: float
    skill_alignment: float
    experience_validation: float
    gap_analysis: List[str]
    strength_validation: List[str]

class FACSFeedback(BaseModel):
    """Feedback from FACS analysis"""
    engagement_score: float
    emotion_consistency: float
    posture_score: float
    eye_contact_score: float
    gesture_effectiveness: float
    micro_expression_insights: List[str]
    non_verbal_recommendations: List[str]

class VoiceFeedback(BaseModel):
    """Feedback from voice analysis"""
    clarity_score: float
    confidence_score: float
    pace_score: float
    tone_score: float
    filler_word_count: int
    pronunciation_score: float
    vocal_variability: float
    voice_recommendations: List[str]

class ComprehensiveFeedback(BaseModel):
    """Comprehensive feedback combining all analysis"""
    overall_score: float
    resume_feedback: ResumeBasedFeedback
    facs_feedback: FACSFeedback
    voice_feedback: VoiceFeedback
    question_feedback: List[QuestionFeedback]
    overall_strengths: List[str]
    critical_improvements: List[str]
    personalized_recommendations: List[str]
    progress_tracking: Dict[str, float]
    next_steps: List[str]

class InterviewSession(BaseModel):
    """Complete interview session"""
    session_id: str
    user_id: str
    resume_id: str
    interview_type: InterviewType
    start_time: datetime
    end_time: Optional[datetime] = None
    status: SessionStatus
    questions: List[InterviewQuestion]
    user_answers: List[UserAnswer]
    feedback: Optional[ComprehensiveFeedback] = None
    session_metadata: Dict[str, Any] = {}
    total_duration: Optional[int] = None  # in seconds

class InterviewSummary(BaseModel):
    """Summary of interview session"""
    session_id: str
    overall_score: float
    average_question_score: float
    strongest_category: str
    weakest_category: str
    time_efficiency: float  # actual vs expected time
    completion_rate: float
    key_insights: List[str]
    improvement_priority: List[str]
    summary_timestamp: datetime

class PracticeRecommendation(BaseModel):
    """Personalized practice recommendation"""
    focus_area: str
    recommended_exercises: List[str]
    estimated_time: int  # in minutes
    difficulty_level: str
    priority: int  # 1-5 scale
    expected_improvement: float
    resources: List[str]

class InterviewProgress(BaseModel):
    """User's progress tracking"""
    user_id: str
    total_sessions: int
    average_score: float
    best_score: float
    worst_score: float
    progress_timeline: List[Dict[str, float]]
    skill_improvement: Dict[str, float]
    last_session_date: Optional[datetime] = None
    next_recommendation: Optional[PracticeRecommendation] = None