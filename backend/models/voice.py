from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

class SpeechTranscript(BaseModel):
    """Speech transcript with timing information"""
    text: str
    start_time: float
    end_time: float
    confidence: float
    speaker_id: Optional[str] = None

class SpeechFeatures(BaseModel):
    """Extracted speech features"""
    pitch_mean: float
    pitch_std: float
    pitch_min: float
    pitch_max: float
    energy_mean: float
    energy_std: float
    energy_min: float
    energy_max: float
    speech_rate: float  # words per minute
    pause_duration_mean: float
    pause_duration_std: float
    pause_count: int
    clarity_score: float
    pronunciation_score: float

class FillerWordAnalysis(BaseModel):
    """Analysis of filler words and speech disfluencies"""
    filler_words: Dict[str, int]  # word -> count
    filler_word_rate: float  # per 100 words
    disfluency_count: int
    disfluency_rate: float  # per minute
    common_fillers: List[str]

class ToneAnalysis(BaseModel):
    """Tone and emotional analysis of speech"""
    tone_confidence: Dict[str, float]  # emotion -> confidence
    dominant_tone: str
    tone_variability: float
    confidence_score: float
    enthusiasm_score: float
    professionalism_score: float

class VoiceQualityMetrics(BaseModel):
    """Voice quality measurements"""
    volume_mean: float
    volume_std: float
    volume_range: float
    articulation_rate: float
    voice_stability: float
    breathiness_score: float
    nasality_score: float
    overall_voice_quality: float

class SpeechPatternAnalysis(BaseModel):
    """Analysis of speech patterns and delivery"""
    speech_features: SpeechFeatures
    filler_word_analysis: FillerWordAnalysis
    tone_analysis: ToneAnalysis
    voice_quality: VoiceQualityMetrics
    engagement_score: float
    clarity_score: float
    confidence_score: float

class VoiceAnalysisRequest(BaseModel):
    """Request model for voice analysis"""
    audio_file: str
    transcript: Optional[str] = None
    analysis_type: str = Field(default="comprehensive", description="Analysis type: basic, detailed, comprehensive")
    target_metrics: List[str] = ["clarity", "confidence", "pace", "tone"]
    language_code: str = "en-US"

class VoiceAnalysisResponse(BaseModel):
    """Response model for voice analysis"""
    analysis_id: str
    audio_metadata: Dict[str, Any]
    transcript: Optional[SpeechTranscript] = None
    speech_analysis: SpeechPatternAnalysis
    overall_score: float
    recommendations: List[str]
    analysis_timestamp: datetime
    processing_time_ms: int

class VoiceFeedback(BaseModel):
    """Detailed voice quality feedback"""
    session_id: str
    strengths: List[str]
    areas_for_improvement: List[str]
    specific_suggestions: List[str]
    progress_metrics: Dict[str, float]
    comparison_with_previous: Optional[Dict[str, float]] = None
    practice_exercises: List[str]
    feedback_timestamp: datetime

class VoiceSession(BaseModel):
    """Voice analysis session data"""
    session_id: str
    user_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    audio_file_path: str
    transcript_path: Optional[str] = None
    analysis_results: List[VoiceAnalysisResponse]
    feedback: Optional[VoiceFeedback] = None
    status: str  # "active", "completed", "failed"