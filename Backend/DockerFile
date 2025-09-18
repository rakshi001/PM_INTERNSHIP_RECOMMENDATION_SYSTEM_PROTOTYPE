FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy dependency file first (better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose port (if your app runs on a port, e.g., FastAPI/Flask/Django)
EXPOSE 8000

# Command to run the app (adjust as per your project)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
