# Deployment Guide - Nissan Chatbot

This guide covers deploying the Nissan Chatbot to production.

## Architecture

- **Frontend**: Next.js → Deploy to Vercel
- **Backend**: FastAPI → Deploy to Railway or Render

---

## Option 1: Railway (Recommended - Easiest)

### Deploy Backend to Railway

1. **Create Railway Account**: Go to [railway.app](https://railway.app) and sign up

2. **Install Railway CLI** (optional):
   ```bash
   npm install -g @railway/cli
   railway login
   ```

3. **Deploy via GitHub**:
   - Push your code to GitHub
   - In Railway dashboard, click "New Project" → "Deploy from GitHub repo"
   - Select the repository
   - Set the root directory to `backend`

4. **Set Environment Variables** in Railway dashboard:
   ```
   OPENAI_API_KEY=your-openai-api-key
   OPENAI_ASSISTANT_ID=asst_OyXxiGYqXAfNKSvxDsPSLVg6
   OPENAI_VECTOR_STORE_ID=vs_693dc84e90408191a3c97593df1db311
   FRONTEND_URL=https://your-frontend.vercel.app
   ```

5. **Get your Backend URL**: Railway will provide a URL like `https://your-app.railway.app`

### Deploy Frontend to Vercel

1. **Create Vercel Account**: Go to [vercel.com](https://vercel.com) and sign up

2. **Deploy via GitHub**:
   - In Vercel dashboard, click "Add New" → "Project"
   - Import your GitHub repository
   - Set the root directory to `frontend`

3. **Set Environment Variables** in Vercel dashboard:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.railway.app
   ```

4. **Deploy**: Click Deploy and wait for build to complete

---

## Option 2: Render

### Deploy Backend to Render

1. **Create Render Account**: Go to [render.com](https://render.com) and sign up

2. **Create New Web Service**:
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Set root directory to `backend`
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn api:app --host 0.0.0.0 --port $PORT`

3. **Set Environment Variables**:
   ```
   OPENAI_API_KEY=your-openai-api-key
   OPENAI_ASSISTANT_ID=asst_OyXxiGYqXAfNKSvxDsPSLVg6
   OPENAI_VECTOR_STORE_ID=vs_693dc84e90408191a3c97593df1db311
   FRONTEND_URL=https://your-frontend.vercel.app
   ```

4. **Deploy**: Render will automatically deploy

---

## Environment Variables Reference

### Backend (.env)
```
OPENAI_API_KEY=sk-...
OPENAI_ASSISTANT_ID=asst_...
OPENAI_VECTOR_STORE_ID=vs_...
DEEPGRAM_API_KEY=your-deepgram-key (optional, for voice)
ELEVENLABS_API_KEY=your-elevenlabs-key (optional, for voice)
ELEVENLABS_VOICE_ID=your-voice-id (optional)
FRONTEND_URL=https://your-frontend.vercel.app
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

---

## Post-Deployment Checklist

- [ ] Backend health check: `https://your-backend.railway.app/health`
- [ ] Frontend loads correctly
- [ ] Chat widget appears and opens
- [ ] Chat messages stream properly
- [ ] CORS is configured correctly (no console errors)

---

## Updating CORS for Production

The backend already allows all origins (`*`). For production security, update `backend/api.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend.vercel.app",
        "https://your-custom-domain.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Custom Domain (Optional)

### Vercel
1. Go to Project Settings → Domains
2. Add your custom domain
3. Update DNS records as instructed

### Railway
1. Go to Service Settings → Networking
2. Add custom domain
3. Update DNS records as instructed

---

## Troubleshooting

### Chat not connecting
- Check browser console for CORS errors
- Verify NEXT_PUBLIC_API_URL is set correctly
- Check backend health endpoint

### Streaming not working
- Ensure backend is running latest code
- Check for proxy/CDN buffering issues
- Verify SSE headers are not being modified

### Images not loading
- Ensure Nissan CDN is accessible
- Check Next.js image configuration
