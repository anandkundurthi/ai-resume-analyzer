from PyPDF2 import PdfReader
from datetime import datetime

def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text()
    return text

def clean_text(text):
    return text.lower()

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
        stop_words = {"the","and","is","in","of","to","a","for","with","on","at","by","an","be","or","that","this","are","we","you","it","as","your","our"}
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
    return suggestions


def generate_action_plan(score, matched_skills, missing_skills):
    strengths = matched_skills[:5]
    focus_skills = missing_skills[:5]

    if score >= 80:
        level = "Strong Fit"
        headline = "You are interview-ready for many roles in this category."
    elif score >= 60:
        level = "Competitive Fit"
        headline = "You are close to target. Closing top gaps can significantly improve outcomes."
    elif score >= 40:
        level = "Developing Fit"
        headline = "You have partial alignment. Build core skills and strengthen evidence in projects."
    else:
        level = "Early Fit"
        headline = "You need stronger baseline alignment before applying broadly."

    priority_actions = []
    for skill in focus_skills[:3]:
        priority_actions.append(f"Build and document one project outcome using {skill}.")
    while len(priority_actions) < 3:
        priority_actions.append("Add measurable impact bullets using metrics (%, $, time saved).")

    week_plan = [
        "Week 1: Prioritize top 2 missing skills and create a focused learning schedule.",
        "Week 2: Build a mini-project that demonstrates those skills with business impact.",
        "Week 3: Rewrite resume bullets using action verbs and quantified outcomes.",
        "Week 4: Re-analyze resume and apply to roles matching your improved profile.",
    ]

    resume_edits = [
        "Move strongest, role-relevant projects to the top half of the resume.",
        "Add a 2-line professional summary aligned with the target job.",
        "Tailor skills order so required keywords appear naturally in context.",
    ]

    return {
        "level": level,
        "headline": headline,
        "strengths": strengths,
        "focus_skills": focus_skills,
        "priority_actions": priority_actions,
        "week_plan": week_plan,
        "resume_edits": resume_edits,
    }


def build_report_text(user_email, score, matched_skills, missing_skills, action_plan):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    matched_text = ", ".join(matched_skills[:10]) if matched_skills else "None identified"
    missing_text = ", ".join(missing_skills[:10]) if missing_skills else "None identified"

    lines = [
        "ResumeAI Professional Feedback Report",
        "===================================",
        f"Candidate: {user_email}",
        f"Generated on: {today} UTC",
        "",
        f"Match Score: {score}%",
        f"Fit Level: {action_plan['level']}",
        f"Summary: {action_plan['headline']}",
        "",
        "Top Matched Skills:",
        matched_text,
        "",
        "Top Missing Skills:",
        missing_text,
        "",
        "Priority Actions:",
        f"1. {action_plan['priority_actions'][0]}",
        f"2. {action_plan['priority_actions'][1]}",
        f"3. {action_plan['priority_actions'][2]}",
        "",
        "30-Day Roadmap:",
        f"- {action_plan['week_plan'][0]}",
        f"- {action_plan['week_plan'][1]}",
        f"- {action_plan['week_plan'][2]}",
        f"- {action_plan['week_plan'][3]}",
        "",
        "Resume Improvement Checklist:",
        f"- {action_plan['resume_edits'][0]}",
        f"- {action_plan['resume_edits'][1]}",
        f"- {action_plan['resume_edits'][2]}",
    ]
    return "\n".join(lines)
