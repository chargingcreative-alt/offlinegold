from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel
import uuid
import csv
from io import StringIO
from fastapi.responses import StreamingResponse

from scraper import GoogleMapsScraper
from scoring import calculate_closing_chance
from database import init_db, save_lead, get_leads, get_unique_niches

app = FastAPI(title="OfflineGold API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DB on startup
@app.on_event("startup")
async def startup_event():
    init_db()

class ScrapeRequest(BaseModel):
    query: str
    max_results: Optional[int] = 10

class Lead(BaseModel):
    id: str
    name: str
    rating: Optional[float] = None
    reviews: int = 0
    category: str = "Unknown"
    address: str = "Unknown"
    phone: str = "Unknown"
    website: Optional[str] = None
    closing_chance: int = 0
    query: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "OfflineGold API is running"}

@app.post("/api/scrape", response_model=List[Lead])
async def scrape_endpoint(req: ScrapeRequest):
    scraper = GoogleMapsScraper()
    results = await scraper.scrape(req.query, max_results=req.max_results)
    
    leads = []
    for res in results:
        lead_id = str(uuid.uuid4())
        closing_chance = calculate_closing_chance(res)
        
        lead_data = {
            "id": lead_id,
            "name": res['name'],
            "rating": res['rating'],
            "reviews": res['reviews'],
            "category": res['category'],
            "address": res['address'],
            "phone": res['phone'],
            "website": res['website'],
            "closing_chance": closing_chance
        }
        
        save_lead(lead_data, req.query)
        leads.append(Lead(**lead_data, query=req.query))
        
    return leads

@app.get("/api/leads", response_model=List[Lead])
async def get_leads_endpoint(
    no_website: bool = False, 
    min_score: int = 0, 
    niche: Optional[str] = None
):
    leads = get_leads(no_website=no_website, min_score=min_score, niche=niche)
    return [Lead(**l) for l in leads]

@app.get("/api/niches")
async def get_niches_endpoint():
    return get_unique_niches()

@app.get("/api/leads/export")
async def export_leads():
    leads = get_leads()
    if not leads:
        raise HTTPException(status_code=404, detail="No leads found to export")
    
    si = StringIO()
    cw = csv.DictWriter(si, fieldnames=leads[0].keys())
    cw.writeheader()
    cw.writerows(leads)
    
    output = si.getvalue()
    
    return StreamingResponse(
        iter([output]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=leads.csv"}
    )

if __name__ == "__main__":
    import uvicorn
    # Use port 8000 for backend (proxied by frontend on 3000)
    uvicorn.run(app, host="0.0.0.0", port=8000)
