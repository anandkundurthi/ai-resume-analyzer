from app.utils import generate_career_suggestions, extract_text_from_pdf, clean_text, calculate_similarity
from app.skill_db import skills
from fastapi import UploadFile, File, FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
from app.auth_db import get_db, User, Analysis

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="supersecretkey")
templates = Jinja2Templates(directory="app/templates")

ALL_SKILLS = skills["technical"] + skills["soft_skills"] + skills["tools"] + skills["business"]

@app.get("/")
def root():
    return RedirectResponse("/login", status_code=303)

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or password != user.hashed_password:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})
    request.session["user"] = user.email
    return RedirectResponse("/upload", status_code=303)

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
def register(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return templates.TemplateResponse("register.html", {"request": request, "error": "User already exists"})
    new_user = User(email=email, hashed_password=password)
    db.add(new_user)
    db.commit()
    return RedirectResponse("/login", status_code=303)

@app.get("/upload", response_class=HTMLResponse)
def upload_page(request: Request):
    if not request.session.get("user"):
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analyze/", response_class=HTMLResponse)
async def analyze_resume(request: Request, resume: UploadFile = File(...), job_description: str = Form(...), db: Session = Depends(get_db)):
    if not request.session.get("user"):
        return RedirectResponse("/login", status_code=303)
    user_email = request.session.get("user")
    user = db.query(User).filter(User.email == user_email).first()
    resume.file.seek(0)
    resume_text = extract_text_from_pdf(resume.file)
    if not resume_text:
        return templates.TemplateResponse("index.html", {"request": request, "error": "Could not read PDF"})
    cleaned_resume = clean_text(resume_text)
    cleaned_jd = clean_text(job_description)
    similarity_score, matched_skills, missing_skills = calculate_similarity(cleaned_resume, cleaned_jd, ALL_SKILLS)
    suggestions = generate_career_suggestions(similarity_score, missing_skills)
    if user:
        new_analysis = Analysis(user_id=user.id, score=similarity_score, matched_skills=", ".join(matched_skills), missing_skills=", ".join(missing_skills))
        db.add(new_analysis)
        db.commit()
    return templates.TemplateResponse("result.html", {"request": request, "score": similarity_score, "matched": matched_skills, "missing": missing_skills, "suggestions": suggestions, "user": user_email})

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    if not request.session.get("user"):
        return RedirectResponse("/login", status_code=303)
    user_email = request.session.get("user")
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        return RedirectResponse("/login", status_code=303)
    analyses = db.query(Analysis).filter(Analysis.user_id == user.id).all()
    total_scans = len(analyses)
    avg_score = int(sum(a.score or 0 for a in analyses) / total_scans) if total_scans > 0 else 0
    return templates.TemplateResponse("dashboard.html", {"request": request, "analyses": analyses, "total_scans": total_scans, "avg_score": avg_score, "user": user_email})

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)
