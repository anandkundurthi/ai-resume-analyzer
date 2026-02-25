from PyPDF2 import PdfReader


def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text()
    return text


def clean_text(text):
    text = text.lower()
    return text


def calculate_similarity(resume_text, job_description, skills_list):
    matched = []
    missing = []

    for skill in skills_list:
        in_jd = skill in job_description
        in_resume = skill in resume_text
        if in_jd:
            if in_resume:
                matched.append(skill)
            else:
                missing.append(skill)

    total_required = len(matched) + len(missing)
    if total_required == 0:
        resume_words = set(resume_text.split())
        jd_words = set(job_description.split())
        stop_words = {"the", "and", "is", "in", "of", "to", "a", "for",
                      "with", "on", "at", "by", "an", "be", "or", "that",
                      "this", "are", "we", "you", "it", "as", "your", "our"}
        jd_words -= stop_words
        if not jd_words:
            return 0, [], []
        matched_words = resume_words.intersection(jd_words)
        score = round((len(matched_words) / len(jd_words)) * 100, 2)
        return min(score, 100), [], []

    score = round((len(matched) / total_required) * 100, 2)
    return score, matched, missing


def generate_career_suggestions(score, missing_skills):
    suggestions = []

    if score >= 80:
        suggestions.append("You are highly aligned with this role. Focus on advanced system design and leadership skills.")
    elif score >= 60:
        suggestions.append("You are moderately aligned. Strengthen the missing technical skills to improve your profile.")
    elif score >= 40:
        suggestions.append("You have some relevant skills but significant gaps remain. Prioritize the missing skills below.")
    else:
        suggestions.append("Your resume needs significant improvement for this role. Focus on building the core required skills.")

    if missing_skills:
        suggestions.append("Recommended skills to learn: " + ", ".join(missing_skills[:5]))

    if "react" in missing_skills:
        suggestions.append("Consider strengthening frontend skills for roles like Frontend Developer.")
    if "python" in missing_skills:
        suggestions.append("Improving Python can open Backend and Data roles.")
    if "sql" in missing_skills:
        suggestions.append("Database skills are critical for Backend and Data Engineering roles.")
    if "machine learning" in missing_skills:
        suggestions.append("Machine Learning skills are in high demand for AI/Data Science roles.")
    if "docker" in missing_skills:
        suggestions.append("Docker knowledge is essential for DevOps and Backend Engineering roles.")

    return suggestionsfrom PyPDF2 import PdfReader


def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text()
    return text

def clean_text(text):
    text = text.lower()
    words = text.split()
    cleaned_words = [word for word in words if word.isalpha()]
    return " ".join(cleaned_words)

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
