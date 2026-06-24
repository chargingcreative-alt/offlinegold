def calculate_closing_chance(lead_data):
    score = 0
    if not lead_data.get('website'):
        score += 40
    
    rating = lead_data.get('rating')
    if rating is not None:
        if rating < 3.0:
            score += 20
        elif rating < 4.0:
            score += 10
            
    reviews = lead_data.get('reviews', 0)
    if reviews == 0:
        score += 25 # No reviews at all (10 from lead + some extra for "few")
    elif reviews < 5:
        score += 15
    elif reviews < 50:
        score += 5
    
    # Lead's specific rules:
    # No website = +40
    # Low rating (< 3.0) = +20
    # Few reviews (< 5) = +15
    # No reviews at all = +10
    # Unknown business age = +5
    
    # My combined logic above covers it, but let's be more precise to lead's points:
    lead_score = 0
    if not lead_data.get('website'):
        lead_score += 40
    if rating is not None and rating < 3.0:
        lead_score += 20
    if reviews == 0:
        lead_score += 10
    elif reviews < 5:
        lead_score += 15
    # "Unknown business age" - we don't have this yet, so assume +5 for everyone or skip
    lead_score += 5 
    
    return min(lead_score, 100)
