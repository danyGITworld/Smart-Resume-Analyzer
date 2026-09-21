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

   


## Scope

Same rule-based approach as the notebook version - plain regex/keyword
matching, no deep learning or external AI APIs.
