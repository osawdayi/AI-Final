# How to Use the Draft Recommendations and AI Features

## Step-by-Step Guide

### Step 1: Load Player Predictions First
**IMPORTANT:** You MUST click "Load Player Predictions" BEFORE "Get Draft Recommendations"

1. Scroll to the **Draft Assistant** section (main section on the homepage)
2. Click the **"Load Player Predictions"** button
3. Wait for it to load (you'll see a loading message)
4. The "Get Draft Recommendations" button will become enabled (no longer grayed out)

### Step 2: Get Draft Recommendations
1. After loading predictions, click **"Get Draft Recommendations"**
2. The recommendations table will appear **directly below the button**
3. You'll see a table with:
   - Rank
   - Player Name
   - Team
   - Position
   - Position Rank
   - Projected Points
   - Draft button

### Step 3: View AI Features (Premium Users Only)
**As a premium user, you'll see AI features appear below the recommendations table:**

1. **🤖 AI Draft Analysis** - Appears automatically when you get recommendations
   - Shows strategic advice
   - Which players to target
   - Position strategy
   - Sleepers and value picks

2. **🎯 Personalized Draft Strategy** - Appears when you have drafted players
   - Add some players to "Already Drafted Players" 
   - Get recommendations again
   - Strategy section will appear above the AI Analysis

## Where to Find Everything

### Location on Page:
```
Homepage
└── Draft Assistant Section (main section)
    ├── Draft Settings (Number of Teams, Draft Position)
    ├── Load Player Predictions button
    ├── Already Drafted Players section
    ├── Get Draft Recommendations button
    ├── Draft Info (Current Pick, Round) ← appears after getting recommendations
    ├── Recommendations Table ← appears here
    ├── 🎯 Personalized Draft Strategy (Premium, if players drafted) ← appears here
    └── 🤖 AI Draft Analysis (Premium) ← appears here
```

## Troubleshooting

### Nothing appears when I click "Get Draft Recommendations"
**Solution:** Make sure you clicked "Load Player Predictions" FIRST. The button should be enabled (not grayed out).

### I don't see the AI Analysis
**Possible reasons:**
1. You're not logged in as a premium user
2. OpenAI API key is not configured
3. Check browser console (F12) for errors

### The table is empty
**Possible reasons:**
1. Player data didn't load correctly
2. All players are marked as drafted
3. Check browser console (F12) for errors

### I can't see the recommendations table
**Solution:** Scroll down! The table appears directly below the "Get Draft Recommendations" button. Make sure you're looking in the Draft Assistant section, not the Profile section.

## Visual Guide

When you click "Get Draft Recommendations", you should see:

1. **Above the table:**
   ```
   [Get Draft Recommendations] button
   Current Pick: X
   Round: Y, Pick: Z
   ```

2. **The Table:**
   ```
   ┌──────┬─────────────┬──────┬──────────┬──────────┬──────────────┬────────┐
   │ Rank │ Name        │ Team │ Position │ Pos Rank │ Proj. Points │ Action │
   ├──────┼─────────────┼──────┼──────────┼──────────┼──────────────┼────────┤
   │  1   │ Player Name │  TEAM│    QB    │    1     │    350.5     │ Draft  │
   └──────┴─────────────┴──────┴──────────┴──────────┴──────────────┴────────┘
   ```

3. **Below the table (Premium users):**
   ```
   ┌─────────────────────────────────────┐
   │ 🎯 Personalized Draft Strategy      │
   │ (if you have drafted players)       │
   │ Strategy text here...               │
   └─────────────────────────────────────┘

   ┌─────────────────────────────────────┐
   │ 🤖 AI Draft Analysis                │
   │ Analysis text here...               │
   └─────────────────────────────────────┘
   ```

