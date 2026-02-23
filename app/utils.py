import PyPDF2


def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text()
    return text

def clean_text(text):
    doc = nlp(text.lower())
    tokens = [token.lemma_ for token in doc if not token.is_stop and token.is_alpha]
    return " ".join(tokens)

def calculate_similarity(resume_text, job_description):
    resume_words = set(resume_text.split())
    jd_words = set(job_description.split())

    if not jd_words:
        return 0

    matched = resume_words.intersection(jd_words)
    score = (len(matched) / len(jd_words)) * 100

    return round(score, 2)

def generate_career_suggestions(score, missing_skills):

    suggestions = []

    if score >= 80:
        suggestions.append("You are highly aligned with this role. Focus on advanced system design and leadership skills.")
    elif score >= 60:
        suggestions.append("You are moderately aligned. Strengthen the missing technical skills to improve your profile.")
    else:
        suggestions.append("Your resume needs significant improvement. Focus on building core technical skills.")

    if missing_skills:
        suggestions.append("Recommended skills to learn: " + ", ".join(missing_skills[:5]))

    # Role recommendations
    if "react" in missing_skills:
        suggestions.append("Consider strengthening frontend skills for roles like Frontend Developer.")
    if "python" in missing_skills:
        suggestions.append("Improving Python can open Backend and Data roles.")
    if "sql" in missing_skills:
        suggestions.append("Database skills are critical for Backend and Data Engineering roles.")

    return suggestions
