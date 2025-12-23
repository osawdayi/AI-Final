# Kickoff Kings - Fantasy Football Predictions Website

A comprehensive fantasy football website that uses historical data to predict player performance and provides draft assistance.

## Features

- **Player Statistics Scraping**: Web scrapes ESPN NFL player statistics in real-time
- **Fantasy Points Calculator**: Calculates fantasy points based on ESPN's standard scoring rules
- **Player Predictions**: Predicts future season fantasy points using historical data
- **Draft Assistant**: Provides draft recommendations based on:
  - Number of teams in league
  - Your draft position
  - Already drafted players
  - Shows player name, team, position, position rank, and projected points

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

2. Run the Flask application:
```bash
python app.py
```

3. Open your browser and navigate to:
```
http://localhost:5000
```

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
Capstone-Website/
├── app.py                 # Flask backend application
├── scraper.py             # ESPN web scraper
├── fantasy_calculator.py  # Fantasy points calculator
├── prediction_model.py    # Prediction model using historical data
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Main HTML template
└── static/
    ├── css/
    │   └── style.css     # Styling
    └── js/
        └── app.js        # Frontend JavaScript
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

## Notes

- The scraper includes fallback sample data for development/testing
- ESPN's website structure may change, requiring scraper updates
- The prediction model uses historical averages and trends
- For production use, consider adding authentication and data persistence

## License

© 2024 Kickoff Kings. All rights reserved.

