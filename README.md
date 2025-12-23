# Kickoff Kings - Fantasy Football Predictions Website

A comprehensive fantasy football website that uses historical data to predict player performance and provides AI-powered draft assistance with user authentication and premium subscriptions.

## Features

- **Player Statistics Scraping**: Web scrapes ESPN NFL player statistics in real-time
- **Fantasy Points Calculator**: Calculates fantasy points based on ESPN's standard scoring rules
- **Player Predictions**: Predicts future season fantasy points using historical data
- **Draft Assistant**: Provides draft recommendations based on:
  - Number of teams in league
  - Your draft position
  - Already drafted players
  - Shows player name, team, position, position rank, and projected points
- **User Authentication**: Secure sign up and login powered by Supabase
- **Data Persistence**: Save draft sessions and player data in Supabase database
- **AI-Powered Analysis**: Premium feature using OpenAI for enhanced draft recommendations
- **Premium Subscriptions**: Stripe integration for subscription management

## Color Scheme

- **Red**: Primary color (#DC143C)
- **Black**: Background (#000000)
- **White**: Text and accents (#FFFFFF)
- **Gold**: Highlights and branding (#FFD700)

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
   - Copy `.env.example` to `.env` (or create `.env` file)
   - Fill in your API keys (see `INTEGRATION_SETUP.md` for detailed setup instructions)
   - Required keys:
     - `SUPABASE_URL` and `SUPABASE_KEY` (for database and auth)
     - `OPENAI_API_KEY` (for AI features)
     - `STRIPE_SECRET_KEY` and `STRIPE_PUBLISHABLE_KEY` (for payments)
     - `SECRET_KEY` (for Flask sessions)

3. Set up Supabase database:
   - Create a Supabase project
   - Run the SQL script in `supabase_schema.sql` in the Supabase SQL editor
   - This creates all necessary tables and security policies

4. Run the Flask application:
```bash
python app.py
```

5. Open your browser and navigate to:
```
http://localhost:5000
```

**See `INTEGRATION_SETUP.md` for detailed setup instructions for Supabase, OpenAI, and Stripe.**

## Usage

### Player Predictions
1. Click "Load Player Data" to scrape current ESPN statistics
2. Click "Generate Predictions" to see projected fantasy points for the upcoming season

### Draft Assistant
1. Enter your league settings:
   - Number of teams (8-16)
   - Your draft position
   - Games played in season
2. Add any players that have already been drafted
3. Click "Get Draft Recommendations" to see suggested picks
4. Click "Draft" on any player to add them to your drafted list

## Project Structure

```
AI-Final/
├── app.py                 # Flask backend application with API routes
├── config.py              # Configuration and environment variables
├── supabase_client.py     # Supabase client and database operations
├── openai_service.py      # OpenAI integration for AI features
├── stripe_service.py      # Stripe integration for payments
├── scraper.py             # ESPN web scraper
├── fantasy_calculator.py  # Fantasy points calculator
├── prediction_model.py    # Prediction model using historical data
├── supabase_schema.sql    # Database schema for Supabase
├── requirements.txt       # Python dependencies
├── .env.example           # Example environment variables file
├── INTEGRATION_SETUP.md   # Detailed setup guide for integrations
├── templates/
│   └── index.html        # Main HTML template
└── static/
    ├── css/
    │   └── style.css     # Styling
    └── js/
        └── app.js        # Frontend JavaScript with auth
```

## Fantasy Scoring Rules

Based on ESPN standard scoring:
- Passing Yards: 1 point per 25 yards
- Passing TDs: 4 points
- Rushing/Receiving Yards: 1 point per 10 yards
- Rushing/Receiving TDs: 6 points
- Receptions: 1 point (PPR)
- Fumbles Lost: -2 points
- Return TDs: 6 points
- Bonus points for milestone games (300+ passing yards, 100+ rushing/receiving yards, etc.)

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Create new user account
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout user
- `GET /api/auth/me` - Get current user info

### Draft & Predictions
- `POST /api/scrape` - Scrape and cache player data
- `POST /api/predictions` - Get player predictions
- `POST /api/draft-assistant` - Get draft recommendations (includes AI analysis for premium users)
- `GET /api/draft-sessions` - Get user's draft sessions
- `DELETE /api/draft-sessions/<id>` - Delete draft session

### Payments
- `POST /api/stripe/create-checkout` - Create Stripe checkout session
- `POST /api/stripe/create-portal` - Create customer portal session
- `POST /api/stripe/webhook` - Handle Stripe webhooks

## Notes

- The scraper includes fallback sample data for development/testing
- ESPN's website structure may change, requiring scraper updates
- The prediction model uses historical averages and trends
- Authentication and data persistence are now implemented via Supabase
- Premium features require an active Stripe subscription
- AI analysis is powered by OpenAI's GPT-4o-mini model

## License

© 2024 Kickoff Kings. All rights reserved.

