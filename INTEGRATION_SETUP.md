# Integration Setup Guide

This guide will help you set up Supabase, OpenAI, and Stripe integrations for the Kickoff Kings application.

## Prerequisites

1. Python 3.8+
2. pip package manager
3. Accounts for:
   - Supabase (free tier available)
   - OpenAI (API key required)
   - Stripe (developer account)

## Step 1: Supabase Setup

### 1.1 Create a Supabase Project

1. Go to [supabase.com](https://supabase.com) and sign up/login
2. Click "New Project"
3. Fill in project details:
   - Name: `kickoff-kings` (or your choice)
   - Database Password: (save this securely)
   - Region: Choose closest to you
4. Wait for project to be created (~2 minutes)

### 1.2 Get Supabase Credentials

1. In your Supabase project, go to **Settings** → **API**
2. Copy the following:
   - **Project URL** (SUPABASE_URL)
   - **anon/public key** (SUPABASE_KEY)
   - **service_role key** (SUPABASE_SERVICE_KEY) - Keep this secret!

### 1.3 Create Database Schema

1. In Supabase, go to **SQL Editor**
2. Open the file `supabase_schema.sql` from this project
3. Copy and paste the entire SQL script
4. Click **Run** to execute
5. Verify tables were created by going to **Table Editor**

### 1.4 Enable Email Authentication (Optional but Recommended)

1. Go to **Authentication** → **Providers**
2. Enable **Email** provider
3. Configure email templates if needed

## Step 2: OpenAI Setup

### 2.1 Get API Key

1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign up or log in
3. Go to **API Keys** section
4. Click **Create new secret key**
5. Copy the key (you won't see it again!)

### 2.2 Add Credits (if needed)

1. Go to **Billing** → **Payment methods**
2. Add a payment method
3. Set up usage limits if desired

## Step 3: Stripe Setup

### 3.1 Create Stripe Account

1. Go to [stripe.com](https://stripe.com) and sign up
2. Complete account verification
3. Switch to **Test mode** (toggle in top right)

### 3.2 Get API Keys

1. Go to **Developers** → **API keys**
2. Copy:
   - **Publishable key** (STRIPE_PUBLISHABLE_KEY)
   - **Secret key** (STRIPE_SECRET_KEY)

### 3.3 Create a Product and Price

1. Go to **Products** → **Add product**
2. Create a product:
   - Name: "Kickoff Kings Premium"
   - Description: "Premium subscription for AI-powered draft analysis"
3. Set pricing:
   - Model: Recurring
   - Price: $9.99/month (or your choice)
   - Billing period: Monthly
4. Copy the **Price ID** (looks like `price_xxxxx`) - This is your STRIPE_PREMIUM_PRICE_ID

### 3.4 Set Up Webhooks

1. Go to **Developers** → **Webhooks**
2. Click **Add endpoint**
3. Set endpoint URL: `https://yourdomain.com/api/stripe/webhook`
   - For local testing, use [ngrok](https://ngrok.com) or similar
4. Select events to listen for:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
5. Copy the **Signing secret** (STRIPE_WEBHOOK_SECRET)

## Step 4: Environment Variables

### 4.1 Create .env File

Create a `.env` file in the project root:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key_here
SUPABASE_SERVICE_KEY=your_service_role_key_here

# OpenAI Configuration
OPENAI_API_KEY=sk-your_openai_key_here

# Stripe Configuration
STRIPE_PUBLISHABLE_KEY=pk_test_your_key_here
STRIPE_SECRET_KEY=sk_test_your_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
STRIPE_PREMIUM_PRICE_ID=price_your_price_id_here

# Flask Configuration
SECRET_KEY=your_random_secret_key_here
FLASK_ENV=development
```

**Important**: Never commit the `.env` file to git! It's already in `.gitignore`.

### 4.2 Generate Secret Key

Generate a secure secret key for Flask:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Use the output as your `SECRET_KEY`.

## Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 6: Run the Application

```bash
python app.py
```

The application will run on `http://localhost:5000`

## Testing the Integrations

### Test Supabase Authentication

1. Open the application in your browser
2. Click "Sign Up" and create an account
3. Verify you can log in and see your user info
4. Check Supabase dashboard → **Authentication** → **Users** to see the new user

### Test Player Caching

1. Click "Load Player Predictions"
2. Check Supabase dashboard → **Table Editor** → **player_cache** to see cached data

### Test OpenAI Integration

1. Sign up for a premium account (or manually set subscription_tier to 'premium' in database)
2. Load player predictions
3. Get draft recommendations
4. Verify AI analysis appears below recommendations

### Test Stripe Integration

1. Click "Upgrade to Premium" (must be logged in)
2. Use Stripe test card: `4242 4242 4242 4242`
   - Any future expiry date
   - Any 3-digit CVC
   - Any ZIP code
3. Complete checkout
4. Verify subscription created in Stripe dashboard
5. Verify user subscription_tier updated in Supabase

## Troubleshooting

### Supabase Connection Issues

- Verify your SUPABASE_URL and SUPABASE_KEY are correct
- Check that RLS (Row Level Security) policies are set up correctly
- Ensure the database schema was created successfully

### OpenAI API Errors

- Verify your API key is correct
- Check your OpenAI account has credits/quota
- Ensure you're using a valid model name (default: `gpt-4o-mini`)

### Stripe Webhook Issues

- For local development, use ngrok: `ngrok http 5000`
- Update webhook URL in Stripe dashboard
- Verify webhook secret matches
- Check webhook logs in Stripe dashboard for errors

### Authentication Issues

- Clear browser localStorage if tokens get corrupted
- Check Supabase logs for authentication errors
- Verify email provider is enabled in Supabase

## Production Deployment

### Environment Variables

Set environment variables in your hosting platform (Heroku, Railway, AWS, etc.)

### Database Migrations

The `supabase_schema.sql` file contains all necessary tables. Run it once in production.

### Webhook URLs

Update Stripe webhook URLs to your production domain:
```
https://yourdomain.com/api/stripe/webhook
```

### CORS Configuration

Update CORS settings in your Flask app if needed for your frontend domain.

## Security Notes

1. **Never commit** `.env` file or API keys
2. Use **environment variables** in production
3. Keep **SUPABASE_SERVICE_KEY** and **STRIPE_SECRET_KEY** secure
4. Enable **RLS** on all Supabase tables (already done in schema)
5. Use **HTTPS** in production
6. Set up proper **CORS** policies
7. Validate all user inputs on the backend

## Support

For issues with:
- **Supabase**: Check [Supabase Docs](https://supabase.com/docs)
- **OpenAI**: Check [OpenAI Docs](https://platform.openai.com/docs)
- **Stripe**: Check [Stripe Docs](https://stripe.com/docs)

