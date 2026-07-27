# Smart Resume Analyzer (Flask Web App)

A small Flask web app version of the Smart Resume Analyzer capstone project.
Upload a resume (PDF/DOCX), pick a target role, and get a score, ATS keyword
match, and improvement suggestions - viewable at a real deployed URL.

## Run locally

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5000 in your browser.

## Deploy to Render (free tier)

1. Push this folder to a GitHub repo (see steps in the earlier zip's README,
   or use `git init && git add . && git commit -m "init"` then push to a new repo).
2. Go to https://render.com and sign up / log in (GitHub login works).
3. Click **New +** → **Web Service**.
4. Connect your GitHub repo.
5. Render should auto-detect the `render.yaml` and pre-fill settings. If not, set manually:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Plan:** Free
6. Click **Create Web Service**. First deploy takes a few minutes.
7. Once live, Render gives you a URL like `https://smart-resume-analyzer.onrender.com`
   - **this is your deployment link** for the assignment.

Note: Render's free tier spins down after ~15 min of inactivity and takes
~30-50 seconds to wake up on the next request - normal for a free-tier demo,
not a bug.

## Project structure

```
resume-analyzer-flask/
├── app.py                 # Flask app - routes + all analysis logic
├── templates/
│   ├── base.html
│   ├── index.html         # upload form
│   └── result.html        # report + charts
├── static/
│   └── style.css
├── requirements.txt
├── Procfile                # tells Render how to start the app
├── render.yaml              # Render blueprint config
└── .gitignore
```

## Scope

Same rule-based approach as the notebook version - plain regex/keyword
matching, no deep learning or external AI APIs, matching the assignment's
stated scope limits.
