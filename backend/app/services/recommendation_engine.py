import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import LabelEncoder
import os
from typing import List, Dict, Any
from ..models.schemas import UserProfile, InternshipRecommendation

class RecommendationEngine:
    """
    AI-powered recommendation engine for internship matching
    Uses ML techniques including TF-IDF vectorization and cosine similarity
    """
    
    def __init__(self):
        self.internships_df = None
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        self.skills_vectors = None
        self.is_loaded = False
        
    def load_data(self):
        """Load internship data from CSV file"""
        try:
            data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'internships.csv')
            
            # Load CSV with explicit data types to avoid conversion issues
            self.internships_df = pd.read_csv(data_path, dtype={
                'id': 'str',
                'title': 'str', 
                'company': 'str',
                'sector': 'str',
                'location': 'str',
                'duration_months': 'str',  # Keep as string initially
                'stipend': 'str',          # Keep as string initially
                'description': 'str',
                'required_skills': 'str',
                'education_requirement': 'str',
                'application_deadline': 'str'
            })
            
            # Clean and convert numeric columns 
            self.internships_df['duration_months'] = pd.to_numeric(
                self.internships_df['duration_months'], errors='coerce'
            ).fillna(3).astype(int)
            
            self.internships_df['stipend'] = pd.to_numeric(
                self.internships_df['stipend'], errors='coerce'
            )
            
            # Fill NaN values with appropriate defaults
            self.internships_df['title'] = self.internships_df['title'].fillna('Internship Opportunity')
            self.internships_df['company'] = self.internships_df['company'].fillna('Company Name')
            self.internships_df['sector'] = self.internships_df['sector'].fillna('General')
            self.internships_df['location'] = self.internships_df['location'].fillna('Location TBD')
            self.internships_df['description'] = self.internships_df['description'].fillna('Description not available')
            self.internships_df['required_skills'] = self.internships_df['required_skills'].fillna('')
            self.internships_df['education_requirement'] = self.internships_df['education_requirement'].fillna('Not specified')
            
            # Prepare text features for similarity matching
            self._prepare_features()
            self.is_loaded = True
            print(f"Loaded {len(self.internships_df)} internships successfully")
            
        except Exception as e:
            print(f"Error loading data: {e}")
            self.is_loaded = False
            raise e
    
    def _prepare_features(self):
        """Prepare features for ML-based matching"""
        # Combine relevant text features
        self.internships_df['combined_features'] = (
            self.internships_df['required_skills'].fillna('') + ' ' +
            self.internships_df['sector'].fillna('') + ' ' +
            self.internships_df['description'].fillna('')
        )
        
        # for creating TF-IDF vectors which will be used in skills and content matching
        self.skills_vectors = self.vectorizer.fit_transform(
            self.internships_df['combined_features']
        )
    
    def get_recommendations(self, user_profile: UserProfile) -> List[InternshipRecommendation]:
        """
        Generate personalized internship recommendations using ML algorithms
        """
        if not self.is_loaded:
            raise Exception("Data not loaded")
        
        try:
            # Create user feature vector
            user_skills_text = ' '.join(user_profile.skills) + ' ' + user_profile.field_of_study
            user_vector = self.vectorizer.transform([user_skills_text])
            
            # Calculate similarity scores
            similarity_scores = cosine_similarity(user_vector, self.skills_vectors).flatten()
            
            # Apply business rules and filtering
            filtered_internships = self._apply_filters(user_profile)
            
            # Score and rank internships
            scored_internships = self._score_internships(
                filtered_internships, user_profile, similarity_scores
            )
            
            # Return top 5 recommendations
            top_recommendations = scored_internships.head(5)
            
            return [
                self._create_recommendation_object(row, user_profile)
                for _, row in top_recommendations.iterrows()
            ]
            
        except Exception as e:
            print(f"Error in get_recommendations: {e}")
            print(f"User profile: {user_profile}")
            print(f"Data loaded: {self.is_loaded}")
            print(f"Internships count: {len(self.internships_df) if self.internships_df is not None else 'None'}")
            raise e
    
    def _apply_filters(self, user_profile: UserProfile) -> pd.DataFrame:
        """Apply business logic filters"""
        filtered_df = self.internships_df.copy()
        
        # Education level filter
        education_mapping = {
            'high_school': ['High School', 'Diploma', 'Undergraduate', 'Graduate', 'Postgraduate'],
            'diploma': ['Diploma', 'Undergraduate', 'Graduate', 'Postgraduate'],
            'undergraduate': ['Undergraduate', 'Graduate', 'Postgraduate'],
            'graduate': ['Graduate', 'Postgraduate'],
            'postgraduate': ['Postgraduate']
        }
        
        allowed_education = education_mapping.get(user_profile.education_level.value, [])
        if allowed_education:
            # Use case-insensitive matching and handle NaN values
            filtered_df = filtered_df[
                filtered_df['education_requirement'].fillna('').str.contains('|'.join(allowed_education), case=False, na=False)
            ]
        
        # Reset index to ensure proper indexing later
        filtered_df = filtered_df.reset_index(drop=True)
        
        # Ensure we have at least some internships to recommend
        if len(filtered_df) == 0:
            print("Warning: No internships match education filter, returning all internships")
            filtered_df = self.internships_df.copy().reset_index(drop=True)
        
        return filtered_df
    
    def _score_internships(self, internships_df: pd.DataFrame, 
                          user_profile: UserProfile, similarity_scores: np.ndarray) -> pd.DataFrame:
        """Calculate comprehensive matching scores"""
        scored_df = internships_df.copy()
        
        # Add similarity scores - fix indexing issue
        # Reset index to ensure proper alignment
        scored_df = scored_df.reset_index(drop=True)
        
        # Ensure similarity_scores length matches dataframe length
        if len(similarity_scores) >= len(scored_df):
            scored_df['similarity_score'] = similarity_scores[:len(scored_df)]
        else:
            # If similarity scores are shorter, pad with zeros
            padded_scores = np.zeros(len(scored_df))
            padded_scores[:len(similarity_scores)] = similarity_scores
            scored_df['similarity_score'] = padded_scores
        
        # Calculate additional scoring factors
        scored_df['location_score'] = scored_df['location'].apply(
            lambda x: 20 if user_profile.preferred_location.lower() in str(x).lower() else 0
        )
        
        scored_df['sector_score'] = scored_df['sector'].apply(
            lambda x: 15 if any(sector.lower() in str(x).lower() for sector in user_profile.preferred_sectors) else 0
        )
        
        # Skills matching score
        scored_df['skills_match_score'] = scored_df['required_skills'].apply(
            lambda x: self._calculate_skills_match(x, user_profile.skills)
        )
        
        # Experience level matching
        scored_df['experience_score'] = scored_df.apply(
            lambda row: self._calculate_experience_score(row, user_profile.experience_years), axis=1
        )
        
        # Combine all scores (weighted)
        scored_df['final_score'] = (
            scored_df['similarity_score'] * 40 +  # Content similarity
            scored_df['skills_match_score'] * 25 +  # Skills match
            scored_df['location_score'] +  # Location preference
            scored_df['sector_score'] +  # Sector preference
            scored_df['experience_score']  # Experience match
        )
        
        # Sort by final score
        return scored_df.sort_values('final_score', ascending=False)
    
    def _calculate_skills_match(self, required_skills: str, user_skills: List[str]) -> float:
        """Calculate percentage of skills match"""
        if pd.isna(required_skills):
            return 0
        
        required = [s.strip().lower() for s in str(required_skills).split(',')]
        user = [s.strip().lower() for s in user_skills]
        
        matches = sum(1 for skill in required if any(skill in user_skill or user_skill in skill for user_skill in user))
        return (matches / len(required)) * 20 if required else 0
    
    def _calculate_experience_score(self, row: pd.Series, user_experience: int) -> float:
        """Calculate experience level matching score"""
        # Simple heuristic: favor internships that match experience level
        if user_experience == 0:
            return 5  # Entry level bonus
        elif user_experience <= 2:
            return 3
        else:
            return 2
    
    def _create_recommendation_object(self, row: pd.Series, user_profile: UserProfile) -> InternshipRecommendation:
        """Create InternshipRecommendation object from DataFrame row"""
        # Generate match reasons
        match_reasons = []
        if row.get('skills_match_score', 0) > 10:
            match_reasons.append("Strong skills alignment")
        if row.get('location_score', 0) > 0:
            match_reasons.append("Preferred location match")
        if row.get('sector_score', 0) > 0:
            match_reasons.append("Sector preference aligned")
        if row.get('similarity_score', 0) > 0.3:
            match_reasons.append("Content similarity high")
        if not match_reasons:
            match_reasons.append("General compatibility")
        
        # Normalize final score to 0-100 scale
        max_possible_score = 100  # Theoretical maximum
        match_score = min(100, (row.get('final_score', 0) / max_possible_score) * 100)
        
        # Safe conversion functions to handle potential data type issues
        def safe_int(value, default=0):
            try:
                if pd.isna(value):
                    return default
                return int(float(value))  # Convert to float first, then int
            except (ValueError, TypeError):
                return default
        
        def safe_str(value, default=""):
            try:
                if pd.isna(value):
                    return default
                return str(value).strip()
            except:
                return default
        
        def safe_list(value, default=None):
            if default is None:
                default = []
            try:
                if pd.isna(value):
                    return default
                return [s.strip() for s in str(value).split(',') if s.strip()]
            except:
                return default
        
        return InternshipRecommendation(
            id=safe_str(row['id'], f"INT_{hash(str(row)) % 10000}"),
            title=safe_str(row['title'], "Internship Opportunity"),
            company=safe_str(row['company'], "Company Name"),
            sector=safe_str(row['sector'], "General"),
            location=safe_str(row['location'], "Location TBD"),
            duration_months=safe_int(row['duration_months'], 3),
            stipend=safe_int(row['stipend']) if not pd.isna(row.get('stipend')) else None,
            description=safe_str(row['description'], "Internship description not available"),
            required_skills=safe_list(row['required_skills']),
            education_requirement=safe_str(row['education_requirement'], "Not specified"),
            application_deadline=safe_str(row.get('application_deadline')) if not pd.isna(row.get('application_deadline')) else None,
            match_score=round(max(0, min(100, match_score)), 1),
            match_reasons=match_reasons
        )
    
    def is_data_loaded(self) -> bool:
        """Check if data is loaded"""
        return self.is_loaded
    
    def get_total_internships(self) -> int:
        """Get total number of internships"""
        return len(self.internships_df) if self.is_loaded else 0
    
    def get_available_sectors(self) -> List[str]:
        """Get unique sectors available"""
        if not self.is_loaded:
            return []
        return sorted(self.internships_df['sector'].dropna().unique().tolist())
    
    def get_available_locations(self) -> List[str]:
        """Get unique locations available"""
        if not self.is_loaded:
            return []
        return sorted(self.internships_df['location'].dropna().unique().tolist())