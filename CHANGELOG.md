# ResumeAI — Update Changelog

## 🐛 Bug Fixes

### Critical: Passwords stored in plaintext
- **Before:** Passwords were saved directly to the database (`hashed_password=password`)
- **After:** Passwords are now properly hashed using SHA-256 via the existing `hash_password()` function, and verified with `verify_password()` on login

### Cover Letter PDF/DOCX used wrong export functions
- **Before:** Cover letter PDF and DOCX downloads called the ATS resume export functions, producing incorrectly formatted output
- **After:** Two new dedicated functions — `build_cover_letter_pdf_bytes()` and `build_cover_letter_docx_bytes()` — with proper letter formatting (margins, spacing, font size 11pt)

### Analysis score stored as Integer (precision lost)
- **Before:** `score = Column(Integer)` truncated decimal scores like `72.5` → `72`
- **After:** `score = Column(Float)` preserves full precision

## ✨ New Features

### Score History Chart on Dashboard
- A line chart (Chart.js) now appears on the dashboard when 2+ analyses exist
- Shows match score trend over time with dates on the x-axis

### Application Tracker: Date Tracking
- Added **Date Applied** and **Interview Date** fields to the application form and table
- Database migrated automatically via `ensure_schema()`

### Application Tracker: Delete Applications
- Each application row now has a **Delete** button
- Secure: only the owning user can delete their own applications (`POST /applications/{id}/delete`)

### Mobile Navigation (Hamburger Menu)
- All pages now have a responsive hamburger menu on screens ≤ 820px
- Tapping the menu icon reveals/hides nav links as a dropdown

### `created_at` timestamp on Analyses
- Each analysis now records the UTC date it was run
- Used as labels in the score history chart

## 🔧 Performance & Code Quality

- `uvicorn[standard]` added to requirements for better async performance
- All imports properly organized and deduplicated
- `ensure_schema()` now handles migration for all new columns automatically (no manual DB changes needed)
- Cover letter and ATS resume export paths are now fully independent

## 🚀 How to Run

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```
