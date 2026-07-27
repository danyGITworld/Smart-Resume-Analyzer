# Smart Resume Analyzer

AI Capstone Project — analyzes a resume (PDF/DOCX), scores it, checks it
against role-specific ATS keywords, and generates improvement suggestions.

This repo has two versions of the same core logic:

| Folder | What it is | Use it for |
|---|---|---|
| [`notebook/`](./notebook) | Google Colab notebook | Running/demoing the analysis step-by-step, submitting notebook output |
| [`webapp/`](./webapp) | Flask web app | Getting a live deployment link (Render) for the assignment's "Deployment" deliverable |

## Quick links

- **Run in Colab:** open `notebook/Smart_Resume_Analyzer.ipynb` in Google Colab
- **Run the web app locally / deploy it:** see [`webapp/README.md`](./webapp/README.md)

## What it does

1. **Upload & Parse** — reads text from a PDF or DOCX resume
2. **Resume Score Analyzer** — rule-based score out of 100 (contact info, sections, completeness)
3. **ATS Keyword Checker** — compares resume text against keyword banks for a chosen role
   (Data Analyst, Web Developer, AI Engineer, Cloud Engineer)
4. **Smart Feedback System** — plain-language improvement suggestions
5. **Dashboard** — score breakdown chart + ATS keyword match chart


