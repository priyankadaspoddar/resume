import librosa
import numpy as np
import speech_recognition as sr
import asyncio
import logging
import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from google.generativeai import GenerativeModel
import google.generativeai as genai
from pydub import AudioSegment
import webrtcvad
import collections

from models.voice import (
    VoiceAnalysisRequest, VoiceAnalysisResponse, SpeechTranscript,
    SpeechFeatures, FillerWordAnalysis, ToneAnalysis, VoiceQualityMetrics,
    SpeechPatternAnalysis, VoiceFeedback, VoiceSession
)

logger = logging.getLogger(__name__)

class VoiceAnalyzer:
    """Voice Quality Engine for speech pattern and delivery analysis"""
    
    def __init__(self):
        self.vad = webrtcvad.Vad()
        self.vad.set_mode(3)  # Aggressive mode
        self.gemini_model = None
        self.filler_words = self._load_filler_words()
        self.tone_keywords = self._load_tone_keywords()
        
    async def initialize(self):
        """Initialize voice analysis components"""
        try:
            # Initialize Gemini model for advanced analysis
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            self.gemini_model = GenerativeModel('gemini-2.5-pro')
            
            logger.info("Voice Analyzer initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing voice analyzer: {str(e)}")
            raise
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.gemini_model:
            del self.gemini_model
    
    def _load_filler_words(self) -> List[str]:
        """Load common filler words and disfluencies"""
        return [
            "um", "uh", "like", "you know", "so", "well", "actually", "basically",
            "literally", "really", "just", "kind of", "sort of", "I mean", "you see",
            "right", "okay", "fine", "honestly", "frankly", "obviously", "clearly"
        ]
    
    def _load_tone_keywords(self) -> Dict[str, List[str]]:
        """Load tone-specific keywords for analysis"""
        return {
            "confident": ["definitely", "certainly", "absolutely", "without doubt", "clearly"],
            "enthusiastic": ["excited", "passionate", "love", "enjoy", "thrilled", "energetic"],
            "professional": ["respectfully", "appropriately", "suitably", "properly"],
            "nervous": ["maybe", "perhaps", "possibly", "I think", "I guess", "kind of"],
            "bored": ["whatever", "fine", "okay", "whatever you want"],
            "angry": ["frustrated", "annoyed", "upset", "disappointed", "terrible"]
        }
    
    async def analyze_speech(self, request: VoiceAnalysisRequest) -> VoiceAnalysisResponse:
        """Analyze speech patterns and voice quality"""
        start_time = datetime.now()
        
        try:
            # Load audio file
            audio_data, sample_rate = self._load_audio(request.audio_file)
            
            # Extract speech features
            speech_features = self._extract_speech_features(audio_data, sample_rate)
            
            # Perform speech-to-text if no transcript provided
            transcript = request.transcript
            if not transcript:
                transcript = await self._speech_to_text(request.audio_file, request.language_code)
            
            # Analyze filler words
            filler_analysis = self._analyze_filler_words(transcript)
            
            # Analyze tone
            tone_analysis = self._analyze_tone(transcript)
            
            # Analyze voice quality
            voice_quality = self._analyze_voice_quality(audio_data, sample_rate)
            
            # Calculate overall scores
            engagement_score = self._calculate_engagement_score(speech_features, filler_analysis, tone_analysis)
            clarity_score = self._calculate_clarity_score(speech_features, filler_analysis)
            confidence_score = self._calculate_confidence_score(tone_analysis, speech_features)
            
            # Generate recommendations
            recommendations = await self._generate_voice_recommendations(
                speech_features, filler_analysis, tone_analysis, voice_quality, request
            )
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return VoiceAnalysisResponse(
                analysis_id=f"voice_{int(start_time.timestamp())}",
                audio_metadata=self._get_audio_metadata(request.audio_file),
                transcript=SpeechTranscript(
                    text=transcript,
                    start_time=0.0,
                    end_time=len(audio_data) / sample_rate,
                    confidence=0.95,
                    speaker_id="user"
                ) if transcript else None,
                speech_analysis=SpeechPatternAnalysis(
                    speech_features=speech_features,
                    filler_word_analysis=filler_analysis,
                    tone_analysis=tone_analysis,
                    voice_quality=voice_quality,
                    engagement_score=engagement_score,
                    clarity_score=clarity_score,
                    confidence_score=confidence_score
                ),
                overall_score=np.mean([engagement_score, clarity_score, confidence_score]),
                recommendations=recommendations,
                analysis_timestamp=start_time,
                processing_time_ms=int(processing_time)
            )
            
        except Exception as e:
            logger.error(f"Error in voice analysis: {str(e)}")
            raise
    
    def _load_audio(self, audio_file: str) -> Tuple[np.ndarray, int]:
        """Load audio file and return data and sample rate"""
        try:
            # Load with librosa
            audio_data, sample_rate = librosa.load(audio_file, sr=None)
            return audio_data, sample_rate
        except Exception as e:
            logger.error(f"Error loading audio file: {str(e)}")
            raise
    
    def _extract_speech_features(self, audio_data: np.ndarray, sample_rate: int) -> SpeechFeatures:
        """Extract speech features using librosa"""
        # Pitch analysis
        f0, voiced_flag, _ = librosa.pyin(
            audio_data, 
            fmin=librosa.note_to_hz('C2'), 
            fmax=librosa.note_to_hz('C7')
        )
        
        # Remove unvoiced frames
        voiced_f0 = f0[voiced_flag > 0]
        
        pitch_mean = np.mean(voiced_f0) if len(voiced_f0) > 0 else 0
        pitch_std = np.std(voiced_f0) if len(voiced_f0) > 0 else 0
        pitch_min = np.min(voiced_f0) if len(voiced_f0) > 0 else 0
        pitch_max = np.max(voiced_f0) if len(voiced_f0) > 0 else 0
        
        # Energy analysis
        energy = librosa.feature.rms(y=audio_data)[0]
        energy_mean = np.mean(energy)
        energy_std = np.std(energy)
        energy_min = np.min(energy)
        energy_max = np.max(energy)
        
        # Speech rate
        speech_rate = self._calculate_speech_rate(audio_data, sample_rate)
        
        # Pause analysis
        pause_duration_mean, pause_duration_std, pause_count = self._analyze_pauses(audio_data, sample_rate)
        
        # Clarity and pronunciation scores
        clarity_score = self._calculate_clarity(audio_data, sample_rate)
        pronunciation_score = self._calculate_pronunciation(audio_data, sample_rate)
        
        return SpeechFeatures(
            pitch_mean=pitch_mean,
            pitch_std=pitch_std,
            pitch_min=pitch_min,
            pitch_max=pitch_max,
            energy_mean=energy_mean,
            energy_std=energy_std,
            energy_min=energy_min,
            energy_max=energy_max,
            speech_rate=speech_rate,
            pause_duration_mean=pause_duration_mean,
            pause_duration_std=pause_duration_std,
            pause_count=pause_count,
            clarity_score=clarity_score,
            pronunciation_score=pronunciation_score
        )
    
    def _calculate_speech_rate(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """Calculate speech rate in words per minute"""
        # Estimate number of words based on voiced segments
        # This is a simplified estimation
        duration = len(audio_data) / sample_rate
        voiced_frames = self._detect_voiced_segments(audio_data, sample_rate)
        estimated_words = len(voiced_frames) * 0.1  # Rough estimation
        return (estimated_words / duration) * 60 if duration > 0 else 0
    
    def _detect_voiced_segments(self, audio_data: np.ndarray, sample_rate: int) -> List[float]:
        """Detect voiced segments in audio"""
        frame_duration = 0.02  # 20ms frames
        frame_length = int(frame_duration * sample_rate)
        
        voiced_segments = []
        for i in range(0, len(audio_data) - frame_length, frame_length):
            frame = audio_data[i:i + frame_length]
            if self.vad.is_speech(frame.tobytes(), sample_rate):
                voiced_segments.append(i / sample_rate)
        
        return voiced_segments
    
    def _analyze_pauses(self, audio_data: np.ndarray, sample_rate: int) -> Tuple[float, float, int]:
        """Analyze pauses in speech"""
        voiced_segments = self._detect_voiced_segments(audio_data, sample_rate)
        
        if len(voiced_segments) < 2:
            return 0.0, 0.0, 0
        
        # Calculate pause durations
        pause_durations = []
        for i in range(1, len(voiced_segments)):
            pause_duration = voiced_segments[i] - voiced_segments[i-1]
            if pause_duration > 0.1:  # Only consider pauses longer than 100ms
                pause_durations.append(pause_duration)
        
        if not pause_durations:
            return 0.0, 0.0, 0
        
        return np.mean(pause_durations), np.std(pause_durations), len(pause_durations)
    
    def _calculate_clarity(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """Calculate speech clarity score"""
        # Use spectral features to assess clarity
        spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)[0]
        clarity_score = np.mean(spectral_centroids) / 1000  # Normalize
        return min(clarity_score, 1.0)
    
    def _calculate_pronunciation(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """Calculate pronunciation clarity score"""
        # Use zero-crossing rate as a proxy for pronunciation clarity
        zcr = librosa.feature.zero_crossing_rate(audio_data)[0]
        zcr_mean = np.mean(zcr)
        
        # Normalize and invert (lower ZCR generally indicates better pronunciation)
        pronunciation_score = 1.0 - min(zcr_mean * 10, 1.0)
        return pronunciation_score
    
    async def _speech_to_text(self, audio_file: str, language_code: str = "en-US") -> str:
        """Convert speech to text using Google Speech Recognition"""
        try:
            recognizer = sr.Recognizer()
            
            with sr.AudioFile(audio_file) as source:
                audio_data = recognizer.record(source)
            
            # Use Google Web Speech API
            text = recognizer.recognize_google(audio_data, language=language_code)
            return text
            
        except Exception as e:
            logger.error(f"Error in speech-to-text conversion: {str(e)}")
            return ""  # Return empty string if STT fails
    
    def _analyze_filler_words(self, transcript: str) -> FillerWordAnalysis:
        """Analyze filler words and disfluencies"""
        if not transcript:
            return FillerWordAnalysis(
                filler_words={},
                filler_word_rate=0.0,
                disfluency_count=0,
                disfluency_rate=0.0,
                common_fillers=[]
            )
        
        transcript_lower = transcript.lower()
        words = transcript_lower.split()
        
        # Count filler words
        filler_counts = {}
        for filler in self.filler_words:
            count = transcript_lower.count(filler)
            if count > 0:
                filler_counts[filler] = count
        
        # Calculate rates
        total_words = len(words)
        filler_word_rate = (sum(filler_counts.values()) / total_words * 100) if total_words > 0 else 0
        
        # Count disfluencies (repetitions, false starts)
        disfluency_count = self._count_disfluencies(transcript)
        disfluency_rate = (disfluency_count / (total_words / 100)) if total_words > 0 else 0
        
        # Get common fillers
        common_fillers = sorted(filler_counts.keys(), key=lambda x: filler_counts[x], reverse=True)[:5]
        
        return FillerWordAnalysis(
            filler_words=filler_counts,
            filler_word_rate=filler_word_rate,
            disfluency_count=disfluency_count,
            disfluency_rate=disfluency_rate,
            common_fillers=common_fillers
        )
    
    def _count_disfluencies(self, transcript: str) -> int:
        """Count disfluencies in transcript"""
        # Simple disfluency detection
        disfluency_patterns = [
            r'\b(i|i\'m|i am)\s+(i|i\'m|i am)\b',
            r'\b(um|uh|like)\s+(um|uh|like)\b',
            r'\b(so|well|actually)\s+(so|well|actually)\b'
        ]
        
        import re
        disfluency_count = 0
        for pattern in disfluency_patterns:
            matches = re.findall(pattern, transcript.lower())
            disfluency_count += len(matches)
        
        return disfluency_count
    
    def _analyze_tone(self, transcript: str) -> ToneAnalysis:
        """Analyze tone and emotional content"""
        if not transcript:
            return ToneAnalysis(
                tone_confidence={},
                dominant_tone="neutral",
                tone_variability=0.0,
                confidence_score=0.5,
                enthusiasm_score=0.5,
                professionalism_score=0.5
            )
        
        # Analyze tone keywords
        tone_scores = {}
        for tone, keywords in self.tone_keywords.items():
            score = 0
            for keyword in keywords:
                score += transcript.lower().count(keyword)
            tone_scores[tone] = score
        
        # Calculate confidence scores
        total_keywords = sum(tone_scores.values())
        tone_confidence = {}
        for tone, score in tone_scores.items():
            tone_confidence[tone] = score / total_keywords if total_keywords > 0 else 0
        
        # Determine dominant tone
        dominant_tone = max(tone_confidence, key=tone_confidence.get) if tone_confidence else "neutral"
        
        # Calculate variability
        tone_variability = np.std(list(tone_confidence.values())) if tone_confidence else 0.0
        
        # Calculate specific scores
        confidence_score = tone_confidence.get("confident", 0.0) + (1 - tone_confidence.get("nervous", 0.0))
        enthusiasm_score = tone_confidence.get("enthusiastic", 0.0)
        professionalism_score = tone_confidence.get("professional", 0.0) + (1 - tone_confidence.get("bored", 0.0))
        
        return ToneAnalysis(
            tone_confidence=tone_confidence,
            dominant_tone=dominant_tone,
            tone_variability=tone_variability,
            confidence_score=confidence_score,
            enthusiasm_score=enthusiasm_score,
            professionalism_score=professionalism_score
        )
    
    def _analyze_voice_quality(self, audio_data: np.ndarray, sample_rate: int) -> VoiceQualityMetrics:
        """Analyze voice quality metrics"""
        # Volume analysis
        volume = librosa.feature.rms(y=audio_data)[0]
        volume_mean = np.mean(volume)
        volume_std = np.std(volume)
        volume_range = np.max(volume) - np.min(volume)
        
        # Articulation rate
        articulation_rate = self._calculate_articulation_rate(audio_data, sample_rate)
        
        # Voice stability
        voice_stability = self._calculate_voice_stability(audio_data, sample_rate)
        
        # Breathiness score (simplified)
        breathiness_score = self._calculate_breathiness(audio_data, sample_rate)
        
        # Nasality score (simplified)
        nasality_score = self._calculate_nasality(audio_data, sample_rate)
        
        # Overall voice quality
        overall_quality = np.mean([
            volume_mean, voice_stability, (1 - breathiness_score), (1 - nasality_score)
        ])
        
        return VoiceQualityMetrics(
            volume_mean=volume_mean,
            volume_std=volume_std,
            volume_range=volume_range,
            articulation_rate=articulation_rate,
            voice_stability=voice_stability,
            breathiness_score=breathiness_score,
            nasality_score=nasality_score,
            overall_voice_quality=overall_quality
        )
    
    def _calculate_articulation_rate(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """Calculate articulation rate"""
        # Use zero-crossing rate as a proxy for articulation
        zcr = librosa.feature.zero_crossing_rate(audio_data)[0]
        return np.mean(zcr) * 1000  # Scale for readability
    
    def _calculate_voice_stability(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """Calculate voice stability (jitter and shimmer proxy)"""
        # Use pitch variation as stability measure
        f0, voiced_flag, _ = librosa.pyin(audio_data, fmin=80, fmax=400)
        voiced_f0 = f0[voiced_flag > 0]
        
        if len(voiced_f0) < 2:
            return 0.5
        
        # Calculate jitter (pitch variation)
        pitch_diffs = np.abs(np.diff(voiced_f0))
        jitter = np.mean(pitch_diffs) / np.mean(voiced_f0) if np.mean(voiced_f0) > 0 else 0
        
        # Stability is inverse of jitter
        return max(0, 1 - jitter)
    
    def _calculate_breathiness(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """Calculate breathiness score (0 = not breathy, 1 = very breathy)"""
        # Use spectral flatness as breathiness indicator
        spectral_flatness = librosa.feature.spectral_flatness(y=audio_data)[0]
        flatness_mean = np.mean(spectral_flatness)
        
        # Higher flatness indicates more noise (breathiness)
        return min(flatness_mean * 5, 1.0)
    
    def _calculate_nasality(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """Calculate nasality score (0 = not nasal, 1 = very nasal)"""
        # Use spectral centroid and bandwidth as nasality indicators
        spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)[0]
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio_data, sr=sample_rate)[0]
        
        centroid_mean = np.mean(spectral_centroids)
        bandwidth_mean = np.mean(spectral_bandwidth)
        
        # Nasal sounds tend to have lower centroids and specific bandwidth patterns
        nasality_score = 1.0 - (centroid_mean / 2000)  # Normalize
        return max(0, min(nasality_score, 1.0))
    
    def _calculate_engagement_score(self, speech_features: SpeechFeatures, 
                                  filler_analysis: FillerWordAnalysis, 
                                  tone_analysis: ToneAnalysis) -> float:
        """Calculate overall engagement score"""
        # Engagement factors
        pace_score = 1.0 - abs(speech_features.speech_rate - 150) / 150  # Optimal rate ~150 WPM
        pause_score = max(0, 1.0 - (filler_analysis.pause_duration_mean / 2.0))  # Optimal pause < 2s
        filler_score = max(0, 1.0 - (filler_analysis.filler_word_rate / 50))  # Max 50 filler words per 100
        tone_score = tone_analysis.confidence_score
        
        return np.mean([pace_score, pause_score, filler_score, tone_score])
    
    def _calculate_clarity_score(self, speech_features: SpeechFeatures, 
                               filler_analysis: FillerWordAnalysis) -> float:
        """Calculate speech clarity score"""
        clarity_base = speech_features.clarity_score
        pronunciation_score = speech_features.pronunciation_score
        filler_penalty = filler_analysis.filler_word_rate / 100
        
        return max(0, clarity_base + pronunciation_score - filler_penalty)
    
    def _calculate_confidence_score(self, tone_analysis: ToneAnalysis, 
                                  speech_features: SpeechFeatures) -> float:
        """Calculate confidence score"""
        tone_confidence = tone_analysis.confidence_score
        volume_confidence = min(speech_features.volume_mean * 10, 1.0)
        pace_confidence = 1.0 - abs(speech_features.speech_rate - 150) / 200
        
        return np.mean([tone_confidence, volume_confidence, pace_confidence])
    
    async def _generate_voice_recommendations(self, speech_features: SpeechFeatures,
                                            filler_analysis: FillerWordAnalysis,
                                            tone_analysis: ToneAnalysis,
                                            voice_quality: VoiceQualityMetrics,
                                            request: VoiceAnalysisRequest) -> List[str]:
        """Generate personalized voice recommendations using Gemini"""
        recommendations = []
        
        # Basic recommendations based on analysis
        if speech_features.speech_rate > 200:
            recommendations.append("Slow down your speech rate for better clarity")
        elif speech_features.speech_rate < 100:
            recommendations.append("Increase your speech rate to maintain engagement")
        
        if filler_analysis.filler_word_rate > 20:
            recommendations.append("Work on reducing filler words like 'um' and 'uh'")
        
        if tone_analysis.confidence_score < 0.5:
            recommendations.append("Practice speaking with more confidence and conviction")
        
        if voice_quality.overall_voice_quality < 0.6:
            recommendations.append("Work on improving your voice quality and projection")
        
        # Use Gemini for advanced recommendations
        try:
            prompt = f"""
            Analyze this voice quality analysis and provide specific recommendations:
            
            Speech Rate: {speech_features.speech_rate} WPM
            Filler Word Rate: {filler_analysis.filler_word_rate} per 100 words
            Confidence Score: {tone_analysis.confidence_score}
            Clarity Score: {speech_features.clarity_score}
            Voice Quality: {voice_quality.overall_voice_quality}
            
            Analysis Type: {request.analysis_type}
            Target Metrics: {request.target_metrics}
            
            Provide 3-5 actionable recommendations for improving speech delivery
            and voice quality for interview situations.
            """
            
            response = await self.gemini_model.generate_content_async(prompt)
            if response.text:
                gemini_recommendations = response.text.split('\n')
                recommendations.extend([rec.strip('- ') for rec in gemini_recommendations if rec.strip()])
        
        except Exception as e:
            logger.error(f"Error generating voice recommendations: {str(e)}")
        
        return recommendations[:10]  # Limit to 10 recommendations
    
    def _get_audio_metadata(self, audio_file: str) -> Dict[str, Any]:
        """Get audio file metadata"""
        try:
            audio = AudioSegment.from_file(audio_file)
            return {
                "duration_seconds": len(audio) / 1000,
                "sample_rate": audio.frame_rate,
                "channels": audio.channels,
                "bit_depth": audio.sample_width * 8
            }
        except Exception as e:
            logger.error(f"Error getting audio metadata: {str(e)}")
            return {}
    
    async def get_detailed_feedback(self, session_id: str) -> VoiceFeedback:
        """Get detailed voice quality feedback for a session"""
        # This would typically fetch from a database
        # For now, return a placeholder with comprehensive feedback
        return VoiceFeedback(
            session_id=session_id,
            strengths=[
                "Good vocal clarity and pronunciation",
                "Appropriate speech rate for the context",
                "Clear articulation in most sections"
            ],
            areas_for_improvement=[
                "Reduce filler word usage",
                "Work on maintaining consistent volume",
                "Improve confidence in delivery"
            ],
            specific_suggestions=[
                "Practice speaking without filler words by recording yourself",
                "Use breathing exercises to improve voice projection",
                "Focus on maintaining eye contact during speech"
            ],
            progress_metrics={
                "speech_rate_improvement": 0.15,
                "filler_word_reduction": 0.25,
                "confidence_increase": 0.10
            },
            practice_exercises=[
                "Tongue twisters for articulation",
                "Breathing exercises for voice control",
                "Mirror practice for confidence building"
            ],
            feedback_timestamp=datetime.now()
        )