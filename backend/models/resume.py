from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

class ResumeMetadata(BaseModel):
    """Metadata about the resume file"""
    filename: str
    file_size: int
    file_type: str
    upload_date: datetime
    extracted_text_length: int

class PersonalInfo(BaseModel):
    """Personal information extracted from resume"""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    website: Optional[str] = None

class EducationEntry(BaseModel):
    """Educational background entry"""
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    gpa: Optional[str] = None
    achievements: List[str] = []

class WorkExperienceEntry(BaseModel):
    """Work experience entry"""
    company: str
    job_title: str
    start_date: str
    end_date: Optional[str] = None
    location: Optional[str] = None
    description: str
    achievements: List[str] = []
    technologies: List[str] = []

class SkillCategory(BaseModel):
    """Categorized skills"""
    category: str
    skills: List[str]
    proficiency_level: Optional[str] = None

class ProjectEntry(BaseModel):
    """Project experience entry"""
    name: str
    description: str
    technologies: List[str]
    role: str
    duration: Optional[str] = None
    achievements: List[str] = []

class CertificationEntry(BaseModel):
    """Certification entry"""
    name: str
    issuing_organization: str
    issue_date: Optional[str] = None
    expiration_date: Optional[str] = None
    credential_id: Optional[str] = None

class ResumeAnalysisRequest(BaseModel):
    """Request model for resume analysis"""
    extract_keywords: bool = True
    extract_entities: bool = True
    generate_questions: bool = True
    analysis_depth: str = Field(default="medium", description="Analysis depth: basic, medium, advanced")
    target_job_title: Optional[str] = None
    target_industry: Optional[str] = None

class ResumeAnalysisResponse(BaseModel):
    """Response model for resume analysis"""
    resume_id: str
    metadata: ResumeMetadata
    personal_info: PersonalInfo
    education: List[EducationEntry]
    work_experience: List[WorkExperienceEntry]
    skills: List[SkillCategory]
    projects: List[ProjectEntry]
    certifications: List[CertificationEntry]
    extracted_keywords: List[str]
    entities: Dict[str, List[str]]
    quality_score: float
    recommendations: List[str]
    analysis_timestamp: datetime
    processing_time_ms: int

class InterviewQuestion(BaseModel):
    """Generated interview question"""
    question: str
    category: str
    difficulty: str
    related_skills: List[str]
    explanation: Optional[str] = None

class QuestionsResponse(BaseModel):
    """Response model for generated questions"""
    resume_id: str
    questions: List[InterviewQuestion]
    total_questions: int
    categories: List[str]
    generation_timestamp: datetime