# OfflineGold

Bulk lead scraping tool that extracts businesses from Google Maps across any niche, with a unique filter for businesses without a website. Each lead is analyzed and scored on "closing chance".

## Project Structure

- `backend/`: FastAPI server with scraping endpoints.
  - `scraper.py`: Playwright-based Google Maps scraper.
  - `scoring.py`: Algorithm to calculate lead closing chance.
  - `database.py`: Lead persistence and retrieval.
  - `main.py`: API endpoints.
- `frontend/`: Vite + React dashboard for users.

## Features

- **Google Maps Scraper**: Search by niche and location.
- **Website Filter**: Identify businesses that don't have an online presence.
- **Closing Chance Scoring**: Predictive rating of how likely a business is to need services.
- **CSV Export**: Export leads for outreach.

## Getting Started

### Backend

1. Navigate to `backend/`.
2. Install dependencies: `pip install -r requirements.txt`.
3. Set up Playwright: `playwright install chromium`.
4. Run the server: `python main.py`.

### Frontend

1. Navigate to `frontend/`.
2. Install dependencies: `npm install`.
3. Run the dev server: `npm run dev`.

## Environment Variables

- `PLAYWRIGHT_BROWSERS_PATH`: Path to Playwright browsers (pre-configured for sandbox).
