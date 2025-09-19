from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import os
from .services.recommendation_engine import RecommendationEngine
from .models.schemas import UserProfile, InternshipRecommendation

app = FastAPI(
    title="PM Internship Recommendation API",
    description="AI-powered internship recommendation system for PM Internship Scheme",
    version="1.0.0"
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize recommendation engine
recommendation_engine = RecommendationEngine()

@app.on_event("startup")
async def startup_event():
    """Initialize the recommendation engine on startup"""
    try:
        recommendation_engine.load_data()
        print("✅ Recommendation engine initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize recommendation engine: {e}")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "PM Internship Recommendation API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "data_loaded": recommendation_engine.is_data_loaded(),
        "total_internships": recommendation_engine.get_total_internships()
    }

@app.post("/recommend", response_model=List[InternshipRecommendation])
async def get_recommendations(user_profile: UserProfile):
    """
    Get personalized internship recommendations based on user profile
    """
    try:
        if not recommendation_engine.is_data_loaded():
            raise HTTPException(
                status_code=503, 
                detail="Recommendation service is not ready. Please try again later."
            )
        
        recommendations = recommendation_engine.get_recommendations(user_profile)
        
        if not recommendations:
            raise HTTPException(
                status_code=404,
                detail="No suitable internships found. Please try adjusting your preferences."
            )
        
        return recommendations
        
    except Exception as e:
        print(f"Error in get_recommendations: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendations: {str(e)}"
        )

@app.get("/sectors")
async def get_available_sectors():
    """Get list of available sectors for internships"""
    try:
        sectors = recommendation_engine.get_available_sectors()
        return {"sectors": sectors}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch sectors: {str(e)}"
        )

@app.get("/locations")
async def get_available_locations():
    """Get list of available locations for internships"""
    try:
        locations = recommendation_engine.get_available_locations()
        return {"locations": locations}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch locations: {str(e)}"
        )