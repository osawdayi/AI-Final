# Fix Supabase Configuration Issue

## Problem
You're getting "Supabase configured: False" even though your .env file has correct credentials.

## Root Cause
The issue is a version incompatibility between the Supabase library and urllib3. The error is:
```
TypeError: __init__() got an unexpected keyword argument 'proxy'
```

## Solution

### Step 1: Fix urllib3 Version

Run these commands in your terminal:

```bash
cd /Users/osawdayi2022/Downloads/AI-Final

# Uninstall conflicting packages
pip3 uninstall -y urllib3 supabase

# Install compatible urllib3 version
pip3 install 'urllib3<2.0.0'

# Reinstall supabase
pip3 install supabase==2.3.4
```

### Step 2: Verify It Works

Test if Supabase can now initialize:

```bash
python3 -c "from supabase_client import supabase_service; print('Supabase configured:', supabase_service.is_configured())"
```

You should see: `Supabase configured: True`

### Step 3: Restart Your Flask Server

```bash
# Stop your current server (Ctrl+C)
python3 app.py
```

You should now see:
```
Supabase configured: True
```

## Alternative: Use Virtual Environment (Recommended)

If the above doesn't work, use a virtual environment to isolate dependencies:

```bash
cd /Users/osawdayi2022/Downloads/AI-Final

# Create virtual environment
python3 -m venv venv

# Activate it (Mac/Linux)
source venv/bin/activate

# Install dependencies with correct versions
pip install 'urllib3<2.0.0'
pip install -r requirements.txt

# Run the app
python app.py
```

## Verify Your .env File

Make sure your `.env` file in the project root has:

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... (your actual key)
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... (your actual service key)
```

**Important:** 
- NO quotes around values
- NO spaces around the `=` sign
- Values should NOT start with `your_` (those are placeholders)

## Still Not Working?

If it's still not working after fixing urllib3:

1. Check your terminal output when running `python3 app.py` - look for any error messages
2. Verify your Supabase credentials are correct in the Supabase dashboard
3. Make sure you've restarted the Flask server after updating dependencies

