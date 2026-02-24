from sqlalchemy.exc import IntegrityError
from app.utils import generate_career_suggestions
from app.auth_db import SessionLocal, User, Analysis
from fastapi import FastAPI, UploadFile, File, Form, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session

from app.utils import extract_text_from_pdf, clean_text, calculate_similarity
from app.skill_db import skills
from app.auth_db import User, hash_password, verify_password, get_db

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="supersecretkey")

templates = Jinja2Templates(directory="app/templates")


# ---------------- HOME ----------------
@app.get("/upload", response_class=HTMLResponse)
def upload_page(request: Request):

    user_email = request.session.get("user")

    if not user_email:
        return RedirectResponse("/login", status_code=303)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "user": user_email
        }
    )
# ---------------- REGISTER PAGE ----------------
@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(
        "register.html",
        {"request": request}
    )


# ---------------- REGISTER SUBMIT ----------------
@app.post("/register")
def register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(User.email == email).first()

    if existing_user:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "User already exists"}
        )

    new_user = User(
        email=email,
        hashed_password=hash_password(password)
    )

    db.add(new_user)
    db.commit()

    return RedirectResponse(url="/login", status_code=303)    

# ---------------- LOGIN ----------------
@app.get("/", response_class=HTMLResponse)
def root():
    return RedirectResponse("/login", status_code=303)

@app.post("/login")
def login(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

    request.session["user"] = user.email
    return RedirectResponse(url="/upload", status_code=303)


# ---------------- LOGOUT ----------------
@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)


# ---------------- ANALYZE ----------------
@app.post("/analyze", response_class=HTMLResponse)
async def analyze_resume(
    request: Request,
    resume: UploadFile = File(...),
    job_description: str = Form(...),
    db: Session = Depends(get_db)
):

    # 🔒 1. Protect route
    user_email = request.session.get("user")
    if not user_email:
        return RedirectResponse("/login", status_code=303)

    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        return RedirectResponse("/login", status_code=303)

    # 📄 2. Read PDF safely
    resume.file.seek(0)
    resume_text = extract_text_from_pdf(resume.file)

    if not resume_text:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error": "Could not read PDF",
                "user": user_email
            }
        )

    cleaned_resume = clean_text(resume_text)
    cleaned_jd = clean_text(job_description)

    similarity_score = calculate_similarity(cleaned_resume, cleaned_jd)

    matched_skills = []
    missing_skills = []

    for skill in skills:
        if skill in cleaned_resume and skill in cleaned_jd:
            matched_skills.append(skill)
        elif skill in cleaned_jd:
            missing_skills.append(skill)

    suggestions = generate_career_suggestions(similarity_score, missing_skills)

    # 💾 3. Save to database
    new_analysis = Analysis(
        user_id=user.id,
        score=similarity_score,
        matched_skills=", ".join(matched_skills),
        missing_skills=", ".join(missing_skills)
    )

    db.add(new_analysis)
    db.commit()

    # 🎯 4. Return result page
    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "score": similarity_score,
            "matched": matched_skills,
            "missing": missing_skills,
            "suggestions": suggestions,
            "user": user_email
        }
    )
# ---------------- DASHBOARD  ---------------- 
# ---------------- DASHBOARD ----------------
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):

    user_email = request.session.get("user")

    if not user_email:
        return RedirectResponse("/login", status_code=303)

    user = db.query(User).filter(User.email == user_email).first()

    if not user:
        return RedirectResponse("/", status_code=303)

    analyses = db.query(Analysis).filter(
        Analysis.user_id == user.id
    ).all()

    total_scans = len(analyses)

    avg_score = 0
    if total_scans > 0:
        avg_score = int(sum(a.score or 0 for a in analyses) / total_scans)

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "analyses": analyses,
            "total_scans": total_scans,
            "avg_score": avg_score,
            "user": user_email
        }
    )
