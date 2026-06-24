import subprocess
import json

def init_db():
    cmd = '''team-db "CREATE TABLE IF NOT EXISTS leads (
        id TEXT PRIMARY KEY, 
        query TEXT, 
        name TEXT, 
        rating REAL, 
        reviews INTEGER, 
        category TEXT, 
        address TEXT, 
        phone TEXT, 
        website TEXT, 
        closing_chance INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )"'''
    subprocess.run(cmd, shell=True)

def save_lead(lead_data, query):
    id = lead_data['id']
    name = lead_data['name'].replace("'", "''")
    rating = lead_data['rating'] if lead_data['rating'] is not None else "NULL"
    reviews = lead_data['reviews']
    category = lead_data['category'].replace("'", "''")
    address = lead_data['address'].replace("'", "''")
    phone = lead_data['phone'].replace("'", "''")
    website = f"'{lead_data['website']}'" if lead_data['website'] else "NULL"
    closing_chance = lead_data['closing_chance']
    
    cmd = f'''team-db "INSERT OR REPLACE INTO leads (id, query, name, rating, reviews, category, address, phone, website, closing_chance) 
              VALUES ('{id}', '{query}', '{name}', {rating}, {reviews}, '{category}', '{address}', '{phone}', {website}, {closing_chance})"'''
    subprocess.run(cmd, shell=True)

def get_leads(no_website=False, min_score=0, niche=None):
    sql = "SELECT * FROM leads WHERE closing_chance >= " + str(min_score)
    if no_website:
        sql += " AND website IS NULL"
    if niche:
        sql += f" AND query LIKE '%{niche}%'"
    sql += " ORDER BY closing_chance DESC"
    
    cmd = f'team-db "{sql}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    try:
        return json.loads(result.stdout)
    except:
        return []

def get_unique_niches():
    cmd = 'team-db "SELECT DISTINCT query FROM leads"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    try:
        data = json.loads(result.stdout)
        return [row['query'] for row in data]
    except:
        return []
