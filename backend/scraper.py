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
            # Use a real user agent to avoid "limited view"
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            
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
                    full_text = await item.inner_text()
                    rating = None
                    reviews = 0
                    
                    # Try to find pattern like "4.7(1,564)" or "4.7 (1.5k)"
                    import re
                    # Updated regex to be more flexible
                    match = re.search(r"(\d+\.\d+)\s*stars?\s*\(?([\d,.]+[Kk]?)\)?", full_text, re.IGNORECASE)
                    if not match:
                        # Try pattern like "4.7 (1.5k) Reviews"
                        match = re.search(r"(\d+\.\d+)\s+([\d,.]+[Kk]?)\s+Reviews", full_text, re.IGNORECASE)
                    if not match:
                        # Try just the parentheses next to the rating
                        match = re.search(r"(\d+\.\d+)\s*\(([\d,.]+[Kk]?)\)", full_text)
                    
                    if match:
                        rating = float(match.group(1))
                        reviews_str = match.group(2).lower()
                        try:
                            if 'k' in reviews_str:
                                reviews = int(float(reviews_str.replace('k', '').replace(',', '')) * 1000)
                            else:
                                reviews = int(reviews_str.replace(',', '').replace('.', ''))
                        except:
                            pass
                    else:
                        # Fallback to the star element aria-label which sometimes has full text
                        rating_elem = await item.query_selector('span[role="img"]')
                        if rating_elem:
                            rating_text = await rating_elem.get_attribute('aria-label') or ""
                            # Pattern: "4.7 stars 1,564 Reviews" or "4.7 stars (1,564)"
                            r_match = re.search(r"(\d+\.\d+)\s*stars?\s*\(?([\d,.]+[Kk]?)\)?", rating_text, re.IGNORECASE)
                            if r_match:
                                rating = float(r_match.group(1))
                                reviews_str = r_match.group(2).lower()
                                try:
                                    if 'k' in reviews_str:
                                        reviews = int(float(reviews_str.replace('k', '').replace(',', '')) * 1000)
                                    else:
                                        reviews = int(reviews_str.replace(',', '').replace('.', ''))
                                except:
                                    pass
                            elif not rating:
                                r_match = re.search(r"(\d+\.\d+)", rating_text)
                                if r_match:
                                    rating = float(r_match.group(1))

                    # Category, Address, Phone heuristic parsing
                    text_content = await item.inner_text()
                    lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                    
                    category = "Unknown"
                    address = "Unknown"
                    phone = "Unknown"
                    
                    # Phone regex pattern (US centric but common)
                    phone_pattern = r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
                    
                    for line in lines[1:]:
                        # Check for phone first in the line
                        phone_match = re.search(phone_pattern, line)
                        if phone_match and phone == "Unknown":
                            phone = phone_match.group()
                        
                        if "  " in line: # Observed double space between Category and Address
                            parts = [p.strip() for p in line.split("  ")]
                            if category == "Unknown":
                                category = parts[0]
                                if len(parts) > 1:
                                    address = parts[1]
                        elif " \u00b7 " in line:
                            parts = [p.strip() for p in line.split(" \u00b7 ")]
                            # If it has hours-related words, try to extract phone from it
                            if any(word in parts[0] for word in ["Open", "Closed", "Hours", "Permanently"]):
                                for p in parts:
                                    p_match = re.search(phone_pattern, p)
                                    if p_match:
                                        phone = p_match.group()
                            else:
                                if category == "Unknown":
                                    category = parts[0]
                                    if len(parts) > 1:
                                        address = parts[1]
                        elif "(" in line and ")" in line and any(char.isdigit() for char in line):
                            # Likely a phone line if it matches the pattern
                            p_match = re.search(phone_pattern, line)
                            if p_match:
                                phone = p_match.group()
                        elif category == "Unknown" and not any(char.isdigit() for char in line) and len(line) < 40:
                            category = line

                    # Final cleanup for address - if it's the same as phone, or contains hours
                    if address != "Unknown":
                        if address == phone:
                            address = "Unknown"
                        elif any(word in address for word in ["Open", "Closed", "Hours"]):
                            address = "Unknown"

                    # Website detection improved
                    website = None
                    website_elem = await item.query_selector('a[data-value="Website"]')
                    if website_elem:
                        website = await website_elem.get_attribute('href')
                    
                    if not website:
                        # Fallback: look for any link that looks like a website link
                        links = await item.query_selector_all('a')
                        for link in links:
                            label = await link.get_attribute('aria-label') or ""
                            if "website" in label.lower():
                                website = await link.get_attribute('href')
                                break

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
