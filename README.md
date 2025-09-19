# PM Internship Recommendation System — Prototype

This is a prototype backend for an Internship Recommendation System, built using **FastAPI**, **Pandas**, **NumPy**, and **Scikit-Learn**.

---

## ⚙️ Setup & Installation

Follow these steps to run the project locally:

### 1. Clone the repository

```bash
git clone https://github.com/preetham92/PM_INTERNSHIP_RECOMMENDATION_SYSTEM_PROTOTYPE
cd PM_INTERNSHIP_RECOMMENDATION_SYSTEM_PROTOTYPE/Backend
```

### 2. Create and activate a virtual environment

```# Create venv
python3 -m venv venv

# Activate venv (Linux / macOS)
source venv/bin/activate

# (Windows)
# venv\Scripts\activate
```
### 3. Install dependencies

Make sure you are in your backend directory before itself.
```
pip install -r requirements.txt
```

### 🚀 Run the FastAPI server

From inside the ``` Backend folder```:

Run this in your terminal 
```
uvicorn app.main:app --reload
```

Once running, the server will be available at:

Base URL: http://127.0.0.1:8000

Docs UI: http://127.0.0.1:8000/docs

ReDoc UI: http://127.0.0.1:8000/redoc


## 📁 Project Structure
```
Backend/
├── app/
│   ├── main.py          
│   ├── models/           
│   ├── services/         
│   └── data/              
├── requirements.txt
├── run.py
└── venv/ (virtual environment - ignored in git)
```



