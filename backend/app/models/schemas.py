from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class EducationLevel(str, Enum):
    """Education level enumeration"""
    HIGH_SCHOOL = "high_school"
    DIPLOMA = "diploma"
    UNDERGRADUATE = "undergraduate"
    GRADUATE = "graduate"
    POSTGRADUATE = "postgraduate"

class UserProfile(BaseModel):
    """User profile for internship recommendations"""
    name: str = Field(..., min_length=2, max_length=100, description="User's full name")
    education_level: EducationLevel = Field(..., description="Current education level")
    field_of_study: str = Field(..., min_length=2, max_length=100, description="Field of study or specialization")
    skills: List[str] = Field(..., min_length=1, max_length=20, description="List of user's skills")
    preferred_sectors: List[str] = Field(..., min_length=1, max_length=10, description="Preferred industry sectors")
    preferred_location: str = Field(..., min_length=2, max_length=100, description="Preferred work location")
    experience_years: Optional[int] = Field(0, ge=0, le=10, description="Years of relevant experience")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Rahul Sharma",
                "education_level": "undergraduate",
                "field_of_study": "Computer Science",
                "skills": ["Python", "Data Analysis", "Communication"],
                "preferred_sectors": ["Technology", "Healthcare"],
                "preferred_location": "Delhi",
                "experience_years": 0
            }
        }

class InternshipRecommendation(BaseModel):
    """Internship recommendation response model"""
    id: str = Field(..., description="Unique internship identifier")
    title: str = Field(..., description="Internship job title")
    company: str = Field(..., description="Company or organization name")
    sector: str = Field(..., description="Industry sector")
    location: str = Field(..., description="Internship location")
    duration_months: int = Field(..., description="Duration in months")
    stipend: Optional[int] = Field(None, description="Monthly stipend amount")
    description: str = Field(..., description="Internship description")
    required_skills: List[str] = Field(..., description="Required skills")
    education_requirement: str = Field(..., description="Education requirement")
    application_deadline: Optional[str] = Field(None, description="Application deadline")
    match_score: float = Field(..., ge=0, le=100, description="Matching score percentage")
    match_reasons: List[str] = Field(..., description="Reasons for recommendation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "INT001",
                "title": "Software Development Intern",
                "company": "Tech Innovations Pvt Ltd",
                "sector": "Technology",
                "location": "Delhi",
                "duration_months": 6,
                "stipend": 15000,
                "description": "Work on web applications using modern technologies",
                "required_skills": ["Python", "JavaScript", "React"],
                "education_requirement": "Undergraduate",
                "application_deadline": "2024-03-15",
                "match_score": 92.5,
                "match_reasons": ["Strong Python skills match", "Location preference aligned", "Education level suitable"]
            }
        }

class RecommendationResponse(BaseModel):
    """API response wrapper for recommendations"""
    user_profile: UserProfile
    recommendations: List[InternshipRecommendation]
    total_matches: int
    generated_at: str