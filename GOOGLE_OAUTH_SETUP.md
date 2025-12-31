# Google OAuth Setup Guide

This guide will help you set up Google OAuth authentication for your Kickoff Kings application using Supabase.

## Step 1: Create Google OAuth Credentials

1. **Go to Google Cloud Console**
   - Visit [Google Cloud Console](https://console.cloud.google.com/)
   - Sign in with your Google account

2. **Create a New Project (or select existing)**
   - Click the project dropdown at the top
   - Click "New Project"
   - Name it: `Kickoff Kings` (or your choice)
   - Click "Create"

3. **Enable Google+ API**
   - In the left sidebar, go to **APIs & Services** → **Library**
   - Search for "Google+ API"
   - Click on it and click **Enable**

4. **Create OAuth 2.0 Credentials**
   - Go to **APIs & Services** → **Credentials**
   - Click **+ CREATE CREDENTIALS** → **OAuth client ID**
   - If prompted, configure the OAuth consent screen first:
     - User Type: **External** (unless you have a Google Workspace)
     - App name: `Kickoff Kings`
     - User support email: Your email
     - Developer contact: Your email
     - Click **Save and Continue**
     - Scopes: Click **Save and Continue** (default scopes are fine)
     - Test users: Add your email, then **Save and Continue**

5. **Create OAuth Client ID**
   - Application type: **Web application**
   - Name: `Kickoff Kings Web Client`
   - **Authorized JavaScript origins:**
     - `http://127.0.0.1:5000` (for local development - use this if you're using 127.0.0.1)
     - `http://localhost:5000` (alternative for local development)
     - `https://yourdomain.com` (for production)
   - **Authorized redirect URIs:**
     - `http://127.0.0.1:5000/auth/callback` (for local development - use this if you're using 127.0.0.1)
     - `http://localhost:5000/auth/callback` (alternative for local development)
     - `https://yourdomain.com/auth/callback` (for production)
     - **Important:** Also add your Supabase project URL: `https://YOUR_PROJECT_ID.supabase.co/auth/v1/callback`
       (Replace YOUR_PROJECT_ID with your actual Supabase project reference ID)
   - Click **Create**

6. **Copy Your Credentials**
   - Copy the **Client ID** (looks like: `xxxxx.apps.googleusercontent.com`)
   - Copy the **Client Secret** (you'll need this for Supabase)

## Step 2: Configure Supabase

1. **Go to Supabase Dashboard**
   - Navigate to your project
   - Go to **Authentication** → **Providers**

2. **Enable Google Provider**
   - Find **Google** in the list
   - Toggle it to **Enabled**

3. **Add Google OAuth Credentials**
   - **Client ID (for OAuth)**: Paste your Google Client ID
   - **Client Secret (for OAuth)**: Paste your Google Client Secret
   - Click **Save**

4. **Configure Redirect URLs**
   - In Supabase, go to **Authentication** → **URL Configuration**
   - **Site URL**: `http://localhost:5000` (or your production URL)
   - **Redirect URLs**: Add:
     - `http://localhost:5000/auth/callback`
     - `https://yourdomain.com/auth/callback` (for production)

## Step 3: Update Your Application

The code has already been updated to support Google OAuth. The integration includes:

- **Google Login Button**: Added to login and signup modals
- **OAuth Endpoint**: `/api/auth/google` - generates the OAuth URL
- **Callback Handler**: `/auth/callback` - handles the OAuth redirect
- **Frontend Integration**: JavaScript function `loginWithGoogle()` handles the OAuth flow

## Step 4: Test Google OAuth

1. **Start your Flask application:**
   ```bash
   python3 app.py
   ```

2. **Test the login:**
   - Click "Login" or "Sign Up"
   - Click "Continue with Google"
   - You should be redirected to Google's login page
   - Sign in with your Google account
   - You'll be redirected back to your app
   - You should be logged in!

## Troubleshooting

### "Redirect URI mismatch" Error

- Make sure the redirect URI in Google Cloud Console exactly matches:
  - `http://localhost:5000/auth/callback` (local)
  - `https://yourdomain.com/auth/callback` (production)
- Also ensure Supabase callback URL is added: `https://YOUR_PROJECT.supabase.co/auth/v1/callback`

### "OAuth client not found" Error

- Verify your Client ID and Client Secret in Supabase are correct
- Make sure you copied the entire Client ID (including `.apps.googleusercontent.com`)

### User Not Logging In After OAuth

- Check browser console for errors (F12)
- Verify Supabase is properly configured
- Check that the callback URL is correct in both Google Console and Supabase

### OAuth Consent Screen Issues

- If using "External" user type, make sure you've added test users
- The app must be published or in testing mode with test users

## Production Deployment

When deploying to production:

1. **Update Google OAuth Credentials:**
   - Add your production domain to "Authorized JavaScript origins"
   - Add your production callback URL to "Authorized redirect URIs"

2. **Update Supabase:**
   - Update Site URL to your production domain
   - Add production callback URL to Redirect URLs

3. **Publish Your OAuth App (if needed):**
   - In Google Cloud Console, go to **OAuth consent screen**
   - Click **PUBLISH APP** if you want it available to all users
   - Or keep it in testing mode and add users as test users

## Security Notes

- Never commit OAuth credentials to git
- Keep your Client Secret secure (only stored in Supabase)
- Use HTTPS in production
- Regularly rotate your OAuth credentials
- Monitor OAuth usage in Google Cloud Console

## Additional Resources

- [Supabase OAuth Documentation](https://supabase.com/docs/guides/auth/social-login/auth-google)
- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Google Cloud Console](https://console.cloud.google.com/)

