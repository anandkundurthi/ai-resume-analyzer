from fastapi import UploadFile, File
from app.utils import extract_text_from_pdf, clean_text, calculate_similarity
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session

from app.auth_db import get_db, User, verify_password

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="supersecretkey")

templates = Jinja2Templates(directory="app/templates")


# ---------------- ROOT ----------------
@app.get("/")
def root():
    return RedirectResponse("/login", status_code=303)


# ---------------- LOGIN GET ----------------
@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# ---------------- LOGIN POST ----------------
@app.post("/login")
def login(request: Request,
          email: str = Form(...),
          password: str = Form(...),
          db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == email).first()

    # SIMPLE CHECK (no hashing for now)
    if not user or password != user.hashed_password:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid credentials"}
        )

    request.session["user"] = user.email
    return RedirectResponse("/upload", status_code=303)

# ---------------- REGISTER GET ----------------
@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# ---------------- REGISTER POST ----------------
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
        hashed_password=password
    )

    db.add(new_user)
    db.commit()

    return RedirectResponse("/login", status_code=303)


# ---------------- UPLOAD ----------------
@app.get("/upload", response_class=HTMLResponse)
def upload_page(request: Request):
    if not request.session.get("user"):
        return RedirectResponse("/login", status_code=303)

    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

# ---------------- ANALYZE ----------------
@app.post("/analyze/", response_class=HTMLResponse)
async def analyze_resume(
    request: Request,
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    if not request.session.get("user"):
        return RedirectResponse("/login", status_code=303)

    resume.file.seek(0)
    resume_text = extract_text_from_pdf(resume.file)

    if not resume_text:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "error": "Could not read PDF"}
        )

    cleaned_resume = clean_text(resume_text)
    cleaned_jd = clean_text(job_description)

    similarity_score = calculate_similarity(cleaned_resume, cleaned_jd)

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "score": similarity_score
        }
    )


# ---------------- DASHBOARD ----------------
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    if not request.session.get("user"):
        return RedirectResponse("/login", status_code=303)

    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request}
    )


# ---------------- LOGOUT ----------------
@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)
