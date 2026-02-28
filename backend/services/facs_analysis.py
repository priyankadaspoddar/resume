import cv2
import mediapipe as mp
import numpy as np
import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from google.generativeai import GenerativeModel
import google.generativeai as genai
import os

from models.facs import (
    FACSAnalysisRequest, FACSAnalysisResponse, FACSRealTimeResponse,
    FacialLandmarks, FACSActionUnit, MicroExpression, PostureAnalysis,
    GestureAnalysis, EyeContactAnalysis, FACSFrameAnalysis, FACSVideoAnalysis
)

logger = logging.getLogger(__name__)

class FACSAnalyzer:
    """FACS Vision Analysis using Gemini 2.5 Pro's multimodal vision"""
    
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_pose = mp.solutions.pose
        self.mp_hands = mp.solutions.hands
        self.face_mesh = None
        self.pose_detector = None
        self.hands_detector = None
        self.gemini_model = None
        
        # FACS Action Units mapping
        self.au_mapping = self._initialize_au_mapping()
        
        # Emotion detection model
        self.emotion_model = None
        
    async def initialize(self):
        """Initialize FACS analysis components"""
        try:
            # Initialize MediaPipe components
            self.face_mesh = self.mp_face_mesh.FaceMesh(
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            
            self.pose_detector = self.mp_pose.Pose(
                static_image_mode=False,
                model_complexity=1,
                enable_segmentation=False,
                min_detection_confidence=0.5
            )
            
            self.hands_detector = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=2,
                min_detection_confidence=0.5
            )
            
            # Initialize Gemini model for advanced analysis
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            self.gemini_model = GenerativeModel('gemini-2.5-pro-vision')
            
            logger.info("FACS Analyzer initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing FACS analyzer: {str(e)}")
            raise
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.face_mesh:
            self.face_mesh.close()
        if self.pose_detector:
            self.pose_detector.close()
        if self.hands_detector:
            self.hands_detector.close()
        if self.gemini_model:
            del self.gemini_model
    
    def _initialize_au_mapping(self) -> Dict[str, List[int]]:
        """Initialize FACS Action Unit to landmark mapping"""
        return {
            "AU01": [1, 2, 3, 4],  # Inner brow raiser
            "AU02": [5, 6, 7, 8],  # Outer brow raiser
            "AU04": [9, 10, 11, 12],  # Brow lowerer
            "AU05": [13, 14, 15, 16],  # Upper lid raiser
            "AU06": [17, 18, 19, 20],  # Cheek raiser
            "AU07": [21, 22, 23, 24],  # Lid tightener
            "AU09": [25, 26, 27, 28],  # Nose wrinkler
            "AU10": [29, 30, 31, 32],  # Upper lip raiser
            "AU12": [33, 34, 35, 36],  # Lip corner puller
            "AU14": [37, 38, 39, 40],  # Dimpler
            "AU15": [41, 42, 43, 44],  # Lip corner depressor
            "AU17": [45, 46, 47, 48],  # Chin raiser
            "AU20": [49, 50, 51, 52],  # Lip stretcher
            "AU23": [53, 54, 55, 56],  # Lip tightener
            "AU25": [57, 58, 59, 60],  # Lips part
            "AU26": [61, 62, 63, 64],  # Jaw drop
            "AU45": [65, 66, 67, 68]   # Blink
        }
    
    async def analyze_frame(self, frame_data: bytes) -> FACSRealTimeResponse:
        """Analyze a single video frame for real-time FACS analysis"""
        try:
            # Convert bytes to numpy array and then to OpenCV image
            nparr = np.frombuffer(frame_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Process frame
            frame_analysis = self._process_frame(frame)
            
            return FACSRealTimeResponse(
                frame_number=0,  # Would be tracked in real implementation
                timestamp=datetime.now(),
                current_emotion=frame_analysis.get('dominant_emotion', 'neutral'),
                emotion_confidence=frame_analysis.get('emotion_confidence', 0.0),
                action_units=frame_analysis.get('action_units', []),
                posture_score=frame_analysis.get('posture_score', 0.0),
                eye_contact_score=frame_analysis.get('eye_contact_score', 0.0),
                engagement_score=frame_analysis.get('engagement_score', 0.0),
                recommendations=frame_analysis.get('recommendations', [])
            )
            
        except Exception as e:
            logger.error(f"Error in frame analysis: {str(e)}")
            raise
    
    def _process_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """Process a single frame and extract FACS features"""
        results = {}
        
        # Face mesh analysis
        face_results = self.face_mesh.process(frame)
        if face_results.multi_face_landmarks:
            face_landmarks = face_results.multi_face_landmarks[0]
            results.update(self._analyze_facial_features(face_landmarks, frame.shape))
        
        # Pose analysis
        pose_results = self.pose_detector.process(frame)
        if pose_results.pose_landmarks:
            results.update(self._analyze_posture(pose_results.pose_landmarks))
        
        # Hand analysis
        hand_results = self.hands_detector.process(frame)
        if hand_results.multi_hand_landmarks:
            results.update(self._analyze_gestures(hand_results.multi_hand_landmarks))
        
        # Eye contact analysis
        results.update(self._analyze_eye_contact(face_results, frame.shape))
        
        # Calculate overall scores
        results['engagement_score'] = self._calculate_engagement_score(results)
        results['recommendations'] = self._generate_facs_recommendations(results)
        
        return results
    
    def _analyze_facial_features(self, face_landmarks, frame_shape) -> Dict[str, Any]:
        """Analyze facial features and extract FACS Action Units"""
        landmarks = face_landmarks.landmark
        
        # Extract key facial landmarks
        left_eye = self._extract_eye_landmarks(landmarks, 'left')
        right_eye = self._extract_eye_landmarks(landmarks, 'right')
        mouth = self._extract_mouth_landmarks(landmarks)
        eyebrows = self._extract_eyebrow_landmarks(landmarks)
        
        # Calculate Action Unit intensities
        action_units = []
        for au_id, landmark_indices in self.au_mapping.items():
            intensity = self._calculate_au_intensity(landmarks, landmark_indices)
            if intensity > 0.2:  # Threshold for detection
                action_units.append(FACSActionUnit(
                    au_id=au_id,
                    intensity=intensity,
                    confidence=self._calculate_au_confidence(intensity),
                    description=self._get_au_description(au_id),
                    muscle_group=self._get_au_muscle_group(au_id)
                ))
        
        # Detect emotions
        emotions = self._detect_emotions(landmarks)
        
        # Detect micro-expressions
        micro_expressions = self._detect_micro_expressions(landmarks)
        
        return {
            'facial_landmarks': FacialLandmarks(
                left_eye=left_eye,
                right_eye=right_eye,
                nose_tip=[landmarks[1].x, landmarks[1].y],
                mouth=mouth,
                jawline=self._extract_jawline_landmarks(landmarks),
                eyebrows=eyebrows
            ),
            'action_units': action_units,
            'detected_emotions': emotions,
            'micro_expressions': micro_expressions
        }
    
    def _extract_eye_landmarks(self, landmarks, eye_type: str) -> List[List[float]]:
        """Extract eye landmarks"""
        if eye_type == 'left':
            indices = [33, 160, 158, 133, 153, 144]
        else:
            indices = [362, 385, 387, 263, 373, 380]
        
        return [[landmarks[i].x, landmarks[i].y] for i in indices]
    
    def _extract_mouth_landmarks(self, landmarks) -> List[List[float]]:
        """Extract mouth landmarks"""
        indices = [61, 185, 40, 270, 287, 314, 409, 78, 308, 324, 318, 402, 317, 14, 87, 178]
        return [[landmarks[i].x, landmarks[i].y] for i in indices]
    
    def _extract_eyebrow_landmarks(self, landmarks) -> Dict[str, List[List[float]]]:
        """Extract eyebrow landmarks"""
        left_indices = [55, 63, 70, 67, 105, 66, 107]
        right_indices = [285, 293, 300, 297, 334, 296, 336]
        
        return {
            'left': [[landmarks[i].x, landmarks[i].y] for i in left_indices],
            'right': [[landmarks[i].x, landmarks[i].y] for i in right_indices]
        }
    
    def _extract_jawline_landmarks(self, landmarks) -> List[List[float]]:
        """Extract jawline landmarks"""
        indices = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]
        return [[landmarks[i].x, landmarks[i].y] for i in indices]
    
    def _calculate_au_intensity(self, landmarks, landmark_indices: List[int]) -> float:
        """Calculate Action Unit intensity based on landmark movements"""
        # Simplified intensity calculation
        # In a real implementation, this would use more sophisticated geometric calculations
        if len(landmark_indices) >= 2:
            point1 = landmarks[landmark_indices[0]]
            point2 = landmarks[landmark_indices[1]]
            return abs(point1.y - point2.y)  # Vertical movement as intensity measure
        return 0.0
    
    def _calculate_au_confidence(self, intensity: float) -> float:
        """Calculate confidence based on intensity"""
        return min(intensity * 5, 1.0)  # Scale intensity to confidence
    
    def _get_au_description(self, au_id: str) -> str:
        """Get description for Action Unit"""
        descriptions = {
            "AU01": "Inner brow raiser",
            "AU02": "Outer brow raiser", 
            "AU04": "Brow lowerer",
            "AU05": "Upper lid raiser",
            "AU06": "Cheek raiser",
            "AU07": "Lid tightener",
            "AU09": "Nose wrinkler",
            "AU10": "Upper lip raiser",
            "AU12": "Lip corner puller",
            "AU14": "Dimpler",
            "AU15": "Lip corner depressor",
            "AU17": "Chin raiser",
            "AU20": "Lip stretcher",
            "AU23": "Lip tightener",
            "AU25": "Lips part",
            "AU26": "Jaw drop",
            "AU45": "Blink"
        }
        return descriptions.get(au_id, "Unknown Action Unit")
    
    def _get_au_muscle_group(self, au_id: str) -> str:
        """Get muscle group for Action Unit"""
        muscle_groups = {
            "AU01": "Frontalis (pars medialis)",
            "AU02": "Frontalis (pars lateralis)",
            "AU04": "Corrugator supercilii",
            "AU05": "Levator palpebrae superioris",
            "AU06": "Zygomaticus major",
            "AU07": "Orbicularis oculi (pars orbitalis)",
            "AU09": "Levator labii superioris alaeque nasi",
            "AU10": "Levator labii superioris",
            "AU12": "Zygomaticus major",
            "AU14": "Buccinator",
            "AU15": "Depressor anguli oris",
            "AU17": "Mentalis",
            "AU20": "Risorius",
            "AU23": "Orbicularis oris",
            "AU25": "Depressor labii inferioris",
            "AU26": "Depressor mandibulae",
            "AU45": "Orbicularis oculi (pars palpebralis)"
        }
        return muscle_groups.get(au_id, "Unknown")
    
    def _detect_emotions(self, landmarks) -> Dict[str, float]:
        """Detect emotions based on facial features"""
        emotions = {
            "happy": 0.0,
            "sad": 0.0,
            "angry": 0.0,
            "surprised": 0.0,
            "fearful": 0.0,
            "disgusted": 0.0,
            "neutral": 0.0
        }
        
        # Simplified emotion detection based on Action Units
        # In practice, this would use a trained model
        mouth_width = abs(landmarks[61].x - landmarks[291].x)
        mouth_height = abs(landmarks[0].y - landmarks[17].y)
        
        if mouth_width > 0.4 and mouth_height > 0.1:
            emotions["happy"] = 0.8
        elif mouth_width < 0.2 and mouth_height < 0.05:
            emotions["neutral"] = 0.9
        else:
            emotions["neutral"] = 0.6
        
        return emotions
    
    def _detect_micro_expressions(self, landmarks) -> List[MicroExpression]:
        """Detect micro-expressions"""
        # This would require temporal analysis across multiple frames
        # For now, return empty list
        return []
    
    def _analyze_posture(self, pose_landmarks) -> Dict[str, Any]:
        """Analyze body posture"""
        landmarks = pose_landmarks.landmark
        
        # Calculate head pose
        head_pose = {
            'pitch': self._calculate_head_pitch(landmarks),
            'yaw': self._calculate_head_yaw(landmarks),
            'roll': self._calculate_head_roll(landmarks)
        }
        
        # Calculate shoulder alignment
        shoulder_alignment = self._calculate_shoulder_alignment(landmarks)
        
        # Calculate spine curvature
        spine_curvature = self._calculate_spine_curvature(landmarks)
        
        # Overall posture score
        posture_score = self._calculate_posture_score(head_pose, shoulder_alignment, spine_curvature)
        
        posture_class = "good" if posture_score > 0.7 else "neutral" if posture_score > 0.4 else "poor"
        
        return {
            'posture': PostureAnalysis(
                head_pose=head_pose,
                shoulder_alignment=shoulder_alignment,
                spine_curvature=spine_curvature,
                overall_posture_score=posture_score,
                posture_class=posture_class
            )
        }
    
    def _calculate_head_pitch(self, landmarks) -> float:
        """Calculate head pitch angle"""
        # Simplified calculation
        nose_y = landmarks[0].y
        neck_y = landmarks[11].y  # Left shoulder
        return abs(nose_y - neck_y)
    
    def _calculate_head_yaw(self, landmarks) -> float:
        """Calculate head yaw angle"""
        nose_x = landmarks[0].x
        left_shoulder_x = landmarks[11].x
        right_shoulder_x = landmarks[12].x
        return abs(nose_x - (left_shoulder_x + right_shoulder_x) / 2)
    
    def _calculate_head_roll(self, landmarks) -> float:
        """Calculate head roll angle"""
        left_eye_y = landmarks[33].y
        right_eye_y = landmarks[263].y
        return abs(left_eye_y - right_eye_y)
    
    def _calculate_shoulder_alignment(self, landmarks) -> Dict[str, float]:
        """Calculate shoulder alignment"""
        left_shoulder = landmarks[11]
        right_shoulder = landmarks[12]
        
        return {
            'left_shoulder_height': left_shoulder.y,
            'right_shoulder_height': right_shoulder.y,
            'alignment_difference': abs(left_shoulder.y - right_shoulder.y)
        }
    
    def _calculate_spine_curvature(self, landmarks) -> float:
        """Calculate spine curvature"""
        # Simplified calculation using spine landmarks
        return 0.0
    
    def _calculate_posture_score(self, head_pose, shoulder_alignment, spine_curvature) -> float:
        """Calculate overall posture score"""
        # Combine different posture metrics
        head_score = 1.0 - min(head_pose['pitch'] + head_pose['yaw'] + head_pose['roll'], 1.0)
        shoulder_score = 1.0 - min(shoulder_alignment['alignment_difference'], 1.0)
        
        return (head_score + shoulder_score) / 2
    
    def _analyze_gestures(self, hand_landmarks_list) -> Dict[str, Any]:
        """Analyze hand gestures"""
        gestures = []
        
        for hand_landmarks in hand_landmarks_list:
            gesture_type = self._classify_gesture(hand_landmarks)
            if gesture_type:
                gestures.append(GestureAnalysis(
                    gesture_type=gesture_type,
                    confidence=0.8,
                    duration_ms=1000,  # Would be calculated in real implementation
                    frequency=1,
                    timestamp=datetime.now()
                ))
        
        return {'gestures': gestures}
    
    def _classify_gesture(self, hand_landmarks) -> Optional[str]:
        """Classify hand gesture"""
        # Simplified gesture classification
        # In practice, this would use more sophisticated algorithms
        return "hand_gesture"  # Placeholder
    
    def _analyze_eye_contact(self, face_results, frame_shape) -> Dict[str, Any]:
        """Analyze eye contact and gaze"""
        if not face_results.multi_face_landmarks:
            return {'eye_contact': None}
        
        face_landmarks = face_results.multi_face_landmarks[0]
        
        # Calculate gaze direction
        gaze_direction = self._calculate_gaze_direction(face_landmarks, frame_shape)
        
        # Calculate eye contact duration and blink rate
        eye_contact_duration = 1.0  # Would be calculated in real implementation
        blink_rate = 0.2  # Would be calculated in real implementation
        pupil_diameter = 0.05  # Would be calculated in real implementation
        focus_score = 0.8  # Would be calculated in real implementation
        
        return {
            'eye_contact': EyeContactAnalysis(
                gaze_direction=gaze_direction,
                eye_contact_duration=eye_contact_duration,
                blink_rate=blink_rate,
                pupil_diameter=pupil_diameter,
                focus_score=focus_score
            )
        }
    
    def _calculate_gaze_direction(self, face_landmarks, frame_shape) -> Dict[str, float]:
        """Calculate gaze direction"""
        # Simplified gaze calculation
        return {'x': 0.5, 'y': 0.5}  # Center of frame
    
    def _calculate_engagement_score(self, analysis_results) -> float:
        """Calculate overall engagement score"""
        scores = []
        
        # Posture score
        if 'posture' in analysis_results:
            scores.append(analysis_results['posture'].overall_posture_score)
        
        # Eye contact score
        if 'eye_contact' in analysis_results:
            scores.append(analysis_results['eye_contact'].focus_score)
        
        # Emotion consistency score
        if 'detected_emotions' in analysis_results:
            emotions = analysis_results['detected_emotions']
            dominant_emotion_score = max(emotions.values()) if emotions else 0.5
            scores.append(dominant_emotion_score)
        
        return np.mean(scores) if scores else 0.5
    
    def _generate_facs_recommendations(self, analysis_results) -> List[str]:
        """Generate FACS-based recommendations"""
        recommendations = []
        
        # Posture recommendations
        if 'posture' in analysis_results:
            posture = analysis_results['posture']
            if posture.posture_class == "poor":
                recommendations.append("Improve your posture by sitting up straight and keeping your shoulders back")
            elif posture.posture_class == "neutral":
                recommendations.append("Maintain good posture throughout the interview")
        
        # Eye contact recommendations
        if 'eye_contact' in analysis_results:
            eye_contact = analysis_results['eye_contact']
            if eye_contact.focus_score < 0.6:
                recommendations.append("Maintain better eye contact with the interviewer")
        
        # Gesture recommendations
        if 'gestures' in analysis_results and len(analysis_results['gestures']) > 0:
            recommendations.append("Use natural hand gestures to emphasize your points")
        
        return recommendations
    
    async def analyze_video(self, request: FACSAnalysisRequest) -> FACSAnalysisResponse:
        """Analyze pre-recorded video for comprehensive FACS analysis"""
        try:
            # This would process the entire video file
            # For now, return a placeholder response
            analysis_id = f"facs_{int(datetime.now().timestamp())}"
            
            # Process video frames (simplified for this example)
            frame_analysis = []
            emotion_timeline = {}
            posture_timeline = []
            gesture_timeline = []
            eye_contact_timeline = []
            micro_expression_timeline = []
            
            # Generate summary
            summary = {
                "engagement_score": 0.75,
                "emotion_consistency": 0.8,
                "posture_score": 0.7,
                "eye_contact_score": 0.85,
                "gesture_effectiveness": 0.6
            }
            
            # Generate recommendations using Gemini
            recommendations = await self._generate_advanced_recommendations(request)
            
            return FACSAnalysisResponse(
                analysis_id=analysis_id,
                video_metadata={"duration": 300, "resolution": "1920x1080"},
                summary=summary,
                detailed_analysis=FACSVideoAnalysis(
                    video_id=analysis_id,
                    total_frames=9000,
                    duration_seconds=300,
                    frame_analysis=frame_analysis,
                    emotion_timeline=emotion_timeline,
                    posture_timeline=posture_timeline,
                    gesture_timeline=gesture_timeline,
                    eye_contact_timeline=eye_contact_timeline,
                    micro_expression_timeline=micro_expression_timeline,
                    overall_performance_score=0.78,
                    recommendations=recommendations
                ),
                recommendations=recommendations,
                analysis_timestamp=datetime.now(),
                processing_time_ms=5000
            )
            
        except Exception as e:
            logger.error(f"Error in video analysis: {str(e)}")
            raise
    
    async def _generate_advanced_recommendations(self, request: FACSAnalysisRequest) -> List[str]:
        """Generate advanced recommendations using Gemini"""
        recommendations = []
        
        try:
            # Use Gemini for advanced analysis recommendations
            prompt = f"""
            Analyze this FACS video analysis request and provide specific recommendations:
            
            Target Focus: {request.target_focus}
            Analysis Duration: {request.analysis_duration}
            Confidence Threshold: {request.confidence_threshold}
            
            Provide recommendations for improving non-verbal communication during interviews.
            Focus on body language, facial expressions, and engagement techniques.
            """
            
            response = await self.gemini_model.generate_content_async(prompt)
            if response.text:
                recommendations = response.text.split('\n')
                recommendations = [rec.strip('- ') for rec in recommendations if rec.strip()]
        
        except Exception as e:
            logger.error(f"Error generating advanced recommendations: {str(e)}")
        
        return recommendations