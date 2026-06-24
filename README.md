# OfflineGold

OfflineGold is a bulk lead scraping tool designed to find businesses on Google Maps that don't have a website. It analyzes these businesses and scores them based on their "closing chance" — a predictive rating of how likely they are to need digital services.

## Features

- **Google Maps Scraper**: Targeted scraping for any niche and location.
- **Website Detection**: Filters out businesses that already have a web presence.
- **Lead Scoring**: Predicts closing chance based on rating, review count, and other factors.
- **Dashboard**: Clean UI for searching and exporting leads.

## Project Structure

- `backend/`: FastAPI server and Playwright scraper.
- `frontend/`: Vite + React dashboard.

## Setup

### Backend

1. Install dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
2. Initialize Playwright:
   ```bash
   playwright install chromium
   ```
3. Run the API:
   ```bash
   python main.py
   ```

### Frontend

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```
2. Run the development server:
   ```bash
   npm run dev
   ```

## License

MIT
