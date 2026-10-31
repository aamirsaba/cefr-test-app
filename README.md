# CEFR Placement Test App

A complete web-based CEFR English placement test with SQLite database.

## 🚀 Local Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Initialize the database (creates cefr_test.db with 50 questions)
python init_db.py

# 3. Run the app
python app.py
```

Visit **http://localhost:5000**

Admin panel: **http://localhost:5000/admin**

## 🌐 Hosting Options

### Option A: PythonAnywhere (Easiest - Free tier available)
1. Sign up at pythonanywhere.com
2. Open a Bash console, upload files via web editor or git
3. Run: `pip install flask`, `python init_db.py`
4. Go to "Web" tab → Add a new web app → Manual → Python 3.10
5. Set source code to your folder, WSGI file to `app.py`
6. Reload → Live!

### Option B: Render.com (Free tier)
1. Push code to GitHub
2. New → Web Service → Connect repo
3. Build: `pip install -r requirements.txt && python init_db.py`
4. Start: `gunicorn app:app` (add `gunicorn` to requirements.txt)

### Option C: Railway / Heroku
Same as Render — push to Git, set build/start commands.

### Option D: Any VPS / Shared Hosting with Python
```bash
git clone <your-repo>
cd cefr-test-app
pip install -r requirements.txt
python init_db.py
# Use gunicorn + nginx for production
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 📊 Features
- ✅ 50 CEFR-graded questions across 3 sections
- ✅ Automatic CEFR level (A0 → B2+) and module assignment
- ✅ SQLite database — no external DB server needed
- ✅ Stores every attempt with per-section breakdown
- ✅ Admin dashboard at `/admin` to view all results
- ✅ Answer review after submission
- ✅ Mobile-responsive design