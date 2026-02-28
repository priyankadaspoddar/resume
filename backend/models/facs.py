from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

class FacialLandmarks(BaseModel):
    """Facial landmarks detected in a frame"""
    left_eye: List[List[float]]
    right_eye: List[List[float]]
    nose_tip: List[float]
    mouth: List[List[float]]
    jawline: List[List[float]]
    eyebrows: Dict[str, List[List[float]]]

class FACSActionUnit(BaseModel):
    """Facial Action Coding System Action Unit"""
    au_id: str
    intensity: float
    confidence: float
    description: str
    muscle_group: str

class MicroExpression(BaseModel):
    """Detected micro-expression"""
    expression_type: str
    intensity: float
    duration_ms: float
    confidence: float
    timestamp: datetime

class PostureAnalysis(BaseModel):
    """Body posture analysis"""
    head_pose: Dict[str, float]  # pitch, yaw, roll
    shoulder_alignment: Dict[str, float]
    spine_curvature: float
    overall_posture_score: float
    posture_class: str  # "good", "neutral", "poor"

class GestureAnalysis(BaseModel):
    """Hand and body gesture analysis"""
    gesture_type: str
    confidence: float
    duration_ms: float
    frequency: int
    timestamp: datetime

class EyeContactAnalysis(BaseModel):
    """Eye contact and gaze analysis"""
    gaze_direction: Dict[str, float]  # x, y coordinates
    eye_contact_duration: float
    blink_rate: float
    pupil_diameter: float
    focus_score: float

class FACSFrameAnalysis(BaseModel):
    """Analysis results for a single video frame"""
    frame_number: int
    timestamp: datetime
    facial_landmarks: Optional[FacialLandmarks] = None
    action_units: List[FACSActionUnit]
    detected_emotions: Dict[str, float]
    micro_expressions: List[MicroExpression]
    posture: Optional[PostureAnalysis] = None
    gestures: List[GestureAnalysis]
    eye_contact: Optional[EyeContactAnalysis] = None
    overall_engagement_score: float

class FACSVideoAnalysis(BaseModel):
    """Analysis results for an entire video"""
    video_id: str
    total_frames: int
    duration_seconds: float
    frame_analysis: List[FACSFrameAnalysis]
    emotion_timeline: Dict[str, List[Dict[str, float]]]
    posture_timeline: List[PostureAnalysis]
    gesture_timeline: List[GestureAnalysis]
    eye_contact_timeline: List[EyeContactAnalysis]
    micro_expression_timeline: List[MicroExpression]
    overall_performance_score: float
    recommendations: List[str]

class FACSAnalysisRequest(BaseModel):
    """Request model for FACS video analysis"""
    video_file: str
    analysis_duration: Optional[int] = None  # in seconds
    target_focus: List[str] = ["emotions", "posture", "gestures", "eye_contact"]
    real_time_mode: bool = False
    confidence_threshold: float = 0.5

class FACSAnalysisResponse(BaseModel):
    """Response model for FACS analysis"""
    analysis_id: str
    video_metadata: Dict[str, Any]
    summary: Dict[str, float]
    detailed_analysis: FACSVideoAnalysis
    recommendations: List[str]
    analysis_timestamp: datetime
    processing_time_ms: int

class FACSRealTimeResponse(BaseModel):
    """Real-time FACS analysis response for WebSocket"""
    frame_number: int
    timestamp: datetime
    current_emotion: str
    emotion_confidence: float
    action_units: List[FACSActionUnit]
    posture_score: float
    eye_contact_score: float
    engagement_score: float
    recommendations: List[str]