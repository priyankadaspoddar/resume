import os
import re
import spacy
import pdfplumber
import docx
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging
from collections import defaultdict
import asyncio
from google.generativeai import GenerativeModel
import google.generativeai as genai

from models.resume import (
    ResumeAnalysisRequest, ResumeAnalysisResponse, PersonalInfo, EducationEntry,
    WorkExperienceEntry, SkillCategory, ProjectEntry, CertificationEntry,
    InterviewQuestion, QuestionsResponse
)

logger = logging.getLogger(__name__)

class ResumeAnalyzer:
    """NER-KE Algorithm v2.0 for Resume Analysis"""
    
    def __init__(self):
        self.nlp = None
        self.gemini_model = None
        self.skill_patterns = self._load_skill_patterns()
        self.job_title_patterns = self._load_job_title_patterns()
        self.industry_keywords = self._load_industry_keywords()
        
    async def initialize(self):
        """Initialize the resume analyzer with required models"""
        try:
            # Load spaCy model
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("spaCy model loaded successfully")
            
            # Initialize Gemini model
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            self.gemini_model = GenerativeModel('gemini-2.5-pro')
            logger.info("Gemini model initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing resume analyzer: {str(e)}")
            raise
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.nlp:
            del self.nlp
        if self.gemini_model:
            del self.gemini_model
    
    def _load_skill_patterns(self) -> Dict[str, List[str]]:
        """Load skill patterns for different categories"""
        return {
            "programming_languages": [
                "python", "java", "javascript", "c++", "c#", "ruby", "go", "rust",
                "typescript", "php", "swift", "kotlin", "scala", "r", "matlab"
            ],
            "frameworks": [
                "react", "angular", "vue", "django", "flask", "spring", "node.js",
                "express", "laravel", "ruby on rails", "asp.net", "flask", "fastapi"
            ],
            "databases": [
                "mysql", "postgresql", "mongodb", "redis", "oracle", "sql server",
                "sqlite", "cassandra", "elasticsearch", "dynamodb", "neo4j"
            ],
            "cloud_platforms": [
                "aws", "azure", "google cloud", "gcp", "docker", "kubernetes",
                "terraform", "ansible", "jenkins", "gitlab ci", "github actions"
            ],
            "soft_skills": [
                "communication", "leadership", "teamwork", "problem-solving",
                "analytical thinking", "creativity", "adaptability", "time management"
            ]
        }
    
    def _load_job_title_patterns(self) -> List[str]:
        """Load common job title patterns"""
        return [
            r"(?i)software.*engineer", r"(?i)senior.*developer", r"(?i)frontend.*developer",
            r"(?i)backend.*developer", r"(?i)full.*stack.*developer", r"(?i)data.*scientist",
            r"(?i)machine.*learning.*engineer", r"(?i)devops.*engineer", r"(?i)cloud.*engineer",
            r"(?i)product.*manager", r"(?i)project.*manager", r"(?i)business.*analyst"
        ]
    
    def _load_industry_keywords(self) -> Dict[str, List[str]]:
        """Load industry-specific keywords"""
        return {
            "technology": ["software", "development", "programming", "coding", "algorithm"],
            "finance": ["financial", "banking", "investment", "trading", "risk management"],
            "healthcare": ["medical", "healthcare", "clinical", "patient care", "health"],
            "education": ["teaching", "education", "academic", "curriculum", "instruction"],
            "marketing": ["marketing", "branding", "digital marketing", "social media", "campaign"]
        }
    
    async def analyze_resume(self, content: bytes, filename: str, request: ResumeAnalysisRequest) -> ResumeAnalysisResponse:
        """Main resume analysis function using NER-KE Algorithm v2.0"""
        start_time = datetime.now()
        
        try:
            # Extract text from resume
            text = self._extract_text(content, filename)
            
            # Initialize analysis results
            analysis_id = f"resume_{int(start_time.timestamp())}"
            
            # Perform NER and KE analysis
            personal_info = self._extract_personal_info(text)
            education = self._extract_education(text)
            work_experience = self._extract_work_experience(text)
            skills = self._extract_skills(text, request.analysis_depth)
            projects = self._extract_projects(text)
            certifications = self._extract_certifications(text)
            
            # Generate keywords and entities
            keywords = self._extract_keywords(text, request.analysis_depth)
            entities = self._extract_entities(text)
            
            # Calculate quality score
            quality_score = self._calculate_quality_score(text, personal_info, work_experience, education, skills)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                text, personal_info, work_experience, education, skills, request
            )
            
            # Generate interview questions if requested
            questions = []
            if request.generate_questions:
                questions = await self._generate_interview_questions(
                    text, personal_info, work_experience, education, skills, request
                )
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return ResumeAnalysisResponse(
                resume_id=analysis_id,
                metadata=self._create_metadata(filename, len(content), len(text)),
                personal_info=personal_info,
                education=education,
                work_experience=work_experience,
                skills=skills,
                projects=projects,
                certifications=certifications,
                extracted_keywords=keywords,
                entities=entities,
                quality_score=quality_score,
                recommendations=recommendations,
                analysis_timestamp=start_time,
                processing_time_ms=int(processing_time)
            )
            
        except Exception as e:
            logger.error(f"Error in resume analysis: {str(e)}")
            raise
    
    def _extract_text(self, content: bytes, filename: str) -> str:
        """Extract text from different file formats"""
        if filename.lower().endswith('.pdf'):
            return self._extract_text_from_pdf(content)
        elif filename.lower().endswith('.docx'):
            return self._extract_text_from_docx(content)
        elif filename.lower().endswith('.txt'):
            return content.decode('utf-8', errors='ignore')
        else:
            raise ValueError(f"Unsupported file format: {filename}")
    
    def _extract_text_from_pdf(self, content: bytes) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with pdfplumber.open(content) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise
        return text
    
    def _extract_text_from_docx(self, content: bytes) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(content)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {str(e)}")
            raise
    
    def _extract_personal_info(self, text: str) -> PersonalInfo:
        """Extract personal information using NER"""
        doc = self.nlp(text)
        
        personal_info = PersonalInfo()
        
        # Extract name (usually at the beginning)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                if not personal_info.name:
                    personal_info.name = ent.text
                break
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            personal_info.email = emails[0]
        
        # Extract phone
        phone_pattern = r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, text)
        if phones:
            personal_info.phone = phones[0]
        
        # Extract location
        for ent in doc.ents:
            if ent.label_ in ["GPE", "LOC"]:
                if not personal_info.location:
                    personal_info.location = ent.text
                break
        
        # Extract LinkedIn/GitHub
        linkedin_pattern = r'linkedin\.com/in/([a-zA-Z0-9_-]+)'
        github_pattern = r'github\.com/([a-zA-Z0-9_-]+)'
        
        linkedin_matches = re.findall(linkedin_pattern, text)
        if linkedin_matches:
            personal_info.linkedin = f"https://linkedin.com/in/{linkedin_matches[0]}"
        
        github_matches = re.findall(github_pattern, text)
        if github_matches:
            personal_info.github = f"https://github.com/{github_matches[0]}"
        
        return personal_info
    
    def _extract_education(self, text: str) -> List[EducationEntry]:
        """Extract education information"""
        education_entries = []
        
        # Common degree patterns
        degree_patterns = [
            r"(?i)(.*?)(?:degree|bachelor|master|ph\.?d|doctorate).*?in\s+([a-zA-Z\s]+?)(?:\s+from|\s+at|\s*,|\s*\n)",
            r"(?i)([a-zA-Z\s]+?)\s+(?:degree|bachelor|master|ph\.?d)\s+in\s+([a-zA-Z\s]+?)(?:\s+from|\s+at|\s*,|\s*\n)"
        ]
        
        for pattern in degree_patterns:
            matches = re.findall(pattern, text, re.MULTILINE | re.DOTALL)
            for match in matches:
                institution = match[0].strip() if len(match) > 0 else ""
                degree = match[1].strip() if len(match) > 1 else ""
                
                if institution and degree:
                    education_entries.append(EducationEntry(
                        institution=institution,
                        degree=degree,
                        field_of_study="",
                        start_date="",
                        end_date="",
                        gpa="",
                        achievements=[]
                    ))
        
        return education_entries
    
    def _extract_work_experience(self, text: str) -> List[WorkExperienceEntry]:
        """Extract work experience using job title patterns"""
        work_entries = []
        
        # Find job titles and companies
        for pattern in self.job_title_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                job_title = match.group(0)
                
                # Look for company name near job title
                context_start = max(0, match.start() - 200)
                context_end = min(len(text), match.end() + 200)
                context = text[context_start:context_end]
                
                # Extract company
                company_pattern = r"(?i)(?:at|for|with)\s+([A-Z][a-zA-Z\s&\.]+?)(?:\s|,|\n|\.|$)"
                company_matches = re.findall(company_pattern, context)
                company = company_matches[0] if company_matches else ""
                
                # Extract duration
                duration_pattern = r"(?i)(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s*\d{4}\s*[-–]\s*(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)?\s*\d{4}?"
                duration_matches = re.findall(duration_pattern, context, re.IGNORECASE)
                duration = duration_matches[0] if duration_matches else ""
                
                if company:
                    work_entries.append(WorkExperienceEntry(
                        company=company,
                        job_title=job_title,
                        start_date=duration,
                        end_date="",
                        location="",
                        description="",
                        achievements=[],
                        technologies=[]
                    ))
        
        return work_entries
    
    def _extract_skills(self, text: str, analysis_depth: str) -> List[SkillCategory]:
        """Extract skills using keyword extraction"""
        skill_categories = []
        
        for category, skills in self.skill_patterns.items():
            found_skills = []
            for skill in skills:
                if re.search(rf'\b{skill}\b', text, re.IGNORECASE):
                    found_skills.append(skill)
            
            if found_skills:
                proficiency = "advanced" if analysis_depth == "advanced" else "intermediate"
                skill_categories.append(SkillCategory(
                    category=category,
                    skills=found_skills,
                    proficiency_level=proficiency
                ))
        
        return skill_categories
    
    def _extract_projects(self, text: str) -> List[ProjectEntry]:
        """Extract project information"""
        projects = []
        
        # Look for project sections
        project_patterns = [
            r"(?i)project.*?(?:\n|\r\n)(.*?)(?=\n\n|\r\n\r\n|experience|education|$)",
            r"(?i)portfolio.*?(?:\n|\r\n)(.*?)(?=\n\n|\r\n\r\n|experience|education|$)"
        ]
        
        for pattern in project_patterns:
            matches = re.findall(pattern, text, re.MULTILINE | re.DOTALL)
            for match in matches:
                project_text = match.strip()
                if len(project_text) > 50:  # Filter out short matches
                    projects.append(ProjectEntry(
                        name="Project",
                        description=project_text[:200],
                        technologies=[],
                        role="",
                        duration="",
                        achievements=[]
                    ))
        
        return projects
    
    def _extract_certifications(self, text: str) -> List[CertificationEntry]:
        """Extract certification information"""
        certifications = []
        
        # Common certification patterns
        cert_patterns = [
            r"(?i)(?:certified|certification).*?(?:in|for)\s+([a-zA-Z\s]+?)(?:\s+from|\s+by|\s*,|\s*\n)",
            r"(?i)([a-zA-Z\s]+?)(?:certified|certification)"
        ]
        
        for pattern in cert_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                cert_name = match.strip()
                if cert_name and len(cert_name) > 5:
                    certifications.append(CertificationEntry(
                        name=cert_name,
                        issuing_organization="",
                        issue_date="",
                        expiration_date="",
                        credential_id=""
                    ))
        
        return certifications
    
    def _extract_keywords(self, text: str, analysis_depth: str) -> List[str]:
        """Extract keywords using TF-IDF and domain-specific patterns"""
        # Simple keyword extraction for now
        doc = self.nlp(text.lower())
        
        # Extract nouns and proper nouns
        keywords = []
        for token in doc:
            if token.pos_ in ["NOUN", "PROPN"] and len(token.text) > 3:
                keywords.append(token.text)
        
        # Remove duplicates and sort by frequency
        keyword_freq = defaultdict(int)
        for keyword in keywords:
            keyword_freq[keyword] += 1
        
        sorted_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)
        return [kw for kw, freq in sorted_keywords[:20]]
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities using spaCy"""
        doc = self.nlp(text)
        
        entities = defaultdict(list)
        for ent in doc.ents:
            entities[ent.label_].append(ent.text)
        
        # Remove duplicates
        for label in entities:
            entities[label] = list(set(entities[label]))
        
        return dict(entities)
    
    def _calculate_quality_score(self, text: str, personal_info: PersonalInfo, 
                               work_experience: List[WorkExperienceEntry],
                               education: List[EducationEntry], skills: List[SkillCategory]) -> float:
        """Calculate overall resume quality score"""
        score = 0.0
        
        # Length score (optimal length)
        word_count = len(text.split())
        if 300 <= word_count <= 800:
            score += 20
        elif 200 <= word_count <= 1200:
            score += 10
        
        # Personal info completeness
        personal_fields = [personal_info.name, personal_info.email, personal_info.phone]
        personal_complete = sum(1 for field in personal_fields if field)
        score += (personal_complete / 3) * 15
        
        # Experience completeness
        if work_experience:
            score += 20
        
        # Education completeness
        if education:
            score += 15
        
        # Skills diversity
        total_skills = sum(len(skill.skills) for skill in skills)
        if total_skills >= 10:
            score += 20
        elif total_skills >= 5:
            score += 10
        
        return min(score, 100.0)
    
    async def _generate_recommendations(self, text: str, personal_info: PersonalInfo,
                                      work_experience: List[WorkExperienceEntry],
                                      education: List[EducationEntry], skills: List[SkillCategory],
                                      request: ResumeAnalysisRequest) -> List[str]:
        """Generate personalized recommendations using Gemini"""
        recommendations = []
        
        # Basic recommendations based on analysis
        if not personal_info.email:
            recommendations.append("Add a professional email address to your contact information")
        
        if len(work_experience) < 2:
            recommendations.append("Consider adding more work experience details or relevant projects")
        
        if len(skills) < 3:
            recommendations.append("Expand your skills section with more technical and soft skills")
        
        # Use Gemini for advanced recommendations
        try:
            prompt = f"""
            Analyze this resume text and provide 3-5 specific recommendations for improvement:
            
            Resume Text: {text[:2000]}...
            
            Focus on:
            1. Content improvements
            2. Formatting suggestions
            3. Keyword optimization
            4. Structure enhancements
            
            Provide actionable recommendations in bullet point format.
            """
            
            response = await self.gemini_model.generate_content_async(prompt)
            if response.text:
                gemini_recommendations = response.text.split('\n')
                recommendations.extend([rec.strip('- ') for rec in gemini_recommendations if rec.strip()])
        
        except Exception as e:
            logger.error(f"Error generating Gemini recommendations: {str(e)}")
        
        return recommendations[:10]  # Limit to 10 recommendations
    
    async def _generate_interview_questions(self, text: str, personal_info: PersonalInfo,
                                          work_experience: List[WorkExperienceEntry],
                                          education: List[EducationEntry], skills: List[SkillCategory],
                                          request: ResumeAnalysisRequest) -> List[InterviewQuestion]:
        """Generate interview questions based on resume content"""
        questions = []
        
        # Generate questions based on work experience
        for exp in work_experience[:3]:  # Limit to first 3 experiences
            prompt = f"""
            Generate 2-3 interview questions based on this work experience:
            
            Company: {exp.company}
            Job Title: {exp.job_title}
            Description: {exp.description}
            
            Focus on behavioral, technical, and situational questions.
            Return questions in JSON format with question, category, and difficulty.
            """
            
            try:
                response = await self.gemini_model.generate_content_async(prompt)
                if response.text:
                    # Parse Gemini response and convert to InterviewQuestion objects
                    # This is a simplified parsing - in production, use proper JSON parsing
                    question_lines = response.text.split('\n')
                    for line in question_lines:
                        if line.strip() and not line.startswith('{'):
                            questions.append(InterviewQuestion(
                                question=line.strip('- '),
                                category="behavioral",
                                difficulty="medium",
                                related_skills=[],
                                explanation=""
                            ))
            except Exception as e:
                logger.error(f"Error generating questions for experience: {str(e)}")
        
        # Generate skills-based questions
        for skill_category in skills[:2]:
            for skill in skill_category.skills[:3]:
                questions.append(InterviewQuestion(
                    question=f"Tell me about a project where you used {skill}.",
                    category="technical",
                    difficulty="medium",
                    related_skills=[skill],
                    explanation=f"Assess practical experience with {skill}"
                ))
        
        return questions[:15]  # Limit to 15 questions
    
    def _create_metadata(self, filename: str, file_size: int, text_length: int) -> Dict[str, Any]:
        """Create metadata for the resume analysis"""
        return {
            "filename": filename,
            "file_size": file_size,
            "file_type": filename.split('.')[-1].lower(),
            "upload_date": datetime.now(),
            "extracted_text_length": text_length
        }
    
    async def generate_interview_questions(self, resume_id: str) -> List[Dict[str, Any]]:
        """Generate interview questions for a specific resume"""
        # This would typically fetch from a database
        # For now, return a placeholder
        return [
            {
                "question": "Tell me about yourself and your professional background.",
                "category": "behavioral",
                "difficulty": "easy",
                "related_skills": ["communication"]
            },
            {
                "question": "Describe a challenging project you worked on and how you overcame obstacles.",
                "category": "situational",
                "difficulty": "medium",
                "related_skills": ["problem-solving", "teamwork"]
            }
        ]