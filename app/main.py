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
