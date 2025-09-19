
import uvicorn
from multiprocessing import freeze_support

def main():
    print("🚀 Starting PM Internship Recommendation API Server...")
    print("📍 Server will be available at: http://localhost:8080")
    print("📚 API Documentation: http://localhost:8080/docs")
    print("🔄 Health Check: http://localhost:8080/health")
    print("\n" + "="*50)
    
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",  # Changed to localhost for Windows compatibility
        port=8080,
        reload=False,  # Disabled reload to avoid Windows multiprocessing issues
        log_level="info"
    )

if __name__ == "__main__":
    freeze_support()  # Required for Windows multiprocessing
    main()