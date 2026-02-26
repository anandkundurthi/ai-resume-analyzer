from app.utils import (
    generate_career_suggestions,
    extract_text_from_upload,
    clean_text,
    calculate_similarity,
    generate_action_plan,
    build_report_text,
    build_ats_resume_text,
    build_ats_resume_pdf_bytes,
    build_ats_resume_docx_bytes,
)
from app.skill_db import skills
from fastapi import UploadFile, File, FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, PlainTextResponse, Response
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
from app.auth_db import get_db, User, Analysis

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="supersecretkey")
templates = Jinja2Templates(directory="app/templates")

ALL_SKILLS = skills["technical"] + skills["soft_skills"] + skills["tools"] + skills["business"]


def normalize_linkedin_url(url: str):
    if not url:
        return None
    cleaned = url.strip()
    if not cleaned:
        return None
    if "linkedin.com" not in cleaned.lower():
        return None
    if not cleaned.startswith("http://") and not cleaned.startswith("https://"):
        cleaned = f"https://{cleaned}"
    return cleaned

@app.get("/")
def root():
    return RedirectResponse("/login", status_code=303)

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    email = email.strip().lower()
    user = db.query(User).filter(User.email == email).first()
    if not user or password != user.hashed_password:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})
    request.session["user"] = user.email
    request.session["linkedin_url"] = user.linkedin_url
    return RedirectResponse("/upload", status_code=303)

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "linkedin_url": ""})

@app.post("/register")
def register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    linkedin_url: str = Form(""),
    db: Session = Depends(get_db),
):
    email = email.strip().lower()
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "error": "User already exists. Please login.",
                "linkedin_url": linkedin_url,
            },
        )
    normalized_linkedin = normalize_linkedin_url(linkedin_url)
    if linkedin_url.strip() and not normalized_linkedin:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Enter a valid LinkedIn URL", "linkedin_url": linkedin_url})
    new_user = User(email=email, hashed_password=password, linkedin_url=normalized_linkedin)
    db.add(new_user)
    db.commit()
    return RedirectResponse("/login", status_code=303)

@app.get("/upload", response_class=HTMLResponse)
def upload_page(request: Request):
    if not request.session.get("user"):
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse("index.html", {"request": request, "linkedin_url": request.session.get("linkedin_url")})

@app.post("/analyze/", response_class=HTMLResponse)
async def analyze_resume(request: Request, resume: UploadFile = File(...), job_description: str = Form(...), db: Session = Depends(get_db)):
    if not request.session.get("user"):
        return RedirectResponse("/login", status_code=303)
    user_email = request.session.get("user")
    user = db.query(User).filter(User.email == user_email).first()
    try:
        resume_text = extract_text_from_upload(resume)
    except ValueError as e:
        return templates.TemplateResponse("index.html", {"request": request, "error": str(e), "linkedin_url": request.session.get("linkedin_url")})
    except Exception:
        return templates.TemplateResponse("index.html", {"request": request, "error": "Could not read this document. Try another file format or a cleaner document.", "linkedin_url": request.session.get("linkedin_url")})
    if not resume_text:
        return templates.TemplateResponse("index.html", {"request": request, "error": "Could not read document content", "linkedin_url": request.session.get("linkedin_url")})
    cleaned_resume = clean_text(resume_text)
    cleaned_jd = clean_text(job_description)
    similarity_score, matched_skills, missing_skills = calculate_similarity(cleaned_resume, cleaned_jd, ALL_SKILLS)
    suggestions = generate_career_suggestions(similarity_score, missing_skills)
    action_plan = generate_action_plan(similarity_score, matched_skills, missing_skills)
    report_text = build_report_text(user_email, similarity_score, matched_skills, missing_skills, action_plan)
    safe_email = user_email.replace("@", "_at_").replace(".", "_")
    request.session["latest_report"] = {
        "filename": f"{safe_email}_resume_report.txt",
        "text": report_text,
    }
    if user:
        new_analysis = Analysis(user_id=user.id, score=similarity_score, matched_skills=", ".join(matched_skills), missing_skills=", ".join(missing_skills))
        db.add(new_analysis)
        db.commit()
    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "score": similarity_score,
            "matched": matched_skills,
            "missing": missing_skills,
            "suggestions": suggestions,
            "action_plan": action_plan,
            "user": user_email,
            "linkedin_url": request.session.get("linkedin_url"),
        },
    )

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
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "analyses": analyses,
            "total_scans": total_scans,
            "avg_score": avg_score,
            "user": user_email,
            "linkedin_url": user.linkedin_url,
        },
    )


@app.get("/profile", response_class=HTMLResponse)
def profile_page(request: Request, db: Session = Depends(get_db)):
    if not request.session.get("user"):
        return RedirectResponse("/login", status_code=303)
    user = db.query(User).filter(User.email == request.session["user"]).first()
    if not user:
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse("profile.html", {"request": request, "linkedin_url": user.linkedin_url, "saved": False})


@app.post("/profile", response_class=HTMLResponse)
def update_profile(request: Request, linkedin_url: str = Form(""), db: Session = Depends(get_db)):
    if not request.session.get("user"):
        return RedirectResponse("/login", status_code=303)
    user = db.query(User).filter(User.email == request.session["user"]).first()
    if not user:
        return RedirectResponse("/login", status_code=303)
    normalized_linkedin = normalize_linkedin_url(linkedin_url)
    if linkedin_url.strip() and not normalized_linkedin:
        return templates.TemplateResponse("profile.html", {"request": request, "linkedin_url": user.linkedin_url, "saved": False, "error": "Enter a valid LinkedIn URL"})
    user.linkedin_url = normalized_linkedin
    db.commit()
    request.session["linkedin_url"] = user.linkedin_url
    return templates.TemplateResponse("profile.html", {"request": request, "linkedin_url": user.linkedin_url, "saved": True})

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)


@app.get("/download-report")
def download_report(request: Request):
    if not request.session.get("user"):
        return RedirectResponse("/login", status_code=303)
    report = request.session.get("latest_report")
    if not report:
        return RedirectResponse("/dashboard", status_code=303)
    response = PlainTextResponse(report.get("text", ""), media_type="text/plain")
    response.headers["Content-Disposition"] = f'attachment; filename="{report.get("filename", "resume_report.txt")}"'
    return response


@app.get("/ats-resume", response_class=HTMLResponse)
def ats_resume_page(request: Request):
    if not request.session.get("user"):
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse(
        "ats_resume.html",
        {
            "request": request,
            "linkedin_url": request.session.get("linkedin_url"),
            "generated_resume": "",
            "form_data": {},
        },
    )


@app.post("/ats-resume", response_class=HTMLResponse)
def generate_ats_resume(
    request: Request,
    full_name: str = Form(""),
    email: str = Form(""),
    phone: str = Form(""),
    location: str = Form(""),
    linkedin: str = Form(""),
    github: str = Form(""),
    summary: str = Form(""),
    skills: str = Form(""),
    experience: str = Form(""),
    projects: str = Form(""),
    education: str = Form(""),
    certifications: str = Form(""),
):
    if not request.session.get("user"):
        return RedirectResponse("/login", status_code=303)

    form_data = {
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "location": location,
        "linkedin": linkedin,
        "github": github,
        "summary": summary,
        "skills": skills,
        "experience": experience,
        "projects": projects,
        "education": education,
        "certifications": certifications,
    }
    resume_text = build_ats_resume_text(form_data)
    safe_name = (full_name.strip() or "candidate").replace(" ", "_")
    request.session["ats_resume"] = {
        "base_filename": f"{safe_name.lower()}_ats_resume",
        "text": resume_text,
    }
    return templates.TemplateResponse(
        "ats_resume.html",
        {
            "request": request,
            "linkedin_url": request.session.get("linkedin_url"),
            "generated_resume": resume_text,
            "form_data": form_data,
        },
    )


@app.get("/download-ats-resume")
def download_ats_resume(request: Request):
    if not request.session.get("user"):
        return RedirectResponse("/login", status_code=303)
    ats_resume = request.session.get("ats_resume")
    if not ats_resume:
        return RedirectResponse("/ats-resume", status_code=303)
    response = PlainTextResponse(ats_resume.get("text", ""), media_type="text/plain")
    response.headers["Content-Disposition"] = f'attachment; filename="{ats_resume.get("base_filename", "ats_resume")}.txt"'
    return response


@app.get("/download-ats-resume-pdf")
def download_ats_resume_pdf(request: Request):
    if not request.session.get("user"):
        return RedirectResponse("/login", status_code=303)
    ats_resume = request.session.get("ats_resume")
    if not ats_resume:
        return RedirectResponse("/ats-resume", status_code=303)
    try:
        pdf_bytes = build_ats_resume_pdf_bytes(ats_resume.get("text", ""))
    except ImportError:
        return PlainTextResponse("PDF export dependency missing. Install requirements and retry.", status_code=500)
    response = Response(content=pdf_bytes, media_type="application/pdf")
    response.headers["Content-Disposition"] = f'attachment; filename="{ats_resume.get("base_filename", "ats_resume")}.pdf"'
    return response


@app.get("/download-ats-resume-docx")
def download_ats_resume_docx(request: Request):
    if not request.session.get("user"):
        return RedirectResponse("/login", status_code=303)
    ats_resume = request.session.get("ats_resume")
    if not ats_resume:
        return RedirectResponse("/ats-resume", status_code=303)
    try:
        docx_bytes = build_ats_resume_docx_bytes(ats_resume.get("text", ""))
    except ImportError:
        return PlainTextResponse("DOCX export dependency missing. Install requirements and retry.", status_code=500)
    response = Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
    response.headers["Content-Disposition"] = f'attachment; filename="{ats_resume.get("base_filename", "ats_resume")}.docx"'
    return response
