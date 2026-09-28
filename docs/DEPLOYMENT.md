# AI StudyBuddy — Deployment Guide (Vercel & Cloud Hosting)

This guide walks through deploying the AI StudyBuddy platform to production so anyone on the web can use it.

---

## Architecture in Production

```
┌───────────────────────────────────────┐
│        Vercel (Global Edge CDN)       │
│      React + Vite + Tailwind UI       │
│  (https://ai-study-buddy.vercel.app)  │
└──────────────────┬────────────────────┘
                   │ HTTPS API Calls (Bearer JWT)
                   ▼
┌───────────────────────────────────────┐
│     Render / Railway / Cloud VM       │
│       FastAPI + SQLAlchemy DB         │
│     (https://api.yourdomain.com)      │
└──────────────────┬────────────────────┘
                   │
                   ▼
┌───────────────────────────────────────┐
│        Google Gemini 3.8 Flash        │
│          (Google Cloud AI)            │
└───────────────────────────────────────┘
```

---

## 1. Deploy Frontend to Vercel (1-Click)

### Step 1: Push Repository to GitHub
Ensure the codebase is pushed to your GitHub repository:
`https://github.com/karthikeyan-s0/AI-study-buddy.git`

### Step 2: Import into Vercel
1. Go to [https://vercel.com](https://vercel.com) and log in with your GitHub account.
2. Click **"Add New..."** → **"Project"**.
3. Select **`AI-study-buddy`** from your repository list.

### Step 3: Configure Build & Environment Settings
- **Framework Preset**: `Vite` (Auto-detected)
- **Root Directory**: Leave as `./` (or select `frontend` if deploying only the frontend)
- **Build Command**: `cd frontend && npm install && npm run build` (Pre-configured via `vercel.json`)
- **Output Directory**: `frontend/dist`
- **Environment Variables**:
  - `VITE_API_URL`: Your deployed backend URL (e.g., `https://ai-study-buddy-api.onrender.com` or `http://localhost:8000` for testing).

### Step 4: Click Deploy
Vercel will compile the Vite React application and assign you a live HTTPS domain:  
`https://ai-study-buddy-xxxx.vercel.app`

---

## 2. Deploy Backend (Render / Railway / Koyeb)

The backend runs as a continuous FastAPI application with persistent storage for SQLite/PostgreSQL.

### Deploying to Render (Free Tier):
1. Go to [https://render.com](https://render.com) and click **"New +"** → **"Web Service"**.
2. Connect your GitHub repository: `AI-study-buddy`.
3. Configure the service:
   - **Root Directory**: `backend`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
4. Add Environment Variables:
   - `GEMINI_API_KEY`: `<Your Gemini API Key>`
   - `GEMINI_MODEL`: `gemini-3.8-flash`
   - `SECRET_KEY`: `<A secure random string>`
   - `DATABASE_URL`: `sqlite:///./studybuddy.db`
5. Click **"Create Web Service"**.
6. Once deployed, copy your Render URL (e.g. `https://ai-study-buddy-api.onrender.com`) and paste it into your Vercel project's `VITE_API_URL` environment variable!
