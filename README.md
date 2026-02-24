AI Resume Analyzer
Project Overview

AI Resume Analyzer is a web application built using FastAPI and Python that helps job seekers evaluate their resumes against job descriptions.

The system calculates a similarity score, identifies matched and missing skills, and provides career suggestions. It also includes user authentication and a dashboard to track analysis history.

Live Demo

Live Application:
https://ai-resume-analyzer-tuet.onrender.com

GitHub Repository:
https://github.com/anandkundurthi/ai-resume-analyzer

Key Features
1. User Authentication

User Registration

Secure Login

Session Management

Logout Functionality

2. Resume Analysis

Upload Resume (PDF format)

Enter Job Description

Extract Resume Text using PyPDF2

Clean and Process Text

Calculate Similarity Score

Identify Matched Skills

Identify Missing Skills

Generate Career Suggestions

3. Dashboard

View Analysis History

Display Total Resume Scans

Calculate Average Score

Start New Analysis

Secure Access (Login Required)

Tech Stack
Backend

Python

FastAPI

Database

SQLite

SQLAlchemy ORM

Frontend

HTML

CSS

Jinja2 Templates

Other Tools

PyPDF2 (PDF text extraction)

Session Middleware (Authentication)

Render (Deployment)

Project Structure

ai-resume-analyzer
│
├── app
│ ├── main.py
│ ├── auth_db.py
│ ├── utils.py
│ ├── skill_db.py
│ └── templates
│
├── requirements.txt
└── README.md

How It Works

User registers or logs in.

User uploads a resume in PDF format.

User pastes a job description.

The system extracts and processes resume text.

Resume and job description are compared.

Similarity score is calculated.

Matched and missing skills are displayed.

Career suggestions are generated.

Results are saved in the dashboard.

Installation (Run Locally)
Step 1: Clone Repository

git clone https://github.com/anandkundurthi/ai-resume-analyzer.git

cd ai-resume-analyzer

Step 2: Create Virtual Environment

python3 -m venv venv
source venv/bin/activate

Step 3: Install Dependencies

pip install -r requirements.txt

Step 4: Run Application

uvicorn app.main:app --reload

Open in browser:
http://127.0.0.1:8000

Skills Demonstrated

Backend Development with FastAPI

RESTful API Design

File Upload Handling

PDF Processing

Authentication & Session Management

Database Modeling with SQLAlchemy

Deployment on Cloud (Render)

Debugging Production Errors

Deployment

This project is deployed using Render with:

uvicorn app.main:app --host 0.0.0.0 --port $PORT

Author

Anand Kundurthi
Backend Developer | Python | FastAPI | SQL

LinkedIn: https://www.linkedin.com/in/anandkundurthi

GitHub: https://github.com/anandkundurthi

