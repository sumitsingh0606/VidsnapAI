# VidSnapAI 🎬

An AI-powered reel generator. Upload images/videos, add a voice-over text, and the app stitches them into a vertical Instagram-style reel with AI-generated speech.

---

## Project Structure

```
vidsnapai/
├── main.py                 # Flask web app
├── generate_process.py     # Background worker (ffmpeg + TTS)
├── text_to_audio.py        # ElevenLabs TTS helper
├── config.py               # Reads env vars (no secrets here)
├── requirements.txt        # Python dependencies
├── Procfile                # Railway process definitions
├── nixpacks.toml           # Tells Railway to install ffmpeg
├── railway.toml            # Railway deployment config
├── .gitignore              # Keeps secrets + uploads out of git
├── .env.example            # Template for local env vars
├── static/
│   ├── css/
│   │   ├── style.css
│   │   ├── create.css
│   │   └── gallery.css
│   └── reels/              # Generated reels saved here
└── templates/
    ├── base.html
    ├── index.html
    ├── create.html
    └── gallery.html
```

---

## Local Development Setup

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/vidsnapai.git
cd vidsnapai
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
cp .env.example .env
# Now edit .env and fill in your real values
```

Your `.env` file should look like:
```
ELEVENLABS_API_KEY=sk_xxxxxxxxxxxxxxxxxxxxx
SECRET_KEY=any-random-string-you-make-up
FLASK_DEBUG=true
```

> ⚠️ Never commit `.env` — it's in `.gitignore`

### 5. Install ffmpeg locally
- **Mac:** `brew install ffmpeg`
- **Ubuntu/Debian:** `sudo apt install ffmpeg`
- **Windows:** Download from https://ffmpeg.org/download.html and add to PATH

### 6. Run the app
Open **two terminals**:

**Terminal 1 — Web server:**
```bash
python main.py
```

**Terminal 2 — Background worker:**
```bash
python generate_process.py
```

Visit http://localhost:5000

---

## Deploying to GitHub

### First-time setup
```bash
git init
git add .
git commit -m "Initial commit"
```

### Create a GitHub repo
1. Go to https://github.com/new
2. Name it `vidsnapai`, keep it public or private
3. **Do NOT** initialize with README (you already have one)

### Push to GitHub
```bash
git remote add origin https://github.com/YOUR_USERNAME/vidsnapai.git
git branch -M main
git push -u origin main
```

---

## Deploying to Railway

### Step 1 — Sign up / log in
Go to https://railway.app and log in with your GitHub account.

### Step 2 — Create a new project
1. Click **New Project**
2. Select **Deploy from GitHub repo**
3. Choose your `vidsnapai` repository
4. Railway will auto-detect it as a Python project

### Step 3 — Set environment variables
In your Railway project dashboard:
1. Click on your service → **Variables** tab
2. Add these variables one by one:

| Variable | Value |
|---|---|
| `ELEVENLABS_API_KEY` | Your ElevenLabs API key |
| `SECRET_KEY` | Any random string (e.g. generate with `python -c "import secrets; print(secrets.token_hex(32))"`) |
| `FLASK_DEBUG` | `false` |

> ✅ This is the safe way — secrets never touch your code or git history.

### Step 4 — Add the worker service (for reel generation)
Railway needs to run two processes: the web server and the background worker.

1. In your project, click **+ New Service** → **GitHub Repo** (same repo)
2. In this second service's settings, go to **Settings → Start Command**
3. Set it to: `python generate_process.py`
4. Add the same environment variables to this service too

> Alternatively, Railway Pro plans support `Procfile` workers automatically.

### Step 5 — Add a volume for persistent storage
User uploads and generated reels need to survive deploys:

1. In your Railway project, click **+ New** → **Volume**
2. Mount it to your web service at path `/app/user_uploads`
3. Add another volume mounted at `/app/static/reels`

### Step 6 — Deploy
Railway auto-deploys on every `git push`. To trigger a manual deploy:
- Go to your service → **Deployments** → **Deploy Now**

### Step 7 — Get your public URL
In the Railway dashboard, go to your web service → **Settings** → **Networking** → **Generate Domain**.

You'll get a URL like: `https://vidsnapai-production.up.railway.app`

---

## Environment Variables Reference

| Variable | Required | Description |
|---|---|---|
| `ELEVENLABS_API_KEY` | ✅ Yes | Your ElevenLabs API key |
| `SECRET_KEY` | ✅ Yes | Flask session secret (any random string) |
| `FLASK_DEBUG` | No | Set `true` only for local dev |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Web Framework | Flask |
| Video Processing | FFmpeg |
| Text-to-Speech | ElevenLabs API |
| Production Server | Gunicorn |
| Hosting | Railway |
