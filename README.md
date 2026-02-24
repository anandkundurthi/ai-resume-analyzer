📊 AI Resume Analyzer

An AI-powered Resume Analyzer built using FastAPI, Python, and SQLAlchemy that helps job seekers compare their resumes with job descriptions and identify skill gaps. The application includes user authentication, PDF resume parsing, similarity scoring, career suggestions, and a dashboard to track analysis history.

🔗 Live App: https://ai-resume-analyzer-tuet.onrender.com

🔗 GitHub Repository: https://github.com/anandkundurthi/ai-resume-analyzer

🚀 Features
🔐 Authentication System

User Registration

Secure Login

Session-based authentication

Logout functionality

📄 Resume Analysis

Upload PDF resume

Paste Job Description

Extract text using PyPDF2

Clean and tokenize text

Calculate similarity score

Identify matched skills

Detect missing skills

Generate career suggestions

📊 Dashboard

View analysis history

Track total scans

View average score

Start new analysis

Secure access (only logged-in users)

🧠 Tech Stack

Backend Framework: FastAPI

Language: Python 3

Database: SQLite

ORM: SQLAlchemy

Authentication: Session Middleware

Templating Engine: Jinja2

PDF Processing: PyPDF2

Deployment: Render

📁 Project Structure
ai-resume-analyzer/
│
├── app/
│   ├── main.py              # FastAPI routes
│   ├── auth_db.py           # Database models & auth logic
│   ├── utils.py             # Resume analysis logic
│   ├── skill_db.py          # Skills list
│   ├── templates/
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── index.html
│   │   ├── result.html
│   │   └── dashboard.html
│
├── requirements.txt
└── README.md
⚙️ Installation (Run Locally)
1️⃣ Clone the repository
git clone https://github.com/anandkundurthi/ai-resume-analyzer.git
cd ai-resume-analyzer
2️⃣ Create virtual environment
python3 -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
3️⃣ Install dependencies
pip install -r requirements.txt
4️⃣ Run the application
uvicorn app.main:app --reload

Open in browser:

http://127.0.0.1:8000
🔄 Application Flow

If user exists →
Login → Upload Resume → Analyze → View Result → Dashboard → History

If user does not exist →
Create Account → Login → Upload Resume → Analyze → View Result → Dashboard

🧩 How It Works

User uploads resume (PDF format)

System extracts text using PyPDF2

Resume text is cleaned and tokenized

Job description is processed

Similarity score is calculated

Matched and missing skills are identified

Career suggestions are generated

Results are stored in database

User can view history in dashboard

🎯 Skills Demonstrated

Backend Development with FastAPI

REST API Design

File Upload Handling

PDF Parsing

Session Authentication

SQLAlchemy ORM

Database Modeling

Jinja2 Template Rendering

Cloud Deployment (Render)

Debugging Production Errors

📌 Deployment

The application is deployed on Render with:

uvicorn app.main:app --host 0.0.0.0 --port $PORT

Render automatically:

Installs dependencies

Builds the app

Hosts it securely over HTTPS

👨‍💻 Author

Anand Kundurthi
Backend Developer | Python | FastAPI | SQL

LinkedIn: https://www.linkedin.com/in/anandkundurthi

GitHub: https://github.com/anandkundurthi

📜 License

This project is open-source and available under the MIT License.
