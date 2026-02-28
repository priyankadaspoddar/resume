import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from google.generativeai import GenerativeModel
import google.generativeai as genai
import os

from models.interview import (
    InterviewSession, InterviewType, SessionStatus, QuestionCategory,
    InterviewQuestion, UserAnswer, QuestionFeedback, ResumeBasedFeedback,
    FACSFeedback, VoiceFeedback, ComprehensiveFeedback, InterviewSummary,
    PracticeRecommendation, InterviewProgress
)

from services.ner_ke import ResumeAnalyzer
from services.facs_analysis import FACSAnalyzer
from services.voice_engine import VoiceAnalyzer

logger = logging.getLogger(__name__)

class InterviewCoach:
    """Main interview coaching service that orchestrates all analysis components"""
    
    def __init__(self):
        self.resume_analyzer = ResumeAnalyzer()
        self.facs_analyzer = FACSAnalyzer()
        self.voice_analyzer = VoiceAnalyzer()
        self.gemini_model = None
        
        # In-memory storage for sessions (in production, use a database)
        self.sessions: Dict[str, InterviewSession] = {}
        self.user_progress: Dict[str, InterviewProgress] = {}
        
    async def initialize(self):
        """Initialize the interview coach and all sub-services"""
        try:
            # Initialize sub-services
            await self.resume_analyzer.initialize()
            await self.facs_analyzer.initialize()
            await self.voice_analyzer.initialize()
            
            # Initialize Gemini model for comprehensive analysis
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            self.gemini_model = GenerativeModel('gemini-2.5-pro')
            
            logger.info("Interview Coach initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing interview coach: {str(e)}")
            raise
    
    async def cleanup(self):
        """Cleanup all resources"""
        await self.resume_analyzer.cleanup()
        await self.facs_analyzer.cleanup()
        await self.voice_analyzer.cleanup()
        if self.gemini_model:
            del self.gemini_model
    
    async def start_session(self, resume_id: str, interview_type: InterviewType = InterviewType.PRACTICE) -> InterviewSession:
        """Start a new interview session"""
        session_id = f"session_{int(datetime.now().timestamp())}"
        
        # Create session
        session = InterviewSession(
            session_id=session_id,
            user_id="user_123",  # In production, get from auth
            resume_id=resume_id,
            interview_type=interview_type,
            start_time=datetime.now(),
            status=SessionStatus.ACTIVE,
            questions=[],
            user_answers=[],
            session_metadata={}
        )
        
        # Generate questions based on resume
        questions = await self._generate_session_questions(resume_id, interview_type)
        session.questions = questions
        
        # Store session
        self.sessions[session_id] = session
        
        # Update user progress
        await self._update_user_progress(session.user_id)
        
        return session
    
    async def _generate_session_questions(self, resume_id: str, interview_type: InterviewType) -> List[InterviewQuestion]:
        """Generate interview questions based on resume and session type"""
        # This would typically fetch resume analysis from database
        # For now, generate sample questions
        
        base_questions = [
            InterviewQuestion(
                question_id="q1",
                question_text="Tell me about yourself and your professional background.",
                category=QuestionCategory.BEHAVIORAL,
                difficulty="easy",
                expected_duration=120,
                related_skills=["communication", "self-presentation"],
                hints=["Focus on relevant experience", "Keep it concise but comprehensive"]
            ),
            InterviewQuestion(
                question_id="q2", 
                question_text="Describe a challenging project you worked on and how you overcame obstacles.",
                category=QuestionCategory.SITUATIONAL,
                difficulty="medium",
                expected_duration=180,
                related_skills=["problem-solving", "teamwork", "resilience"],
                hints=["Use STAR method", "Focus on your role and impact"]
            ),
            InterviewQuestion(
                question_id="q3",
                question_text="Why do you want to work for our company?",
                category=QuestionCategory.BEHAVIORAL,
                difficulty="medium",
                expected_duration=90,
                related_skills=["research", "motivation", "cultural fit"],
                hints=["Research the company", "Align with your values", "Be specific"]
            )
        ]
        
        # Add technical questions for technical interviews
        if interview_type == InterviewType.TECHNICAL:
            technical_questions = [
                InterviewQuestion(
                    question_id="q4",
                    question_text="Explain the difference between SQL and NoSQL databases.",
                    category=QuestionCategory.TECHNICAL,
                    difficulty="medium",
                    expected_duration=120,
                    related_skills=["database knowledge", "technical communication"],
                    hints=["Provide examples", "Discuss when to use each"]
                ),
                InterviewQuestion(
                    question_id="q5",
                    question_text="How would you optimize a slow-running query?",
                    category=QuestionCategory.TECHNICAL,
                    difficulty="hard",
                    expected_duration=180,
                    related_skills=["performance optimization", "problem-solving"],
                    hints=["Indexing", "Query structure", "Database design"]
                )
            ]
            base_questions.extend(technical_questions)
        
        return base_questions
    
    async def submit_answer(self, session_id: str, question_id: str, answer_text: str, 
                          answer_audio: Optional[str] = None, 
                          answer_video: Optional[str] = None) -> QuestionFeedback:
        """Submit an answer to a question and get feedback"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        
        # Create user answer record
        user_answer = UserAnswer(
            question_id=question_id,
            answer_text=answer_text,
            answer_audio=answer_audio,
            answer_video=answer_video,
            start_time=datetime.now(),
            end_time=datetime.now(),
            duration_seconds=len(answer_text.split()) / 150 * 60,  # Rough estimation
            transcript=answer_text
        )
        
        session.user_answers.append(user_answer)
        
        # Analyze the answer
        feedback = await self._analyze_answer(session, user_answer)
        
        return feedback
    
    async def _analyze_answer(self, session: InterviewSession, user_answer: UserAnswer) -> QuestionFeedback:
        """Analyze a user's answer using all available analysis components"""
        # Get the question
        question = next((q for q in session.questions if q.question_id == user_answer.question_id), None)
        if not question:
            raise ValueError(f"Question {user_answer.question_id} not found in session")
        
        # Analyze content quality
        content_score = await self._analyze_answer_content(user_answer.answer_text, question)
        
        # Analyze structure and relevance
        structure_score = self._analyze_answer_structure(user_answer.answer_text)
        relevance_score = self._analyze_answer_relevance(user_answer.answer_text, question)
        
        # Analyze confidence (if voice/video available)
        confidence_score = 0.5
        if user_answer.answer_audio:
            voice_analysis = await self.voice_analyzer.analyze_speech(
                # Create a mock request for voice analysis
                type('VoiceRequest', (), {
                    'audio_file': user_answer.answer_audio,
                    'transcript': user_answer.transcript,
                    'analysis_type': 'basic',
                    'target_metrics': ['confidence'],
                    'language_code': 'en-US'
                })()
            )
            confidence_score = voice_analysis.speech_analysis.confidence_score
        
        # Analyze communication skills
        communication_score = self._analyze_communication_skills(user_answer.answer_text)
        
        # Calculate overall score
        overall_score = np.mean([content_score, structure_score, relevance_score, confidence_score, communication_score])
        
        # Generate feedback
        strengths, improvements, specific_feedback, suggestions = await self._generate_answer_feedback(
            user_answer.answer_text, question, overall_score
        )
        
        # Calculate score breakdown
        score_breakdown = {
            "content": content_score,
            "structure": structure_score,
            "relevance": relevance_score,
            "confidence": confidence_score,
            "communication": communication_score
        }
        
        return QuestionFeedback(
            question_id=user_answer.question_id,
            answer_quality=type('AnswerQuality', (), {
                'content_score': content_score,
                'structure_score': structure_score,
                'relevance_score': relevance_score,
                'confidence_score': confidence_score,
                'communication_score': communication_score,
                'overall_score': overall_score
            })(),
            strengths=strengths,
            areas_for_improvement=improvements,
            specific_feedback=specific_feedback,
            suggested_improvements=suggestions,
            score_breakdown=score_breakdown
        )
    
    async def _analyze_answer_content(self, answer_text: str, question: InterviewQuestion) -> float:
        """Analyze the content quality of an answer"""
        # Use Gemini to analyze content quality
        prompt = f"""
        Analyze this interview answer for content quality:
        
        Question: {question.question_text}
        Answer: {answer_text}
        
        Rate the content quality on a scale of 0-1 based on:
        1. Completeness of response
        2. Relevance to the question
        3. Depth of knowledge demonstrated
        4. Use of specific examples
        
        Provide a score and brief explanation.
        """
        
        try:
            response = await self.gemini_model.generate_content_async(prompt)
            if response.text:
                # Extract score from response (simplified parsing)
                # In production, use proper structured output
                return 0.8  # Placeholder
        except Exception as e:
            logger.error(f"Error analyzing answer content: {str(e)}")
        
        return 0.5  # Default score
    
    def _analyze_answer_structure(self, answer_text: str) -> float:
        """Analyze the structure and organization of an answer"""
        # Check for proper structure (introduction, body, conclusion)
        words = answer_text.lower().split()
        length = len(words)
        
        # Optimal length range
        if 50 <= length <= 300:
            structure_score = 0.8
        elif 20 <= length <= 500:
            structure_score = 0.6
        else:
            structure_score = 0.3
        
        # Check for transition words
        transition_words = ["first", "second", "finally", "additionally", "moreover", "however"]
        transition_count = sum(1 for word in words if word in transition_words)
        transition_score = min(transition_count / 5, 1.0)
        
        return (structure_score + transition_score) / 2
    
    def _analyze_answer_relevance(self, answer_text: str, question: InterviewQuestion) -> float:
        """Analyze how relevant the answer is to the question"""
        # Simple keyword matching for relevance
        question_keywords = set(question.question_text.lower().split())
        answer_keywords = set(answer_text.lower().split())
        
        # Calculate overlap
        if not question_keywords:
            return 0.5
        
        overlap = len(question_keywords.intersection(answer_keywords))
        relevance_score = overlap / len(question_keywords)
        
        return min(relevance_score, 1.0)
    
    def _analyze_communication_skills(self, answer_text: str) -> float:
        """Analyze communication and presentation skills"""
        # Check for clear language
        unclear_words = ["um", "uh", "like", "you know", "basically"]
        unclear_count = sum(answer_text.lower().count(word) for word in unclear_words)
        
        # Check sentence structure
        sentences = answer_text.split('.')
        avg_sentence_length = np.mean([len(s.split()) for s in sentences if s.strip()]) if sentences else 0
        
        # Communication score
        clarity_penalty = unclear_count / len(answer_text.split()) if answer_text.split() else 0
        structure_score = 1.0 if 10 <= avg_sentence_length <= 25 else 0.7
        
        return max(0, structure_score - clarity_penalty)
    
    async def _generate_answer_feedback(self, answer_text: str, question: InterviewQuestion, 
                                      overall_score: float) -> tuple:
        """Generate comprehensive feedback for an answer"""
        strengths = []
        improvements = []
        specific_feedback = ""
        suggestions = []
        
        # Content-based feedback
        if overall_score >= 0.8:
            strengths.append("Excellent content and thorough response")
            specific_feedback = "Your answer demonstrates strong knowledge and provides comprehensive coverage of the topic."
        elif overall_score >= 0.6:
            strengths.append("Good effort with relevant points")
            improvements.append("Could benefit from more specific examples")
            specific_feedback = "Your answer covers the main points but could be strengthened with more concrete examples."
        else:
            improvements.append("Needs significant improvement in content")
            improvements.append("Answer lacks depth and specificity")
            specific_feedback = "Your answer is too general and lacks the depth expected for this question."
        
        # Generate specific suggestions using Gemini
        try:
            prompt = f"""
            Provide specific suggestions for improving this interview answer:
            
            Question: {question.question_text}
            Answer: {answer_text}
            Current Score: {overall_score}
            
            Provide 2-3 specific, actionable suggestions for improvement.
            """
            
            response = await self.gemini_model.generate_content_async(prompt)
            if response.text:
                suggestions = response.text.split('\n')[:3]
        
        except Exception as e:
            logger.error(f"Error generating answer feedback: {str(e)}")
        
        return strengths, improvements, specific_feedback, suggestions
    
    async def get_session_feedback(self, session_id: str) -> ComprehensiveFeedback:
        """Get comprehensive feedback for an entire interview session"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        
        # Complete session
        session.status = SessionStatus.COMPLETED
        session.end_time = datetime.now()
        session.total_duration = int((session.end_time - session.start_time).total_seconds())
        
        # Analyze all answers
        question_feedback = []
        total_score = 0
        
        for user_answer in session.user_answers:
            feedback = await self._analyze_answer(session, user_answer)
            question_feedback.append(feedback)
            total_score += feedback.answer_quality.overall_score
        
        average_score = total_score / len(session.user_answers) if session.user_answers else 0
        
        # Generate comprehensive feedback
        resume_feedback = await self._generate_resume_feedback(session.resume_id, session.user_answers)
        facs_feedback = await self._generate_facs_feedback(session.user_answers)
        voice_feedback = await self._generate_voice_feedback(session.user_answers)
        
        # Get overall strengths and improvements
        overall_strengths, critical_improvements, personalized_recommendations = await self._generate_overall_feedback(
            question_feedback, resume_feedback, facs_feedback, voice_feedback
        )
        
        # Calculate progress tracking
        progress_tracking = await self._calculate_progress_tracking(session.user_id, average_score)
        
        # Get next steps
        next_steps = await self._generate_next_steps(session.user_id, critical_improvements)
        
        return ComprehensiveFeedback(
            overall_score=average_score,
            resume_feedback=resume_feedback,
            facs_feedback=facs_feedback,
            voice_feedback=voice_feedback,
            question_feedback=question_feedback,
            overall_strengths=overall_strengths,
            critical_improvements=critical_improvements,
            personalized_recommendations=personalized_recommendations,
            progress_tracking=progress_tracking,
            next_steps=next_steps
        )
    
    async def _generate_resume_feedback(self, resume_id: str, user_answers: List[UserAnswer]) -> ResumeBasedFeedback:
        """Generate feedback based on resume analysis and answers"""
        # This would typically fetch resume analysis from database
        # For now, return placeholder feedback
        return ResumeBasedFeedback(
            resume_id=resume_id,
            question_relevance=0.8,
            skill_alignment=0.7,
            experience_validation=0.9,
            gap_analysis=["Consider adding more technical project details"],
            strength_validation=["Strong communication skills demonstrated"]
        )
    
    async def _generate_facs_feedback(self, user_answers: List[UserAnswer]) -> FACSFeedback:
        """Generate FACS-based feedback from video answers"""
        # This would analyze video answers for non-verbal communication
        # For now, return placeholder feedback
        return FACSFeedback(
            engagement_score=0.75,
            emotion_consistency=0.8,
            posture_score=0.7,
            eye_contact_score=0.85,
            gesture_effectiveness=0.6,
            micro_expression_insights=["Good eye contact maintained"],
            non_verbal_recommendations=["Use more natural hand gestures"]
        )
    
    async def _generate_voice_feedback(self, user_answers: List[UserAnswer]) -> VoiceFeedback:
        """Generate voice quality feedback from audio answers"""
        # This would analyze audio answers for voice quality
        # For now, return placeholder feedback
        return VoiceFeedback(
            session_id=user_answers[0].question_id if user_answers else "unknown",
            strengths=["Clear pronunciation", "Good volume control"],
            areas_for_improvement=["Reduce filler words", "Improve speech rate"],
            specific_suggestions=["Practice breathing techniques", "Record yourself speaking"],
            progress_metrics={"speech_rate_improvement": 0.15},
            practice_exercises=["Tongue twisters", "Breathing exercises"],
            feedback_timestamp=datetime.now()
        )
    
    async def _generate_overall_feedback(self, question_feedback: List[QuestionFeedback],
                                       resume_feedback: ResumeBasedFeedback,
                                       facs_feedback: FACSFeedback,
                                       voice_feedback: VoiceFeedback) -> tuple:
        """Generate overall session feedback"""
        # Collect strengths
        strengths = []
        for feedback in question_feedback:
            strengths.extend(feedback.strengths)
        strengths.extend(resume_feedback.strength_validation)
        
        # Collect improvements
        improvements = []
        for feedback in question_feedback:
            improvements.extend(feedback.areas_for_improvement)
        improvements.extend(resume_feedback.gap_analysis)
        improvements.extend(facs_feedback.non_verbal_recommendations)
        improvements.extend(voice_feedback.areas_for_improvement)
        
        # Generate personalized recommendations using Gemini
        recommendations = []
        try:
            prompt = f"""
            Based on this interview session analysis, provide personalized recommendations:
            
            Question Feedback Count: {len(question_feedback)}
            Resume Feedback: {resume_feedback.gap_analysis}
            FACS Feedback: {facs_feedback.non_verbal_recommendations}
            Voice Feedback: {voice_feedback.areas_for_improvement}
            
            Provide 3-5 personalized recommendations for interview improvement.
            """
            
            response = await self.gemini_model.generate_content_async(prompt)
            if response.text:
                recommendations = response.text.split('\n')[:5]
        
        except Exception as e:
            logger.error(f"Error generating overall feedback: {str(e)}")
        
        return strengths, improvements, recommendations
    
    async def _calculate_progress_tracking(self, user_id: str, current_score: float) -> Dict[str, float]:
        """Calculate user progress over time"""
        if user_id not in self.user_progress:
            self.user_progress[user_id] = InterviewProgress(
                user_id=user_id,
                total_sessions=0,
                average_score=0.0,
                best_score=0.0,
                worst_score=0.0,
                progress_timeline=[],
                skill_improvement={},
                last_session_date=None
            )
        
        progress = self.user_progress[user_id]
        progress.total_sessions += 1
        progress.last_session_date = datetime.now()
        
        # Update scores
        if progress.best_score == 0 or current_score > progress.best_score:
            progress.best_score = current_score
        if progress.worst_score == 0 or current_score < progress.worst_score:
            progress.worst_score = current_score
        
        # Calculate average
        all_scores = [current_score] + [entry.get('score', 0) for entry in progress.progress_timeline]
        progress.average_score = sum(all_scores) / len(all_scores)
        
        # Add to timeline
        progress.progress_timeline.append({
            'session_date': datetime.now().isoformat(),
            'score': current_score,
            'improvement': current_score - progress.average_score
        })
        
        # Calculate skill improvements
        progress.skill_improvement = {
            'communication': 0.1,
            'technical_knowledge': 0.05,
            'confidence': 0.15
        }
        
        return progress.skill_improvement
    
    async def _generate_next_steps(self, user_id: str, critical_improvements: List[str]) -> List[str]:
        """Generate next steps for user improvement"""
        next_steps = []
        
        # Generate practice recommendations
        for improvement in critical_improvements[:3]:
            next_steps.append(f"Practice addressing: {improvement}")
        
        # Add general recommendations
        next_steps.extend([
            "Review common interview questions for your industry",
            "Practice with a friend or mentor",
            "Record yourself answering questions",
            "Focus on body language and eye contact"
        ])
        
        return next_steps
    
    async def get_session_summary(self, session_id: str) -> InterviewSummary:
        """Get a summary of the interview session"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        
        # Calculate metrics
        total_questions = len(session.questions)
        answered_questions = len(session.user_answers)
        completion_rate = answered_questions / total_questions if total_questions > 0 else 0
        
        # Calculate average question score
        if session.user_answers:
            avg_score = np.mean([0.7 for _ in session.user_answers])  # Placeholder
        else:
            avg_score = 0.0
        
        # Determine strongest and weakest categories
        strongest_category = "Communication"
        weakest_category = "Technical Knowledge"
        
        # Calculate time efficiency
        expected_time = sum(q.expected_duration for q in session.questions) / 60  # in minutes
        actual_time = session.total_duration / 60 if session.total_duration else 0
        time_efficiency = actual_time / expected_time if expected_time > 0 else 1.0
        
        # Generate key insights
        key_insights = [
            "Strong communication skills demonstrated",
            "Good understanding of fundamental concepts",
            "Needs improvement in technical depth"
        ]
        
        # Improvement priority
        improvement_priority = [
            "Deepen technical knowledge in key areas",
            "Practice more complex problem-solving scenarios",
            "Work on concise and structured responses"
        ]
        
        return InterviewSummary(
            session_id=session_id,
            overall_score=avg_score,
            average_question_score=avg_score,
            strongest_category=strongest_category,
            weakest_category=weakest_category,
            time_efficiency=time_efficiency,
            completion_rate=completion_rate,
            key_insights=key_insights,
            improvement_priority=improvement_priority,
            summary_timestamp=datetime.now()
        )
    
    async def get_user_progress(self, user_id: str) -> InterviewProgress:
        """Get user's overall progress and statistics"""
        if user_id not in self.user_progress:
            return InterviewProgress(
                user_id=user_id,
                total_sessions=0,
                average_score=0.0,
                best_score=0.0,
                worst_score=0.0,
                progress_timeline=[],
                skill_improvement={},
                last_session_date=None
            )
        
        return self.user_progress[user_id]
    
    async def get_practice_recommendation(self, user_id: str) -> PracticeRecommendation:
        """Get personalized practice recommendation for user"""
        progress = await self.get_user_progress(user_id)
        
        # Determine focus area based on progress
        if progress.average_score < 0.5:
            focus_area = "Fundamentals"
            difficulty_level = "beginner"
            estimated_time = 30
        elif progress.average_score < 0.7:
            focus_area = "Intermediate Skills"
            difficulty_level = "intermediate"
            estimated_time = 45
        else:
            focus_area = "Advanced Techniques"
            difficulty_level = "advanced"
            estimated_time = 60
        
        # Generate exercises
        exercises = [
            "Review common interview questions",
            "Practice with timed responses",
            "Work on body language and eye contact"
        ]
        
        # Calculate expected improvement
        expected_improvement = 0.1 if progress.average_score < 0.7 else 0.05
        
        # Generate resources
        resources = [
            "Interview preparation guide",
            "Common questions database",
            "Practice session recordings"
        ]
        
        return PracticeRecommendation(
            focus_area=focus_area,
            recommended_exercises=exercises,
            estimated_time=estimated_time,
            difficulty_level=difficulty_level,
            priority=3,
            expected_improvement=expected_improvement,
            resources=resources
        )