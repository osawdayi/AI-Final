# Vercel Deployment Guide for Flask Application

## Vercel Settings Configuration

Based on your project setup, here's what to fill in on the Vercel deployment page:

### Framework Preset
**Select: "Other"** (Vercel doesn't have native Flask support, but we can deploy it as a serverless function)

### Root Directory
**Keep as: `./`** (the root directory)

### Build Command
**Leave as: "None"** (or empty)

### Output Directory
**Leave as: "N/A"** or empty

### Install Command
**Set to: `pip install -r requirements.txt`**

### Environment Variables

Add ALL of these environment variables in the Vercel dashboard:

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key_here
SUPABASE_SERVICE_KEY=your_service_role_key_here
OPENAI_API_KEY=sk-your_openai_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_key_here
STRIPE_SECRET_KEY=sk_test_your_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
STRIPE_PREMIUM_PRICE_ID=price_your_price_id_here
SECRET_KEY=your_random_secret_key_here
FLASK_ENV=production
```

**Important Notes:**
- Replace all the placeholder values with your actual keys
- For Stripe webhook, update the webhook URL in Stripe dashboard to: `https://your-vercel-domain.vercel.app/api/stripe/webhook`
- The SECRET_KEY should be a long random string (generate with: `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`)

## Alternative: Simpler Deployment (Recommended)

Actually, Vercel has some limitations with Flask. Consider these alternatives:

### Option 1: Railway (Easiest for Flask)
Railway.app is specifically designed for Flask applications and is easier to set up:
1. Go to railway.app
2. Connect GitHub repo
3. Add environment variables
4. Deploy - that's it!

### Option 2: Render (Free Tier Available)
1. Go to render.com
2. Create new Web Service
3. Connect GitHub repo
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `gunicorn app:app`
6. Add environment variables
7. Deploy

### Option 3: Fly.io (Good for Flask)
1. Install flyctl CLI
2. Run `fly launch`
3. Add secrets with `fly secrets set KEY=value`
4. Deploy

## If You Still Want to Use Vercel

The files `vercel.json` and `api/index.py` have been created for you. However, note that:

1. **Vercel's Python runtime has limitations:**
   - 10 second timeout for Hobby plan (60s for Pro)
   - May not work well with long-running operations (like web scraping)
   - Some Flask features may not work perfectly

2. **For your app specifically:**
   - Web scraping might timeout on Vercel
   - Database operations should work fine
   - API endpoints should work
   - Static files should work

## Recommended Deployment Platforms (Ranked)

1. **Railway** ⭐ (Best for Flask)
   - Free tier available
   - Easy setup
   - Built for Python/Flask
   - No special configuration needed

2. **Render** ⭐ (Good free tier)
   - Free tier with limitations
   - Easy setup
   - Good documentation

3. **Fly.io** ⭐ (Powerful)
   - Generous free tier
   - Good for Python apps
   - Global deployment

4. **Heroku** (Paid only now)
   - Easy but requires payment
   - Good documentation

5. **Vercel** (Limited)
   - Better for static sites/Next.js
   - Possible but not ideal for Flask
   - Serverless functions have timeouts

## Next Steps

If using Vercel:
1. Fill in the settings as described above
2. Add all environment variables
3. Click Deploy
4. Update Stripe webhook URL to your Vercel domain

If using Railway/Render (Recommended):
1. Create account on Railway or Render
2. Connect GitHub repository
3. Add environment variables
4. Deploy
5. Update Stripe webhook URL

