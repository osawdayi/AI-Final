# Troubleshooting Guide

## Common Issues and Solutions

### "Authentication not configured" Error

This error means Supabase is not properly configured. Check the following:

#### 1. Check Your .env File

Make sure your `.env` file exists and has valid Supabase credentials:

```bash
# Check if .env file exists
ls -la .env

# View .env contents (be careful not to share these publicly!)
cat .env
```

Your `.env` file should have:
```
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your_anon_key_here
SUPABASE_SERVICE_KEY=your_service_role_key_here
```

#### 2. Verify Supabase Credentials

1. Go to your Supabase project dashboard
2. Navigate to **Settings** → **API**
3. Copy:
   - **Project URL** → This is your `SUPABASE_URL`
   - **anon public key** → This is your `SUPABASE_KEY`
   - **service_role key** → This is your `SUPABASE_SERVICE_KEY` (keep secret!)

#### 3. Check for Placeholder Values

Make sure your `.env` values are NOT placeholders like:
- ❌ `your_supabase_project_url`
- ❌ `your_supabase_anon_key`
- ✅ `https://abcdefghijk.supabase.co`
- ✅ `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

#### 4. Restart Your Flask Server

After updating `.env`, restart your Flask application:
```bash
# Stop the server (Ctrl+C)
# Then restart
python3 app.py
```

#### 5. Verify Supabase Client Initialization

Check the terminal output when starting the app. You should see:
- ✅ No error messages about Supabase
- ✅ Server starts successfully
- ❌ If you see "Supabase library not available" or "Failed to initialize Supabase client", check your configuration

### Google OAuth Redirect URI Mismatch

If you get "Redirect URI mismatch" error:

#### For Local Development with 127.0.0.1:

1. **In Google Cloud Console:**
   - Go to **APIs & Services** → **Credentials**
   - Click on your OAuth 2.0 Client ID
   - Under **Authorized redirect URIs**, make sure you have:
     - `http://127.0.0.1:5000/auth/callback`
     - `https://YOUR_PROJECT_ID.supabase.co/auth/v1/callback`

2. **In Supabase:**
   - Go to **Authentication** → **URL Configuration**
   - **Site URL**: `http://127.0.0.1:5000`
   - **Redirect URLs**: Add `http://127.0.0.1:5000/auth/callback`

#### Important Notes:
- Use `127.0.0.1` OR `localhost` consistently (don't mix them)
- Make sure the port matches (usually `5000`)
- The callback path must be exactly `/auth/callback`
- Supabase callback URL format: `https://YOUR_PROJECT_ID.supabase.co/auth/v1/callback`

### Testing Your Configuration

Run this Python script to test if Supabase is configured:

```python
from config import Config
from supabase_client import supabase_service

print("Checking Supabase configuration...")
print(f"SUPABASE_URL set: {bool(Config.SUPABASE_URL)}")
print(f"SUPABASE_KEY set: {bool(Config.SUPABASE_KEY)}")
print(f"Supabase configured: {supabase_service.is_configured()}")

if supabase_service.is_configured():
    print("✅ Supabase is properly configured!")
else:
    print("❌ Supabase is NOT configured. Check your .env file.")
```

Save this as `test_config.py` and run:
```bash
python3 test_config.py
```

### Still Having Issues?

1. **Check Flask Server Logs**: Look for error messages in your terminal
2. **Check Browser Console**: Open Developer Tools (F12) and check for JavaScript errors
3. **Verify Environment Variables**: Make sure `.env` file is in the project root directory
4. **Check File Permissions**: Ensure `.env` file is readable

### Quick Checklist

- [ ] `.env` file exists in project root
- [ ] `SUPABASE_URL` starts with `https://` and ends with `.supabase.co`
- [ ] `SUPABASE_KEY` is a long string (JWT token format)
- [ ] No placeholder text in `.env` values
- [ ] Flask server restarted after updating `.env`
- [ ] Google OAuth redirect URIs match exactly (including `http://` vs `https://`)
- [ ] Supabase Google provider is enabled
- [ ] Google OAuth credentials are added to Supabase



