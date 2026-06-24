import asyncio
from playwright.async_api import async_playwright
import os
import json

class GoogleMapsScraper:
    def __init__(self, browsers_path=None):
        if browsers_path:
            os.environ["PLAYWRIGHT_BROWSERS_PATH"] = browsers_path
        else:
            # Default to the one I just set up if not provided
            os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "/home/team/shared/offlinegold/backend/pw-browsers"

    async def scrape(self, query, max_results=10):
        results = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Navigate to Google Maps
            search_url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"
            await page.goto(search_url)
            
            # Wait for the results to load
            try:
                await page.wait_for_selector('div[role="feed"]', timeout=10000)
            except:
                # If feed not found, maybe there's only one result or a different layout
                pass

            # Scroll to load more results
            feed_selector = 'div[role="feed"]'
            if await page.query_selector(feed_selector):
                for _ in range(3): # Scroll a few times
                    await page.evaluate(f"document.querySelector('{feed_selector}').scrollTop += 1000")
                    await asyncio.sleep(2)
            
            # Extract basic info from the list
            items = await page.query_selector_all('div[role="article"]')
            for item in items[:max_results]:
                try:
                    # Get the link to the place
                    link_element = await item.query_selector('a')
                    if not link_element:
                        continue
                    
                    name = await item.get_attribute('aria-label') or "Unknown"
                    
                    # Click to get details (optional, but let's try to extract from the item first)
                    # For now, let's just get what's visible in the list
                    
                    # Rating and reviews
                    rating_elem = await item.query_selector('span[role="img"]')
                    rating_text = await rating_elem.get_attribute('aria-label') if rating_elem else ""
                    
                    rating = None
                    reviews = 0
                    if rating_text:
                        import re
                        # Example: "4.7 stars 1,564 Reviews" or "4.7 stars (1,564)"
                        match = re.search(r"(\d+\.\d+)", rating_text)
                        if match:
                            rating = float(match.group(1))
                        
                        # Match "1,564 Reviews" or "(1,564)" or "1,564"
                        match_reviews = re.search(r"([\d,]+)\s+Reviews", rating_text)
                        if match_reviews:
                            reviews = int(match_reviews.group(1).replace(',', ''))
                        else:
                            # Try matching reviews in parentheses like "4.7(1,564)"
                            # The aria-label for stars often looks like "4.7 stars 1,564 reviews"
                            # but sometimes the text on the page is different.
                            # Let's try to find digits that are not the rating.
                            matches = re.findall(r"([\d,]+)", rating_text)
                            for m in matches:
                                val = m.replace(',', '')
                                if val != str(rating) and val != "":
                                    try:
                                        reviews = int(val)
                                        break
                                    except:
                                        pass

                    # Category, Address, Phone heuristic parsing
                    text_content = await item.inner_text()
                    lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                    
                    category = "Unknown"
                    address = "Unknown"
                    phone = "Unknown"
                    
                    # More robust parsing based on observed "double space" and line structure
                    for line in lines[1:]:
                        if "  " in line: # Observed double space between Category and Address
                            parts = [p.strip() for p in line.split("  ")]
                            if category == "Unknown":
                                category = parts[0]
                                if len(parts) > 1:
                                    address = parts[1]
                        elif " \u00b7 " in line:
                            parts = [p.strip() for p in line.split(" \u00b7 ")]
                            # If it has "Open", "Closed", "Hours", it's the hours line
                            if any(word in parts[0] for word in ["Open", "Closed", "Hours", "Permanently"]):
                                for p in parts:
                                    if any(char.isdigit() for char in p) and len(p) > 7:
                                        phone = p
                            else:
                                if category == "Unknown":
                                    category = parts[0]
                                    if len(parts) > 1:
                                        address = parts[1]
                        elif "(" in line and ")" in line and any(char.isdigit() for char in line):
                            phone = line
                        elif category == "Unknown" and not any(char.isdigit() for char in line) and len(line) < 40:
                            category = line

                    # Clean up address if it contains phone or hours
                    if address != "Unknown":
                        if "(" in address and ")" in address:
                            address = "Unknown" # Likely misparsed phone
                        elif any(word in address for word in ["Open", "Closed", "Hours"]):
                            address = "Unknown"

                    # Website
                    website_elem = await item.query_selector('a[data-value="Website"]')
                    website = await website_elem.get_attribute('href') if website_elem else None
                    
                    results.append({
                        "name": name,
                        "rating": rating,
                        "reviews": reviews,
                        "category": category,
                        "address": address,
                        "phone": phone,
                        "website": website
                    })
                except Exception as e:
                    print(f"Error extracting item: {e}")
                    
            await browser.close()
        return results

async def main():
    scraper = GoogleMapsScraper()
    leads = await scraper.scrape("plumbers in Austin", max_results=5)
    print(json.dumps(leads, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
