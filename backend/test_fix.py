#!/usr/bin/env python3
"""
Simple test script to verify the recommendation engine fix
Run this in the backend directory after starting the server
"""
import requests
import json

def test_recommendations():
    """Test the fixed recommendation endpoint"""
    
    # Test data
    user_profile = {
        "name": "Test User",
        "education_level": "undergraduate",
        "field_of_study": "Computer Science",
        "skills": ["Python", "JavaScript", "Communication"],
        "preferred_sectors": ["Technology"],
        "preferred_location": "Delhi",
        "experience_years": 0
    }
    
    print("🧪 Testing Fixed Recommendation Engine")
    print("=" * 50)
    
    try:
        # Test health check first
        print("1️⃣ Testing health check...")
        health_response = requests.get("http://localhost:8080/health", timeout=10)
        health_data = health_response.json()
        
        print(f"   Status: {health_response.status_code}")
        print(f"   Health: {health_data.get('status')}")
        print(f"   Data loaded: {health_data.get('data_loaded')}")
        print(f"   Total internships: {health_data.get('total_internships')}")
        
        if health_response.status_code != 200 or not health_data.get('data_loaded'):
            print("❌ Health check failed!")
            return False
        
        print("✅ Health check passed!")
        print()
        
        # Test recommendations
        print("2️⃣ Testing recommendations...")
        print(f"   User: {user_profile['name']}")
        print(f"   Education: {user_profile['education_level']}")
        print(f"   Skills: {', '.join(user_profile['skills'])}")
        print(f"   Location: {user_profile['preferred_location']}")
        print()
        
        response = requests.post(
            "http://localhost:8080/recommend",
            headers={"Content-Type": "application/json"},
            json=user_profile,
            timeout=15
        )
        
        print(f"   Response status: {response.status_code}")
        
        if response.status_code == 200:
            recommendations = response.json()
            print(f"✅ SUCCESS! Got {len(recommendations)} recommendations")
            print()
            
            # Show recommendations
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec['title']}")
                print(f"      Company: {rec['company']}")
                print(f"      Location: {rec['location']}")
                print(f"      Match Score: {rec['match_score']}%")
                print(f"      Sector: {rec['sector']}")
                print()
            
            return True
            
        else:
            print(f"❌ FAILED with status {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   Error: {error_detail.get('detail', 'Unknown error')}")
            except:
                print(f"   Raw response: {response.text}")
            return False
    
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend!")
        print("   Make sure the server is running: python run.py")
        return False
    
    except requests.exceptions.Timeout:
        print("❌ Request timed out!")
        print("   The server might be processing - try again")
        return False
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    success = test_recommendations()
    
    print("=" * 50)
    if success:
        print("🎉 ALL TESTS PASSED! Backend is working correctly!")
        print()
        print("🚀 You can now:")
        print("   • Visit http://localhost:8080/docs for interactive testing")
        print("   • Start the frontend and use the full application")
        print("   • Deploy to production")
    else:
        print("💔 Tests failed. Check the errors above.")
        print()
        print("🔧 Try these solutions:")
        print("   • Restart the backend server")
        print("   • Check if all dependencies are installed")
        print("   • Verify the CSV file exists in app/data/internships.csv")

if __name__ == "__main__":
    main()