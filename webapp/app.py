"""
Smart Resume Analyzer - Flask Web App
--------------------------------------
Same core logic as the Colab notebook (parsing, scoring, ATS keyword
checking, feedback generation) wrapped in a small Flask web app so it
can be deployed with a public URL (e.g. on Render).

Routes:
    GET  /            -> upload form (choose file + target role)
    POST /analyze      -> runs the pipeline and shows the report + charts
"""

import re
import io
import string
import base64

import pdfplumber
import docx
import matplotlib
matplotlib.use("Agg")  # non-interactive backend, required for servers (no display)
import matplotlib.pyplot as plt

from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "dev-secret-key"  # only used for flash messages; fine for a student project

ALLOWED_EXTENSIONS = {"pdf", "docx"}
MAX_FILE_SIZE_MB = 5
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE_MB * 1024 * 1024


# --------------------------------------------------------------------------
# Module 1: Resume Upload and Parsing
# --------------------------------------------------------------------------

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_pdf(file_stream):
    """Extract text from an in-memory PDF file (no disk write needed)."""
    text = ""
    with pdfplumber.open(file_stream) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def extract_text_from_docx(file_stream):
    """Extract text from an in-memory DOCX file."""
    document = docx.Document(file_stream)
    return "\n".join(p.text for p in document.paragraphs)


def parse_resume(file_storage):
    """
    file_storage: Werkzeug FileStorage object from request.files
    Returns extracted text, or raises ValueError on bad input.
    """
    filename = file_storage.filename
    if not filename or not allowed_file(filename):
        raise ValueError("Please upload a PDF or DOCX file.")

    file_bytes = io.BytesIO(file_storage.read())

    if filename.lower().endswith(".pdf"):
        text = extract_text_from_pdf(file_bytes)
    else:
        text = extract_text_from_docx(file_bytes)

    if not text.strip():
        raise ValueError("Could not extract text. The file may be a scanned/image-only PDF.")

    return filename, text


# --------------------------------------------------------------------------
# Module 2: Resume Score Analyzer
# --------------------------------------------------------------------------

def check_contact_info(text):
    email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    phone_pattern = r"(\+?\d{1,3}[-.\s]?)?\(?\d{3,5}\)?[-.\s]?\d{3}[-.\s]?\d{3,4}"

    has_email = bool(re.search(email_pattern, text))
    has_phone = bool(re.search(phone_pattern, text))

    score = (8 if has_email else 0) + (7 if has_phone else 0)
    return score, {"email_found": has_email, "phone_found": has_phone}


def check_section_presence(text):
    text_lower = text.lower()
    sections = {
        "education":      ["education", "academic", "qualification"],
        "skills":         ["skills", "technical skills", "competencies"],
        "projects":       ["projects", "project work"],
        "experience":     ["experience", "internship", "work history"],
        "certifications": ["certification", "certifications", "courses"],
    }
    found = {s: any(kw in text_lower for kw in kws) for s, kws in sections.items()}
    weights = {"education": 15, "skills": 15, "projects": 15, "experience": 10, "certifications": 10}
    score = sum(weights[s] for s, present in found.items() if present)
    return score, found


def check_resume_completeness(text):
    word_count = len(text.split())
    if word_count < 100:
        return 3, word_count
    elif word_count < 250:
        return 9, word_count
    return 15, word_count


def analyze_resume_score(text):
    contact_score, contact_details = check_contact_info(text)
    section_score, section_details = check_section_presence(text)
    completeness_score, word_count = check_resume_completeness(text)

    completeness_scaled = round((completeness_score / 15) * 20)
    total = min(contact_score + section_score + completeness_scaled, 100)

    breakdown = {
        "Contact Information (out of 15)": contact_score,
        "Resume Sections (out of 65)": section_score,
        "Completeness (out of 20)": completeness_scaled,
    }
    details = {"contact": contact_details, "sections": section_details, "word_count": word_count}
    return total, breakdown, details


# --------------------------------------------------------------------------
# Module 3: ATS Keyword Checker
# --------------------------------------------------------------------------

ROLE_KEYWORDS = {
    "Data Analyst": ["sql", "excel", "python", "power bi", "tableau", "data cleaning",
                      "statistics", "pandas", "numpy", "data visualization", "reporting"],
    "Web Developer": ["html", "css", "javascript", "react", "node.js", "rest api",
                       "git", "responsive design", "mongodb", "sql"],
    "AI Engineer": ["python", "machine learning", "deep learning", "tensorflow",
                     "pytorch", "nlp", "computer vision", "scikit-learn", "data preprocessing"],
    "Cloud Engineer": ["aws", "azure", "gcp", "docker", "kubernetes", "ci/cd",
                        "terraform", "linux", "networking", "cloud security"],
}


def preprocess_text(text):
    text = text.lower()
    return text.translate(str.maketrans("", "", string.punctuation))


def check_ats_keywords(text, role):
    processed = preprocess_text(text)
    required = ROLE_KEYWORDS[role]
    matched = [kw for kw in required if kw in processed]
    missing = [kw for kw in required if kw not in processed]
    pct = round((len(matched) / len(required)) * 100)
    return matched, missing, pct


# --------------------------------------------------------------------------
# Module 4: Smart Feedback System
# --------------------------------------------------------------------------

def generate_feedback(score_details, missing_keywords, ats_score):
    suggestions = []
    contact = score_details["contact"]
    sections = score_details["sections"]

    if not contact["email_found"]:
        suggestions.append("Add a professional email address to your contact section.")
    if not contact["phone_found"]:
        suggestions.append("Add a phone number so recruiters can reach you.")
    if not sections["education"]:
        suggestions.append("Add an Education section with your degree and institution.")
    if not sections["skills"]:
        suggestions.append("Add a dedicated Skills section listing your technical skills.")
    if not sections["projects"]:
        suggestions.append("Include a Projects section - this is heavily weighted by recruiters.")
    if not sections["experience"]:
        suggestions.append("Consider adding an Internship/Experience section.")
    if not sections["certifications"]:
        suggestions.append("List relevant certifications or online courses.")
    if score_details["word_count"] < 250:
        suggestions.append("Your resume looks short - add more detail to projects and skills.")
    if missing_keywords:
        suggestions.append(
            f"Add these role-relevant keywords to improve ATS match: {', '.join(missing_keywords[:5])}."
        )
    if ats_score < 50:
        suggestions.append("Low keyword overlap for this role - consider tailoring your resume to the job description.")
    if not suggestions:
        suggestions.append("Great job! Your resume covers all key areas well.")
    return suggestions


# --------------------------------------------------------------------------
# Module 5: Dashboard (chart generation as base64 images for HTML embedding)
# --------------------------------------------------------------------------

def make_score_chart(breakdown):
    labels = list(breakdown.keys())
    values = list(breakdown.values())
    max_values = [15, 65, 20]

    fig, ax = plt.subplots(figsize=(5, 4))
    ax.bar(labels, values, color="#6C5CE7")
    ax.bar(labels, [m - v for m, v in zip(max_values, values)], bottom=values, color="#DFE6E9")
    ax.set_ylabel("Points")
    ax.set_title("Resume Score Breakdown")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    return fig_to_base64(fig)


def make_ats_chart(matched, missing, role, ats_score):
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.pie([len(matched), len(missing)], labels=["Matched", "Missing"],
           autopct="%1.0f%%", colors=["#00B894", "#D63031"], startangle=90)
    ax.set_title(f"ATS Match for {role} ({ats_score}%)")
    plt.tight_layout()
    return fig_to_base64(fig)


def fig_to_base64(fig):
    """Convert a matplotlib figure to a base64 PNG string for embedding in HTML."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100)
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


# --------------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------------

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", roles=list(ROLE_KEYWORDS.keys()))


@app.route("/analyze", methods=["POST"])
def analyze():
    file = request.files.get("resume")
    role = request.form.get("role")

    if not file or file.filename == "":
        flash("Please choose a resume file to upload.")
        return redirect(url_for("index"))

    if role not in ROLE_KEYWORDS:
        flash("Please select a valid target role.")
        return redirect(url_for("index"))

    try:
        filename, text = parse_resume(file)
    except ValueError as e:
        flash(str(e))
        return redirect(url_for("index"))

    score, breakdown, details = analyze_resume_score(text)
    matched, missing, ats_score = check_ats_keywords(text, role)
    feedback = generate_feedback(details, missing, ats_score)

    score_chart = make_score_chart(breakdown)
    ats_chart = make_ats_chart(matched, missing, role, ats_score)

    return render_template(
        "result.html",
        filename=filename,
        role=role,
        score=score,
        breakdown=breakdown,
        matched=matched,
        missing=missing,
        ats_score=ats_score,
        feedback=feedback,
        score_chart=score_chart,
        ats_chart=ats_chart,
    )


if __name__ == "__main__":
    # Local dev server. On Render, gunicorn serves the app instead (see Procfile).
    app.run(debug=True)
